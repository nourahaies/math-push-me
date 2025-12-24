import heapq
import time
from copy import deepcopy
from state import GameState
from successor import get_successors

def _state_signature(grid, player_pos, locks, results):
    """Create a compact hashable signature for a state."""
    frozen_grid = tuple(tuple(row) for row in grid)
    frozen_locks = tuple(sorted(locks.keys()))
    frozen_results = tuple(sorted(results))
    return (player_pos, frozen_grid, frozen_locks, frozen_results)

def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def heuristic(grid, player_pos, locks, goal_pos, results):
    """
    The Golden Formula Heuristic
    Directs the player to locks first, then tools to minimize search space.
    """
    if not locks:
        return _manhattan(player_pos, goal_pos)

    tools = []
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            cell = grid[r][c]
            if cell and (cell.isdigit() or cell in ['+', '-']):
                tools.append((r, c))
            
    dist_to_tools = min([_manhattan(player_pos, t) for t in tools]) if tools else 0
    
    # Heuristic weighting
    h = (len(locks) * 10000)      
    h += (dist_to_tools * 10)     
    return h

def hill_climbing_solve(game, max_nodes=300000):
    """
    Hill Climbing (Greedy Best-First Search) solver.
    """
    start_time = time.time()
    root_state = game.state
    root_results = game.results
    
    start_h = heuristic(root_state.grid, root_state.player_pos, root_state.locks, root_state.goal_pos, root_results)
    
    frontier = []
    counter = 0
    heapq.heappush(frontier, (start_h, counter, root_state, root_results, []))
    
    visited = {} 
    generated = 1

    # DEBUG PRINT (solver start - commented for clean output)
    # print(f"\n=== HILL CLIMBING START (limit={max_nodes}) ===")

    while frontier:
        h, _, cur_state, cur_results, path = heapq.heappop(frontier)

        sig = _state_signature(cur_state.grid, cur_state.player_pos, cur_state.locks, cur_results)
        if sig in visited and visited[sig] <= h:
            continue
        visited[sig] = h

        # 🎯 Goal Check
        if cur_state.player_pos == cur_state.goal_pos and not cur_state.locks:
            print(f"✔ SUCCESS: Goal state reached. Path Length: {len(path)}")
            goal_snapshot = {
                "grid": cur_state.grid,
                "player_pos": cur_state.player_pos,
                "locks": cur_state.locks,
                "results": cur_results
            }
            return goal_snapshot, generated, path

        class MiniGame:
            def __init__(self, s, r):
                self.state = s
                self.results = r
        
        mg = MiniGame(cur_state, cur_results)
        successors = get_successors(mg)

        for s in successors:
            new_h = heuristic(s["grid"], s["player_pos"], s["locks"], cur_state.goal_pos, s["results"])
            
            level_data = {"rows": len(s["grid"]), "cols": len(s["grid"][0]), "grid": s["grid"]}
            new_gs = GameState(level_data)
            new_gs.player_pos = s["player_pos"]
            new_gs.locks = s["locks"]
            new_gs.goal_pos = cur_state.goal_pos
            
            generated += 1
            counter += 1
            heapq.heappush(frontier, (new_h, counter, new_gs, s["results"], path + [s["action"]]))

            # Node Limit Termination
            if generated >= max_nodes:
                print(f"✖ FAILED: Node limit exceeded ({max_nodes}).")
                return None, generated, None

    # Search Exhausted (Stuck in Local Optimum)
    print("✖ FAILED: Search exhausted. Stuck in a local optimum.")
    return None, generated, None