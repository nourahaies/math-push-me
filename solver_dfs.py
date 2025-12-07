# solver_dfs.py
from copy import deepcopy
from state import GameState
from successor import get_successors


def _state_signature(grid, player_pos, locks, results):
    """Create a hashable unique signature for a game state."""
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


def dfs_solve(game, max_nodes=1000000):
    """
    DFS search.
    Returns:
      goal_snapshot, generated_nodes_count, path_actions
    Or:
      None, generated_nodes_count, None
    """

    # Root node
    root_state = deepcopy(game.state)
    root_results = deepcopy(game.results)

    nodes = []
    root_node = {
        "state": root_state,
        "results": root_results,
        "action_from_parent": None,
        "parent": None
    }
    nodes.append(root_node)

    stack = [0]

    visited = set()
    visited.add(
        _state_signature(root_state.grid, root_state.player_pos, root_state.locks, root_results)
    )

    generated = 1  # count nodes

    print(f"\n=== DFS START (limit={max_nodes}) ===")
    print(f"Root pos={root_state.player_pos}  Locks={list(root_state.locks.keys())}\n")

    while stack:
        current_idx = stack.pop()
        node = nodes[current_idx]

        cur_state = node["state"]
        cur_results = node["results"]

        # Goal check
        if cur_state.player_pos == cur_state.goal_pos and not cur_state.locks:
            goal_snapshot = {
                "grid": deepcopy(cur_state.grid),
                "player_pos": cur_state.player_pos,
                "locks": deepcopy(cur_state.locks),
                "results": list(cur_results)
            }
            path = _reconstruct_path(nodes, current_idx)
            print("\n✔ GOAL FOUND!")
            print(f"Generated nodes: {generated}")
            print(f"Path length: {len(path)}")
            return goal_snapshot, generated, path

        # Build successor generator
        class _MiniGame:
            def __init__(self, s, r):
                self.state = s
                self.results = r

        mg = _MiniGame(deepcopy(cur_state), deepcopy(cur_results))
        successors = get_successors(mg)

        for s in successors:
            grid_s = s["grid"]
            pos_s = s["player_pos"]
            locks_s = s["locks"]
            results_s = s["results"]
            action_s = s["action"]

            sig = _state_signature(grid_s, pos_s, locks_s, results_s)
            if sig in visited:
                continue

            # Quick goal check BEFORE building GameState
            if pos_s == cur_state.goal_pos and not locks_s:
                goal_snapshot = {
                    "grid": deepcopy(grid_s),
                    "player_pos": pos_s,
                    "locks": deepcopy(locks_s),
                    "results": list(results_s)
                }

                # Build miniature node to reconstruct path
                temp = {
                    "state": None,
                    "results": deepcopy(results_s),
                    "action_from_parent": action_s,
                    "parent": current_idx
                }
                nodes.append(temp)
                goal_index = len(nodes) - 1

                path = _reconstruct_path(nodes, goal_index)
                print("\n✔ GOAL FOUND (direct successor)!")
                print(f"Generated nodes: {generated}")
                print(f"Path length: {len(path)}")
                return goal_snapshot, generated + 1, path

            # Normal expansion
            level_data = {
                "rows": len(grid_s),
                "cols": len(grid_s[0]),
                "grid": deepcopy(grid_s)
            }

            gs = GameState(level_data)
            gs.locks = deepcopy(locks_s)
            gs.player_pos = pos_s

            new_node = {
                "state": gs,
                "results": deepcopy(results_s),
                "action_from_parent": action_s,
                "parent": current_idx
            }

            nodes.append(new_node)
            new_idx = len(nodes) - 1
            stack.append(new_idx)
            visited.add(sig)
            generated += 1

            if max_nodes and generated >= max_nodes:
                print("\n✖ Node limit reached! No solution found.")
                return None, generated, None

    print("\n✖ DFS ended. No solution found.")
    return None, generated, None
