
from fastapi import APIRouter, Request
from uuid import uuid4
import os, json, re

from models import Character, Stats
from engine import apply_effect, resolve_next, check_condition

# Save file validation

BASE_DIR = os.path.abspath("saves")

# Ensures save names are filesystem-safe and URL-safe
# Prevents injection, traversal, and overly large filenames
def sanitize_save_name(save_name: str) -> str:
    save_name = save_name.strip().lower()

    # allow only safe characters
    if not re.match(r"^[a-z0-9_-]+$", save_name):
        raise ValueError("Invalid save name")

    if len(save_name) > 32:
        raise ValueError("Save name too long")

    return save_name

# Prevent directory traversal attacks by ensuring save files
# always resolve inside BASE_DIR
def save_path(save_name: str):
    path = os.path.abspath(os.path.join(BASE_DIR, f"{save_name}.json"))

    if not os.path.commonpath([path, BASE_DIR]) == BASE_DIR:
        raise ValueError("Invalid path")
    return path

def get_session(session_id:str, sessions):
    state = sessions.get(session_id)
    if state is None:
        raise ValueError("Invalid session")
    return state

# API endpoints

router = APIRouter()

@router.post("/start")
def start_game(request: Request):
    session_id = str(uuid4())

    story = request.app.state.story

    state = Character(
        name="Player",
        rpgClass="Adventurer",
        stats=Stats(strength=3, dexterity=3, intelligence=3, faith=3),
        current_node="scholar:failed_scholar_start"
    )

    request.app.state.sessions[session_id] = state

    node = story[state.current_node]

    filtered_choices = [
        c for c in story[state.current_node].choices
        if check_condition(c.condition, state)
    ]

    return {
        "session_id": session_id,
        "node": {
            **node.model_dump(),
            "choices": [c.model_dump() for c in filtered_choices]
        },
        "state": state.model_dump()
    }

@router.post("/load/{save_name}")
def load_game(save_name: str, session_id: str, request: Request):
    save_name = sanitize_save_name(save_name)
    story = request.app.state.story
    path = save_path(save_name)

    with open(path) as f:
        data = json.load(f)

    state = Character(**data)

    request.app.state.sessions[session_id] = state

    node = story[state.current_node]

    return {
        "session_id": session_id,
        "node": node.model_dump(),
        "state": state.model_dump()
    }

@router.post("/save/{save_name}")
def save_game(save_name: str, session_id: str, request: Request):
    save_name = sanitize_save_name(save_name)

    state = get_session(session_id, request.app.state.sessions)
    
    os.makedirs("saves", exist_ok=True)
    path = save_path(save_name)

    with open(path, "w") as f:
        f.write(state.model_dump_json())

    return {"status": "saved", "file": path}

@router.delete("/save/{save_name}")
def delete_save(save_name: str):
    save_name = sanitize_save_name(save_name)
    path = save_path(save_name)

    if os.path.exists(path):
        os.remove(path)

    return {"status": "deleted"}

@router.post("/choose")
def choose(session_id: str, choice_index: int, request: Request):

    story = request.app.state.story
    state = get_session(session_id, request.app.state.sessions)

    node = story[state.current_node]
    if choice_index < 0 or choice_index >= len(node.choices):
        raise ValueError("Invalid choice index")
    choice = node.choices[choice_index]

    next_node = resolve_next(choice, state)
    state.current_node = next_node

    apply_effect(story[next_node].effects, state)

    # Filter out ineligible choices
    filtered_choices = [
        c for c in story[next_node].choices
        if check_condition(c.condition, state)
    ]

    # debug only: notify when a choice is filtered out
    for c in story[next_node].choices:
        if not check_condition(c.condition, state):
            print(f"Filtered out: {c.text}")

    is_end = len(filtered_choices) == 0

    return {
        "node": {
            **story[next_node].model_dump(),
            "choices": [c.model_dump() for c in filtered_choices]
        },
        "state": state.model_dump(),
        "is_end": is_end
    }

@router.post("/autosave")
def autosave(session_id :str, request: Request):
    
    state = get_session(session_id, request.app.state.sessions)
    
    path = os.path.join(BASE_DIR, "autosave.json")
    with open(path, "w") as f:
        f.write(state.model_dump_json())

    return{"status": "autosaved"}


@router.post("/close-session")
def close_session(session_id: str, request: Request):
    sessions = request.app.state.sessions

    state = sessions.pop(session_id, None)

    if not state:
        return {"status": "session_not_found"}

    return {"status": "closed"}