#level_loader.py
import json
import os


def load_level(level_path):

    if not os.path.exists(level_path):
        raise FileNotFoundError(f"file not found : {level_path}")

    with open(level_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    if "grid" in raw and isinstance(raw["grid"], list):
        return raw

    print(" Loading format... converting...")
    return convert_format(raw)


def convert_format(raw):

    rows = raw["rows"]
    cols = raw["cols"]

    grid = [["." for _ in range(cols)] for _ in range(rows)]

    for obj in raw["cells"]:
        r = obj["row"]
        c = obj["col"]
        t = obj["type"]

        if t == "agent":
            grid[r][c] = "P"

        elif t == "target":
            grid[r][c] = "F"

        elif t == "number":
            grid[r][c] = str(obj["number"])

        elif t == "operation":
            grid[r][c] = obj["operation"]

        elif t == "door":
            value = obj["value"]
            grid[r][c] = "G" + str(value)

        elif t == "block":
            grid[r][c] = "#"

        else:
            raise ValueError(f"Unknown cell type : {t}")

    return {
        "rows": rows,
        "cols": cols,
        "grid": grid
    }
