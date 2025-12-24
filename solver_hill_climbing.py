import heapq
from copy import deepcopy
from state import GameState
from successor import get_successors

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def heuristic(grid, player_pos, locks, goal_pos, results):
    # 1. إذا الأقفال صفر، الهدف هو وجهتنا الوحيدة
    if not locks:
        return manhattan(player_pos, goal_pos)

    # 2. البحث عن كل الأهداف الممكنة (أرقام، عمليات، أقفال)
    tools = []

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            cell = grid[r][c]
            if not cell: continue
            
            # أرقام وعمليات
            if cell.isdigit() or cell in ['+', '-']:
                tools.append((r, c))
            
    # 3. حساب المسافات
    dist_to_tools = min([manhattan(player_pos, t) for t in tools]) if tools else 0
    
    # 4. المعادلة الموزونة (The Golden Formula)
    # هاد الترتيب بيخلي اللاعب يفضل الأقفال، بس ما ينسى الأرقام
    h = (len(locks) * 10000)      # أهم شيء: عدد الأقفال المتبقية
    h += (dist_to_tools * 10)     # ثاني أهم شيء: القرب من الأرقام عشان يجمع "ذخيرة"
    
    return h

def hill_climbing_solve(game, max_nodes=300000):
    root_state = game.state
    root_results = game.results
    
    # ✅ تم إضافة root_results هنا
    start_h = heuristic(root_state.grid, root_state.player_pos, root_state.locks, root_state.goal_pos, root_results)
    
    frontier = []
    counter = 0
    heapq.heappush(frontier, (start_h, counter, root_state, root_results, []))
    
    visited = {} 
    
    print("\n=== FINAL EMERGENCY RECOVERY START ===")

    while frontier:
        h, _, cur_state, cur_results, path = heapq.heappop(frontier)

        sig = (cur_state.player_pos, 
               tuple(tuple(row) for row in cur_state.grid), 
               tuple(sorted(cur_state.locks.keys())),
               tuple(sorted(cur_results)))

        if sig in visited and visited[sig] <= h:
            continue
        visited[sig] = h

        if cur_state.player_pos == cur_state.goal_pos and not cur_state.locks:
            print(f"✔ SUCCESS! Goal reached in {len(path)} moves.")
            goal_snapshot = {
                "grid": cur_state.grid,
                "player_pos": cur_state.player_pos,
                "locks": cur_state.locks,
                "results": cur_results
            }
            return goal_snapshot, len(visited), path

        class MiniGame:
            def __init__(self, s, r):
                self.state = s
                self.results = r
        
        mg = MiniGame(cur_state, cur_results)
        successors = get_successors(mg)

        for s in successors:
            # ✅ تم إضافة s["results"] هنا
            new_h = heuristic(s["grid"], s["player_pos"], s["locks"], cur_state.goal_pos, s["results"])
            
            level_data = {"rows": len(s["grid"]), "cols": len(s["grid"][0]), "grid": s["grid"]}
            new_gs = GameState(level_data)
            new_gs.player_pos = s["player_pos"]
            new_gs.locks = s["locks"]
            new_gs.goal_pos = cur_state.goal_pos
            
            counter += 1
            heapq.heappush(frontier, (new_h, counter, new_gs, s["results"], path + [s["action"]]))

        if counter > max_nodes: break

    print("✖ Failed: The map is too complex for Hill Climbing.")
    return None, counter, None