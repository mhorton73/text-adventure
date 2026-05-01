
# Expected structure:

# node_id
# 
# ## Text
# text line 1
# text line 2
# ...
# text line last
# 
# ## Effects
# add: flag:a
# add: item:b
# remove: flag:c
# remove: item:d
# numchange: gold:10
# numchange: hp:-6
# numchange: strength:2
# 
# ## Choices
#
# list of choices (explained in choice_parser.py)

from parser.primitives import parse_item_key_pair, parse_numeric_pair
from parser.choice_parser import parse_choices

def parse_effects(lines: list[str]) -> dict:
    add = []
    remove = []
    numeric_changes = []

    for line in lines:
        line = line.removeprefix("- ").strip()

        # add_flag / add_item
        if line.startswith("add:"):
            pair = line.removeprefix("add:").strip()
            add.append(parse_item_key_pair(pair))

        # remove
        elif line.startswith("remove:"):
            pair = line.removeprefix("remove:").strip()
            remove.append(parse_item_key_pair(pair))

        # numchange
        elif line.startswith("numchange:"):
            pair = line.removeprefix("numchange:").strip()
            numeric_changes.append(parse_numeric_pair(pair))


    return {
        "add": add,
        "remove": remove,
        "numeric_changes": numeric_changes
    }


def parse_markdown_node(content: str) -> dict:
    
    lines = [l.rstrip() for l in content.split("\n")]

    # Split into sections
    node_id = None
    text_lines = []
    effect_lines = []
    choice_lines = []

    mode = None

    for line in lines:
        stripped = line.strip()

        # preserve blank lines for text, but ditch them for other sections
        if not stripped:
            if mode == "text":
                text_lines.append("")
            continue
        if stripped.startswith("id:"):
            if node_id is not None:
                raise ValueError("Duplicate id in node")
            node_id = stripped.removeprefix("id:").strip()
            continue
        if stripped.startswith("## Text"):
            mode = "text"
            continue
        if stripped.startswith("## Effects"):
            mode = "effects"
            continue
        if stripped.startswith("## Choices"):
            mode = "choices"
            continue

        # some basic validation
        if mode == "effects" and not stripped.startswith((
            "add:", "remove:", "numchange:"
        )):
            raise ValueError(f"Invalid effects line: {line}")
        if mode == "choices" and not stripped.startswith(
            ("- ", "requires:", "excludes:", "numcon:", "skill:", "->")
        ):
            raise ValueError(f"Invalid choices line: {line}")

        if mode == "text":
            text_lines.append(line)
        elif mode == "effects":
            effect_lines.append(stripped)
        elif mode == "choices":
            choice_lines.append(stripped)

    if node_id is None:
        raise ValueError("Missing id")

    if not text_lines:
        raise ValueError("Missing text")
    
    # Parse sections

    text = "\n".join(text_lines)
    effects = parse_effects(effect_lines)    
    choices = parse_choices(choice_lines)

    return {
        "id": node_id,
        "text": text,
        "choices": choices,
        "effects": effects
    }

