from copy import deepcopy
from state import GameState
from successor import get_successors

# دالة البصمة لضمان عدم التكرار (من كود الـ DFS السابق)
def _state_signature(grid, player_pos, locks, results):
    frozen_grid = tuple(tuple(row) for row in grid)
    frozen_locks = tuple(sorted(((k, v[0], v[1]) for k, v in locks.items())))
    frozen_results = tuple(sorted(results))
    return (player_pos, frozen_grid, frozen_locks, frozen_results)

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def heuristic(grid, player_pos, locks, goal_pos, initial_locks_count):
    # 1️⃣ عقوبة الأقفال
    lock_penalty = 100 * len(locks)
    
    # 2️⃣ مكافأة فتح الأقفال (منطق رفيقتك)
    unlocked_bonus = (initial_locks_count - len(locks)) * 50
    
    # 3️⃣ المسافة للهدف
    goal_dist = manhattan(player_pos, goal_pos)
    
    # القيمة النهائية (كلما صغرت كان أفضل)
    return lock_penalty + goal_dist - unlocked_bonus

def hill_climbing_solve(game, max_steps=100000):
    """
    Modified Hill Climbing (Best-First Logic) 
    بمنطق رفيقتك: استخدام قائمة (Frontier) لتجنب القمم المحلية
    """
    root_state = deepcopy(game.state)
    root_results = deepcopy(game.results)
    initial_locks_count = len(root_state.locks)

    # الأرشيف والقائمة (Frontier)
    nodes = []
    root_h = heuristic(root_state.grid, root_state.player_pos, root_state.locks, root_state.goal_pos, initial_locks_count)
    
    # نضع: (الهرستك، الحالة، النتائج، الطريق، الأب)
    frontier = [(root_h, root_state, root_results, [])]
    visited = set()
    
    generated = 0

    print("\n=== ENHANCED HILL CLIMBING START ===")

    while frontier:
        # فرز القائمة لاختيار أفضل عقدة (مثل كود رفيقتك)
        frontier.sort(key=lambda x: x[0])
        current_h, cur_state, cur_results, path = frontier.pop(0)

        # بصمة الحالة لمنع الحلقات
        sig = _state_signature(cur_state.grid, cur_state.player_pos, cur_state.locks, cur_results)
        if sig in visited:
            continue
        visited.add(sig)

        # 🎯 فحص الهدف
        if cur_state.player_pos == cur_state.goal_pos and not cur_state.locks:
            goal_snapshot = {
                "grid": deepcopy(cur_state.grid),
                "player_pos": cur_state.player_pos,
                "locks": deepcopy(cur_state.locks),
                "results": list(cur_results)
            }
            print(f"✔ GOAL FOUND! States explored: {len(visited)}")
            return goal_snapshot, len(path), path

        # استكشاف الجيران
        class MiniGame:
            def __init__(self, s, r):
                self.state = s
                self.results = r

        mg = MiniGame(deepcopy(cur_state), deepcopy(cur_results))
        successors = get_successors(mg)

        for s in successors:
            h = heuristic(s["grid"], s["player_pos"], s["locks"], cur_state.goal_pos, initial_locks_count)
            
            # إنشاء كائن الحالة الجديد
            level_data = {"rows": len(s["grid"]), "cols": len(s["grid"][0]), "grid": deepcopy(s["grid"])}
            new_gs = GameState(level_data)
            new_gs.player_pos = s["player_pos"]
            new_gs.locks = deepcopy(s["locks"])
            new_gs.goal_pos = cur_state.goal_pos
            
            # إضافة الجار للقائمة (Frontier)
            frontier.append((h, new_gs, s["results"], path + [s["action"]]))
            generated += 1

        if len(visited) > max_steps:
            break

    print("✖ No solution found or limit reached.")
    return None, 0, None