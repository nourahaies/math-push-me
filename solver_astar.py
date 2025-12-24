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
    
    lock_penalty = 1000 * len(locks_map)

    nums_ops, locks_positions, goal_pos = _collect_interest_positions(grid)
    best = float('inf')

    for p in nums_ops:
        best = min(best, _manhattan(player_pos, p))

    if not locks_map and goal_pos:
        best = _manhattan(player_pos, goal_pos)

    return lock_penalty + (best if best < float('inf') else 0)


def astar_solve(game, max_nodes=1000000, progress_interval=50000):
    """
    A* solver.
    Returns (goal_snapshot, generated_nodes_count, path_actions)
    """
    start_time = time.time()

    root_state = deepcopy(game.state)
    root_results = deepcopy(game.results)

    nodes = []
    root_node = {
        "state": root_state,
        "results": root_results,
        "action_from_parent": None,
        "parent": None,
        "g": 0
    }
    nodes.append(root_node)

    pq = []
    start_h = heuristic_estimate(root_state.grid, root_state.player_pos, root_state.locks)
    heapq.heappush(pq, (start_h, 0))

    visited = {}
    sig_root = _state_signature(root_state.grid, root_state.player_pos, root_state.locks, root_results)
    visited[sig_root] = 0

    generated = 1
    expanded = 0

    # DEBUG PRINT (solver start)
    # print(f"\n=== A* START (limit={max_nodes}) ===")
    # print(f"Root pos={root_state.player_pos}  Locks={list(root_state.locks.keys())}\n")

    ###last_report = 0

    while pq:
        f, idx = heapq.heappop(pq)
        node = nodes[idx]
        g = node["g"]

        cur_sig = _state_signature(
            node["state"].grid,
            node["state"].player_pos,
            node["state"].locks,
            node["results"]
        )
        if visited.get(cur_sig, float('inf')) < g:
            continue

        expanded += 1

        # DEBUG PRINT (progress report)
        # if expanded - last_report >= progress_interval:
        #     elapsed = time.time() - start_time
        #     print(f"--- Expanded {expanded} nodes (generated {generated}) ---")
        #     print(
        #         f" Player={node['state'].player_pos} "
        #         f"Locks left={len(node['state'].locks)} "
        #         f"Time={elapsed:.1f}s"
        #     )
        #     print("-" * 55)
        #     last_report = expanded

        st = node["state"]

        # goal check
        if st.player_pos == st.goal_pos and not st.locks:
            goal_snapshot = {
                "grid": deepcopy(st.grid),
                "player_pos": st.player_pos,
                "locks": deepcopy(st.locks),
                "results": list(node["results"])
            }
            path = _reconstruct_path(nodes, idx)

            # DEBUG PRINT (goal found)
            # print("\n✔ GOAL FOUND (A*)")
            # print(f"Generated nodes: {generated}")
            # print(f"Expanded nodes: {expanded}")
            # print(f"Path length: {len(path)}")

            return goal_snapshot, generated, path

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

            g_s = g + 1
            sig = _state_signature(grid_s, pos_s, locks_s, results_s)

            prev_g = visited.get(sig)
            if prev_g is not None and g_s >= prev_g:
                continue

            # DEBUG PRINT (direct successor goal)
            # if pos_s == st.goal_pos and not locks_s:
            #     print("Direct goal successor found")

            if pos_s == st.goal_pos and not locks_s:
                goal_snapshot = {
                    "grid": deepcopy(grid_s),
                    "player_pos": pos_s,
                    "locks": deepcopy(locks_s),
                    "results": list(results_s)
                }

                temp = {
                    "state": None,
                    "results": deepcopy(results_s),
                    "action_from_parent": action_s,
                    "parent": idx,
                    "g": g_s
                }
                nodes.append(temp)
                path = _reconstruct_path(nodes, len(nodes) - 1)

                return goal_snapshot, generated + 1, path

            level_data = {
                "rows": len(grid_s),
                "cols": len(grid_s[0]) if grid_s else 0,
                "grid": deepcopy(grid_s)
            }
            gs = GameState(level_data)
            gs.locks = deepcopy(locks_s)
            gs.player_pos = pos_s

            nodes.append({
                "state": gs,
                "results": deepcopy(results_s),
                "action_from_parent": action_s,
                "parent": idx,
                "g": g_s
            })

            h = heuristic_estimate(grid_s, pos_s, locks_s)
            heapq.heappush(pq, (g_s + h, len(nodes) - 1))

            visited[sig] = g_s
            generated += 1

            # DEBUG PRINT (node limit)
            # if generated >= max_nodes:
            #     print("Node limit reached")

            if generated >= max_nodes:
                return None, generated, None

    # DEBUG PRINT (search exhausted)
    # print("A* finished with no solution")

    return None, generated, None
