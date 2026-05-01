
def parse_item_key_pair(pair:str):
    parts = pair.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid item pair format: '{pair}'")
    
    item_type, key = parts
    return {
        "type": item_type.strip(),
        "key": key.strip()
    }

def parse_skill_check(pair:str):
    parts = pair.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid skill check pair format: '{pair}'")
    
    stat, value = parts
    return {
        "stat": stat.strip(),
        "difficulty": int(value.strip())
    }

def parse_numeric_pair(pair:str):
    parts = pair.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid numeric pair format: '{pair}'")
    
    key, delta = parts
    return {
        "key": key.strip(),
        "delta": int(delta.strip())
    }

