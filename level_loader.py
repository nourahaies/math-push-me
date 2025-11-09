import json
import os

def load_level(level_path):
    """
    load a level from a file and get it's data as a JSON array.
    """
    if not os.path.exists(level_path):
        raise FileNotFoundError(f"file not found : {level_path}")
    
    with open(level_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # التحقق من أن المفاتيح الأساسية موجودة
    required_keys = ["rows", "cols", "grid"]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"file  {level_path}    doesn't have the key '{key}'")

    return data
