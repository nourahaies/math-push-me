# solver_bfs.py
from collections import deque
from copy import deepcopy
from state import GameState
from successor import get_successors


def state_signature(grid, player_pos, locks, results):
    frozen_grid = tuple(tuple(row) for row in grid)
    frozen_locks = tuple(sorted((k, v) for k, v in locks.items()))
    frozen_results = tuple(sorted(results))
    return (player_pos, frozen_grid, frozen_locks, frozen_results)


def reconstruct_path(nodes, goal_idx):
    path = []
    idx = goal_idx
    while idx is not None:
        node = nodes[idx]
        if node["action"] is not None:
            path.append(node["action"])
        idx = node["parent"]
    return path[::-1]


def bfs_solve(game, max_nodes=300000):

    # DEBUG PRINT — BFS start
    # print("\n=== BFS START ===")

    root_state = deepcopy(game.state)
    root_results = deepcopy(game.results)

    nodes = [{
        "state": root_state,
        "results": root_results,
        "parent": None,
        "action": None
    }]

    queue = deque([0])
    visited = set()

    root_sig = state_signature(
        root_state.grid,
        root_state.player_pos,
        root_state.locks,
        root_results
    )
    visited.add(root_sig)

    generated = 1
    expanded = 0

    while queue:
        idx = queue.popleft()
        node = nodes[idx]
        expanded += 1

        state = node["state"]
        results = node["results"]

        # DEBUG PRINT — node expansion info
        # print(
        #     f"\n----- Expanded node {idx} (step {expanded}) -----\n"
        #     f"Player pos: {state.player_pos}\n"
        #     f"Remaining locks: {list(state.locks.keys())}\n"
        #     f"Results: {results}\n"
        #     f"---------------------------------------------"
        # )

        # 🎯 Goal check
        if state.player_pos == state.goal_pos and not state.locks:
            path = reconstruct_path(nodes, idx)

            # DEBUG PRINT — goal found
            # print("\n✔ GOAL FOUND!----using BFS")
            # print(f"Expanded nodes: {expanded}")
            # print(f"Generated nodes: {generated}")
            # print(f"Path length: {len(path)}")

            return state, generated, path

        # Mini game for successors
        class MiniGame:
            def __init__(self, s, r):
                self.state = s
                self.results = r

        mg = MiniGame(deepcopy(state), deepcopy(results))
        successors = get_successors(mg)

        for s in successors:
            action = s["action"]
            new_pos = s["player_pos"]
            new_locks = s["locks"]

            # DEBUG PRINT — trying action
            # print(f" Trying action: {action} → moves to {new_pos}")

            sig = state_signature(
                s["grid"],
                new_pos,
                new_locks,
                s["results"]
            )

            if sig in visited:
                # DEBUG PRINT — visited state skipped
                # print("   ⤷ Skipped (already visited)")
                continue

            if len(new_locks) < len(state.locks):
                # DEBUG PRINT — lock opened
                # print("   🔓 Lock opened!")
                pass

            level_data = {
                "rows": len(s["grid"]),
                "cols": len(s["grid"][0]),
                "grid": deepcopy(s["grid"])
            }

            new_state = GameState(level_data)
            new_state.player_pos = new_pos
            new_state.locks = deepcopy(new_locks)
            new_state.goal_pos = state.goal_pos

            nodes.append({
                "state": new_state,
                "results": deepcopy(s["results"]),
                "parent": idx,
                "action": action
            })

            queue.append(len(nodes) - 1)
            visited.add(sig)
            generated += 1

            # DEBUG PRINT — new node added
            # print(f"   ✓ Added new node. Player at {new_pos}, locks_left={len(new_locks)}")

            if generated >= max_nodes:
                # DEBUG PRINT — node limit reached
                # print("\n✖ Node limit reached!")
                return None, generated, None

    # DEBUG PRINT — BFS exhausted
    # print("\n✖ BFS ended. No solution found.")
    # print(f"Expanded nodes: {expanded}")
    # print(f"Generated nodes: {generated}")

    goal_snapshot = {
        "grid": deepcopy(state.grid),
        "player_pos": state.player_pos,
        "locks": deepcopy(state.locks),
        "results": list(results)
    }
    return goal_snapshot, generated, None
