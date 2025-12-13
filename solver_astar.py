# solver_astar.py
from copy import deepcopy
from state import GameState
from successor import get_successors
import heapq
import time

def _state_signature(grid, player_pos, locks, results):
    """Create a compact hashable signature for a state."""
    frozen_grid = tuple(tuple(row) for row in grid)
    frozen_locks = tuple(sorted(((k, v[0], v[1]) for k, v in locks.items())))
    frozen_results = tuple(sorted(results))
    return (player_pos, frozen_grid, frozen_locks, frozen_results)

def _reconstruct_path(nodes, goal_index):
    """Reconstruct the actions path from root to goal."""
    path = []
    idx = goal_index
    while idx is not None:
        node = nodes[idx]
        act = node["action_from_parent"]
        if act is not None:
            path.append(act)
        idx = node["parent"]
    path.reverse()
    return path

def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def _collect_interest_positions(grid):
    """
    جمع مواقع الأرقام والعمليات والأقفال والهدف
    يساعدنا لبناء heuristic سريع.
    """
    nums_ops = []
    locks = []
    goal = None
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    for r in range(rows):
        for c in range(cols):
            cell = grid[r][c]
            if cell is None:
                continue
            if cell.isdigit() or cell in ["+", "-"]:
                nums_ops.append((r, c))
            if isinstance(cell, str) and cell.startswith("G"):
                locks.append((r, c))
            if cell == "F":
                goal = (r, c)
    return nums_ops, locks, goal

def heuristic_estimate(grid, player_pos, locks_map):
    # إذا في أقفال باقيين → أعطي عقوبة ضخمة
    lock_penalty = 1000 * len(locks_map)

    # أقرب هدف فرعي (رقم / عملية / قفل)
    nums_ops, locks_positions, goal_pos = _collect_interest_positions(grid)
    best = float('inf')

    for p in nums_ops:
        best = min(best, _manhattan(player_pos, p))
    for p in locks_positions:
        best = min(best, _manhattan(player_pos, p))

    if not locks_map and goal_pos:
        best = _manhattan(player_pos, goal_pos)

    return lock_penalty + (best if best < float('inf') else 0)


def astar_solve(game, max_nodes=1000000, progress_interval=50000):
    """
    A* solver.
    Returns (goal_snapshot, generated_nodes_count, path_actions) or (None, gen_count, None)
    """
    start_time = time.time()

    root_state = deepcopy(game.state)
    root_results = deepcopy(game.results)

    # nodes array holds node dicts so we can reconstruct path
    nodes = []
    root_node = {
        "state": root_state,
        "results": root_results,
        "action_from_parent": None,
        "parent": None,
        "g": 0
    }
    nodes.append(root_node)

    # priority queue holds (f, node_index)
    pq = []
    start_h = heuristic_estimate(root_state.grid, root_state.player_pos, root_state.locks)
    heapq.heappush(pq, (start_h, 0))

    # visited map: signature -> best g found
    visited = {}
    sig_root = _state_signature(root_state.grid, root_state.player_pos, root_state.locks, root_results)
    visited[sig_root] = 0

    generated = 1
    expanded = 0

    print(f"\n=== A* START (limit={max_nodes}) ===")
    print(f"Root pos={root_state.player_pos}  Locks={list(root_state.locks.keys())}\n")
    last_report = 0

    while pq:
        f, idx = heapq.heappop(pq)
        node = nodes[idx]
        g = node["g"]
        # skip if this node is outdated (we might have inserted a better g for same signature)
        cur_sig = _state_signature(node["state"].grid, node["state"].player_pos, node["state"].locks, node["results"])
        if visited.get(cur_sig, float('inf')) < g:
            continue

        expanded += 1
        # progress printing
        if expanded - last_report >= progress_interval:
            elapsed = time.time() - start_time
            print(f"--- Expanded {expanded} nodes (generated {generated}) ---")
            print(f" Current node player={node['state'].player_pos}  locks_left={len(node['state'].locks)}  time={elapsed:.1f}s")
            print("-----------------------------------------------------")
            last_report = expanded

        # goal check
        st = node["state"]
        if st.player_pos == st.goal_pos and not st.locks:
            goal_snapshot = {
                "grid": deepcopy(st.grid),
                "player_pos": st.player_pos,
                "locks": deepcopy(st.locks),
                "results": list(node["results"])
            }
            path = _reconstruct_path(nodes, idx)
            print("\n✔ GOAL FOUND!")
            print(f"Generated nodes: {generated}")
            print(f"Expanded nodes: {expanded}")
            print(f"Path length: {len(path)}")
            return goal_snapshot, generated, path

        # generate successors using the helper (simulate on copies)
        class _MiniGame:
            def __init__(self, state, results):
                self.state = state
                self.results = results

        mg = _MiniGame(deepcopy(st), deepcopy(node["results"]))
        succs = get_successors(mg)

        for s in succs:
            grid_s = s["grid"]
            pos_s = s["player_pos"]
            locks_s = s["locks"]
            results_s = s["results"]
            action_s = s["action"]

            # compute g for successor (cost per move = 1)
            g_s = g + 1

            sig = _state_signature(grid_s, pos_s, locks_s, results_s)
            prev_g = visited.get(sig)
            if prev_g is not None and g_s >= prev_g:
                # we already have an equal or better path to this signature
                continue

            # quick direct-successor goal check (if move reaches goal and locks cleared)
            if (pos_s == st.goal_pos) and (not locks_s):
                goal_snapshot = {
                    "grid": deepcopy(grid_s),
                    "player_pos": pos_s,
                    "locks": deepcopy(locks_s),
                    "results": list(results_s)
                }
                # create temp node to reconstruct path
                temp = {
                    "state": None,
                    "results": deepcopy(results_s),
                    "action_from_parent": action_s,
                    "parent": idx,
                    "g": g_s
                }
                nodes.append(temp)
                goal_index = len(nodes) - 1
                path = _reconstruct_path(nodes, goal_index)
                print("\n✔ GOAL FOUND (direct successor)!----using A*")
                print(f"Generated nodes: {generated}")
                print(f"Expanded nodes: {expanded}")
                print(f"Path length: {len(path)}")
                return goal_snapshot, generated + 1, path

            # otherwise add new node
            level_data = {
                "rows": len(grid_s),
                "cols": len(grid_s[0]) if grid_s else 0,
                "grid": deepcopy(grid_s)
            }
            gs = GameState(level_data)
            gs.locks = deepcopy(locks_s)
            gs.player_pos = pos_s

            new_node = {
                "state": gs,
                "results": deepcopy(results_s),
                "action_from_parent": action_s,
                "parent": idx,
                "g": g_s
            }
            nodes.append(new_node)
            new_idx = len(nodes) - 1

            # heuristic
            h = heuristic_estimate(grid_s, pos_s, locks_s)
            f_new = g_s + h

            heapq.heappush(pq, (f_new, new_idx))
            visited[sig] = g_s
            generated += 1

            if max_nodes and generated >= max_nodes:
                print("\n✖ Node limit reached! No solution found.")
                return None, generated, None

    print("\n✖ A* ended. No solution found.")
    return None, generated, None
