from copy import deepcopy
from state import GameState
from successor import get_successors


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def heuristic(grid, player_pos, locks, goal_pos):
    """
    Heuristic محسّن لـ Hill Climbing:
    - عقوبة معتدلة على الأقفال
    - جذب للأرقام والعمليات
    - جذب ناعم للهدف حتى لو القفل موجود
    """

    # 1️⃣ عقوبة الأقفال (خففناها)
    lock_penalty = 200 * len(locks)

    # 2️⃣ أقرب رقم أو عملية
    targets = []

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            cell = grid[r][c]
            if cell is None:
                continue
            if cell.isdigit() or cell in ["+", "-"]:
                targets.append((r, c))

    interest_dist = float("inf")
    for t in targets:
        interest_dist = min(interest_dist, manhattan(player_pos, t))

    if interest_dist == float("inf"):
        interest_dist = 0

    # 3️⃣ جذب ناعم للهدف (حتى لو القفل موجود)
    goal_dist = manhattan(player_pos, goal_pos)
    goal_pull = 0.5 * goal_dist

    #return lock_penalty + interest_dist + goal_pull
    return lock_penalty + goal_pull


def hill_climbing_solve(game, max_steps=500):
    """
    Deterministic Hill Climbing (Best Neighbor)
    """

    current_state = deepcopy(game.state)
    current_results = deepcopy(game.results)
    path = []

    current_h = heuristic(
        current_state.grid,
        current_state.player_pos,
        current_state.locks,
        current_state.goal_pos
    )

    # --- [PRINT - MONITOR] ---
    print("\n=== HILL CLIMBING START ===")
    print(f"Start pos={current_state.player_pos}  Locks={list(current_state.locks.keys())}")
    print(f"Initial heuristic = {current_h}")
    # -------------------------

    for step in range(max_steps):

        # --- [PRINT - MONITOR] ---
        print(f"\n--- Step {step} ---")
        print(f"Current pos={current_state.player_pos}  h={current_h}")
        # -------------------------

        # 🎯 Goal check
        if current_state.player_pos == current_state.goal_pos and not current_state.locks:
            goal_snapshot = {
                "grid": deepcopy(current_state.grid),
                "player_pos": current_state.player_pos,
                "locks": deepcopy(current_state.locks),
                "results": list(current_results)
            }

            # --- [PRINT - MONITOR] ---
            print("✔ GOAL FOUND using Hill Climbing")
            print("Path:", path)
            # -------------------------

            return goal_snapshot, len(path), path

        # Generate successors
        class MiniGame:
            def __init__(self, s, r):
                self.state = s
                self.results = r

        mg = MiniGame(deepcopy(current_state), deepcopy(current_results))
        successors = get_successors(mg)

        best_succ = None
        best_h = current_h

        for s in successors:
            h = heuristic(
                s["grid"],
                s["player_pos"],
                s["locks"],
                current_state.goal_pos
            )

            # --- [PRINT - MONITOR] ---
            print(f" Action {s['action']} → pos={s['player_pos']} h={h}")
            # -------------------------

            if h < best_h:
                best_h = h
                best_succ = s

        # ❌ No improvement → local optimum
        if best_succ is None:
            # --- [PRINT - MONITOR] ---
            print("✖ Stuck at local optimum. No better neighbor.")
            # -------------------------
            return None, len(path), None

        # Move to best neighbor
        path.append(best_succ["action"])

        level_data = {
            "rows": len(best_succ["grid"]),
            "cols": len(best_succ["grid"][0]),
            "grid": deepcopy(best_succ["grid"])
        }

        new_state = GameState(level_data)
        new_state.player_pos = best_succ["player_pos"]
        new_state.locks = deepcopy(best_succ["locks"])
        new_state.goal_pos = current_state.goal_pos

        current_state = new_state
        current_results = deepcopy(best_succ["results"])
        current_h = best_h

    # --- [PRINT - MONITOR] ---
    print("✖ Step limit reached. Hill Climbing stopped.")
    # -------------------------

    return None, len(path), None
