# solver_ucs.py
from copy import deepcopy
from state import GameState
from successor import get_successors
import heapq
import time


def state_signature(grid, player_pos, locks, results):
    frozen_grid = tuple(tuple(row) for row in grid)
    frozen_locks = tuple(sorted(((k, v[0], v[1]) for k, v in locks.items())))
    frozen_results = tuple(sorted(results))
    return (player_pos, frozen_grid, frozen_locks, frozen_results)


def reconstruct_path(nodes, goal_idx):
    path = []
    idx = goal_idx
    while idx is not None:
        node = nodes[idx]
        if node["action_from_parent"] is not None:
            path.append(node["action_from_parent"])
        idx = node["parent"]
    path.reverse()
    return path


def move_cost(successor):
    # حالياً كل حركة كلفتها 1
    return 1


def ucs_solve(game, max_nodes=1_000_000, progress_interval=50000):
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
    heapq.heappush(pq, (0, 0))  # (cost, node_index)

    visited = {}
    root_sig = state_signature(
        root_state.grid,
        root_state.player_pos,
        root_state.locks,
        root_results
    )
    visited[root_sig] = 0

    generated = 1
    expanded = 0
    last_report = 0

    print(f"\n=== UCS START (limit={max_nodes}) ===")
    print(f"Root pos={root_state.player_pos}  Locks={list(root_state.locks.keys())}\n")

    while pq:
        cost, idx = heapq.heappop(pq)
        node = nodes[idx]

        # تجاهل المسارات الأسوأ
        sig = state_signature(
            node["state"].grid,
            node["state"].player_pos,
            node["state"].locks,
            node["results"]
        )
        if visited.get(sig, float("inf")) < cost:
            continue

        expanded += 1

        # 🖨️ طباعة مراقبة مثل A*
        if expanded - last_report >= progress_interval:
            elapsed = time.time() - start_time
            st = node["state"]
            print(f"--- Expanded {expanded} nodes (generated {generated}) ---")
            print(f" Player={st.player_pos}  Locks left={len(st.locks)}  Cost={cost}")
            print(f" Time elapsed: {elapsed:.1f}s")
            print("--------------------------------------------------")
            last_report = expanded

        st = node["state"]

        # 🎯 Goal check
        if st.player_pos == st.goal_pos and not st.locks:
            goal_snapshot = {
                "grid": deepcopy(st.grid),
                "player_pos": st.player_pos,
                "locks": deepcopy(st.locks),
                "results": list(node["results"])
            }
            path = reconstruct_path(nodes, idx)
            print("\n✔ GOAL FOUND (UCS)")
            print(f"Total cost: {cost}")
            print(f"Expanded nodes: {expanded}")
            print(f"Generated nodes: {generated}")
            print(f"Path length: {len(path)}")
            return goal_snapshot, generated, path

        # successors
        class MiniGame:
            def __init__(self, s, r):
                self.state = s
                self.results = r

        mg = MiniGame(deepcopy(st), deepcopy(node["results"]))
        successors = get_successors(mg)

        for s in successors:
            step_cost = move_cost(s)
            new_cost = cost + step_cost

            sig_s = state_signature(
                s["grid"],
                s["player_pos"],
                s["locks"],
                s["results"]
            )

            if sig_s in visited and visited[sig_s] <= new_cost:
                continue

            level_data = {
                "rows": len(s["grid"]),
                "cols": len(s["grid"][0]),
                "grid": deepcopy(s["grid"])
            }
            new_state = GameState(level_data)
            new_state.player_pos = s["player_pos"]
            new_state.locks = deepcopy(s["locks"])
            new_state.goal_pos = st.goal_pos

            nodes.append({
                "state": new_state,
                "results": deepcopy(s["results"]),
                "action_from_parent": s["action"],
                "parent": idx,
                "g": new_cost
            })
            new_idx = len(nodes) - 1

            heapq.heappush(pq, (new_cost, new_idx))
            visited[sig_s] = new_cost
            generated += 1

            if generated >= max_nodes:
                print("\n✖ Node limit reached!")
                return None, generated, None

    print("\n✖ UCS ended. No solution found.")
    return None, generated, None
