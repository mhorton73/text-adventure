
import operator

from schemas import(
    Choice, 
    Condition, 
    Effect, 
    StoryItem, 
    SkillCheck, 
    Stat, 
    ComparisonOp,
    NumericCondition
)
from models import Character


OPERATOR_MAP = {
    ComparisonOp.lt: operator.lt,
    ComparisonOp.lte: operator.le,
    ComparisonOp.eq: operator.eq,
    ComparisonOp.gte: operator.ge,
    ComparisonOp.gt: operator.gt,
}

DEFAULT_TRACKER_VALUES = {
    "sanity": 100
}

def get_collections(state: Character):
    return {
        "item": state.inventory,
        "flag": state.flags,
        "spell": state.spells,
    }

def get_value(state: Character, key: str) -> int:
    if key in Stat._value2member_map_:
        return getattr(state.stats, key)
    elif key == "gold":
        return state.gold
    elif key == "hp":
        return state.hp
    elif key in state.trackers:
        return state.trackers.get(key)
    else: return None
    
def set_value(state: Character, key: str, value: int):

    # _value2member_map_ = Internal python lookup table
    if key in Stat._value2member_map_:
        max_val = getattr(state.max_stats, key)
        setattr(state.stats, key, max(0, min(value, max_val)))
    elif key == "gold":
        state.gold = max(0, value)
    elif key == "hp":
        state.hp = max(0, min(value, state.max_hp))
    else:
        state.resources[key] = max(0, value)

def check_numeric_condition(cond: NumericCondition, state: Character):
    current = get_value(state, cond.key)
    if current == None:
        return False
    
    op_func = OPERATOR_MAP[cond.op]
    return op_func(current, cond.value)

# --------- CONDITION CHECK ---------
def check_condition(condition: Condition, state: Character):
    
    collections = get_collections(state)

    def check_item(item: StoryItem):
        collection = collections.get(item.type)
        if collection is None:
            raise ValueError(f"Unknown StoryItem type: {item.type}")
        return item.key in collection

    # required
    for item in condition.required:
        if not check_item(item):
            return False

    # excluded
    for item in condition.excluded:
        if check_item(item):
            return False
        
    for item in condition.numeric:
        if not check_numeric_condition(item, state):
            return False

    return True


# --------- APPLY EFFECT ---------
def apply_effect(effect: Effect, state: Character):
    
    collections = get_collections(state)
    for item in effect.add:
        collection = collections.get(item.type)
        if collection is None:
            raise ValueError(f"Unknown StoryItem type: {item.type}")
        collection.append(item.key)

    for item in effect.remove:
        collection = collections.get(item.type)
        if collection is None:
            raise ValueError(f"Unknown StoryItem type: {item.type}")
        if item.key in collection:
            collection.remove(item.key)

    for item in effect.numeric_changes:
        current_value = get_value(state, item.key)
        if current_value is None:
            current_value = DEFAULT_TRACKER_VALUES.get(item.key, 0)

        new_value = max(0, current_value + item.delta)
        set_value(state, item.key, new_value)



# Skill Check

def resolve_skill_check(skill_check: SkillCheck, state: Character):
    stat_value = getattr(state.stats, skill_check.stat.value)
    return stat_value >= skill_check.difficulty

# --------- RESOLVE NEXT NODE ---------
def resolve_next(choice: Choice, state: Character):
    if choice.skill_check:
        if resolve_skill_check(choice.skill_check, state): 
            return choice.success_node 
        else:
            return choice.failure_node

    return choice.next_node

