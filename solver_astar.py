# solver_astar.py
from copy import deepcopy
import heapq
from state import GameState
from successor import get_successors

# ---------- إعدادات البحث ----------
LOCK_PENALTY = 20       # الوزن المعطى لوجود كل قفل (يمكن التعديل)
PRINT_EVERY = 1000      # كل كم عقدة نطبع حالة للتتبع (0 = لا طباعة دورية)

# ------------------------------
def _state_signature(grid, player_pos, locks, results):
    """
    تُستخدَم لتوليد توقيع (hashable) للحالة لتجنّب الزيارات المكررة.
    نستخدم grid (frozen), player_pos, locks (sorted), results (sorted).
    """
    frozen_grid = tuple(tuple(row) for row in grid)
    frozen_locks = tuple(sorted(((k, v[0], v[1]) for k, v in locks.items())))
    frozen_results = tuple(sorted(results))
    return (player_pos, frozen_grid, frozen_locks, frozen_results)

def _reconstruct_path(came_from, end_key):
    """
    تعيد تسلسل الأفعال من البداية إلى النهاية.
    came_from maps: key -> (parent_key, action)
    end_key هو التوقيع النهائي الذي نصل إليه.
    """
    path = []
    cur = end_key
    while cur in came_from and came_from[cur][0] is not None:
        parent, action = came_from[cur]
        path.append(action)
        cur = parent
    path.reverse()
    return path

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def heuristic(player_pos, goal_pos, locks_left):
    """
    heuristic = Manhattan distance + LOCK_PENALTY * number_of_locks
    """
    if goal_pos is None:
        return 0
    return manhattan(player_pos, goal_pos) + len(locks_left) * LOCK_PENALTY

# ------------------------------
def astar_solve(game, max_nodes=1000000):
    """
    A* search from current game.state and game.results.
    Returns (goal_snapshot, generated_nodes_count, path_actions) or (None, generated_count, None)
    """

    # root (start) state
    start_state = deepcopy(game.state)
    start_results = deepcopy(game.results)

    start_sig = _state_signature(start_state.grid, start_state.player_pos, start_state.locks, start_results)
    goal_pos = start_state.goal_pos

    # open set: heap of (f, g, counter, signature, node_data)
    # node_data = { "grid":..., "player_pos":..., "locks":..., "results":..., "action_from_parent":..., "parent_sig":... }
    open_heap = []
    counter = 0  # tie-breaker for heap

    g_score = { start_sig: 0 }
    f_score = { start_sig: heuristic(start_state.player_pos, goal_pos, start_state.locks) }

    start_node = {
        "grid": deepcopy(start_state.grid),
        "player_pos": start_state.player_pos,
        "locks": deepcopy(start_state.locks),
        "results": list(start_results),
        "action_from_parent": None,
        "parent_sig": None
    }

    heapq.heappush(open_heap, (f_score[start_sig], g_score[start_sig], counter, start_sig, start_node))
    counter += 1

    came_from = {}  # signature -> (parent_signature, action_str)
    came_from[start_sig] = (None, None)

    closed = set()

    generated = 1
    expansions = 0

    print(f"\n=== A* START (max_nodes={max_nodes}) ===")
    print(f"Start pos={start_state.player_pos}  Locks={list(start_state.locks.keys())}\n")

    while open_heap:
        f, g, _, cur_sig, cur_node = heapq.heappop(open_heap)

        # if already processed in closed (we may have old entries in heap)
        if cur_sig in closed:
            continue

        expansions += 1
        if PRINT_EVERY and expansions % PRINT_EVERY == 0:
            print(f"--- Expanded {expansions} nodes (generated {generated}) ---")
            print(f" Current node player={cur_node['player_pos']}  locks_left={len(cur_node['locks'])}")
            print("-----------------------------------------------------")

        # Goal check: player on goal_pos and no locks remain
        if cur_node["player_pos"] == goal_pos and not cur_node["locks"]:
            # reconstruct path
            path = _reconstruct_path(came_from, cur_sig)
            goal_snapshot = {
                "grid": deepcopy(cur_node["grid"]),
                "player_pos": cur_node["player_pos"],
                "locks": deepcopy(cur_node["locks"]),
                "results": list(cur_node["results"])
            }
            print("\n✔ GOAL FOUND!")
            print(f"Generated nodes: {generated}")
            print(f"Expanded nodes: {expansions}")
            print(f"Path length: {len(path)}")
            return goal_snapshot, generated, path

        # mark closed
        closed.add(cur_sig)

        # create a mini-game object for successors
        class _MiniGame:
            def __init__(self, grid, player_pos, locks, results):
                # build a GameState-like structure for successor.get_successors usage
                level_data = {
                    "rows": len(grid),
                    "cols": len(grid[0]) if grid else 0,
                    "grid": deepcopy(grid)
                }
                self.state = GameState(level_data)
                # override properties to reflect snapshot exactly
                self.state.grid = deepcopy(grid)
                self.state.player_pos = player_pos
                self.state.locks = deepcopy(locks)
                self.state.find_positions()  # ensure goal_pos is set (from grid)
                self.results = list(results)

        mg = _MiniGame(cur_node["grid"], cur_node["player_pos"], cur_node["locks"], cur_node["results"])
        succs = get_successors(mg)

        # process successors
        for s in succs:
            grid_s = s["grid"]
            pos_s = s["player_pos"]
            locks_s = s["locks"]
            results_s = s["results"]
            action_s = s["action"]

            sig_s = _state_signature(grid_s, pos_s, locks_s, results_s)

            if sig_s in closed:
                continue

            tentative_g = g + 1  # each move cost = 1 (can be adjusted)

            prev_g = g_score.get(sig_s, None)
            if prev_g is None or tentative_g < prev_g:
                # better path found to sig_s
                g_score[sig_s] = tentative_g
                h = heuristic(pos_s, goal_pos, locks_s)
                f_s = tentative_g + h

                node_s = {
                    "grid": deepcopy(grid_s),
                    "player_pos": pos_s,
                    "locks": deepcopy(locks_s),
                    "results": list(results_s),
                    "action_from_parent": action_s,
                    "parent_sig": cur_sig
                }

                came_from[sig_s] = (cur_sig, action_s)

                heapq.heappush(open_heap, (f_s, tentative_g, counter, sig_s, node_s))
                counter += 1
                generated += 1

                # safety stop
                if max_nodes and generated >= max_nodes:
                    print("\n✖ Node limit reached! No solution found within node limit.")
                    return None, generated, None

    # no solution found
    print("\n✖ A* exhausted open set. No solution found.")
    print(f"Generated nodes: {generated}  Expanded: {expansions}")
    return None, generated, None
