import re

def remove_special_character(string: str) -> str:
    return re.sub(r'[^a-zA-Z0-9\s]', '', string)

def get_time_start_end_from_path(path: str) -> list[str]:
    return path.replace("(", "").replace(")", "").split(",")