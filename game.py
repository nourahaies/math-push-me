from evaluator import scan_expressions


class Game:
    def __init__(self, level_data):
        from state import GameState
        from copy import deepcopy

        self.state = GameState(level_data)
        self.initial_grid = deepcopy(self.state.grid)
        self.results = []  # Array to store results of solved expressions

    def move_player(self, direction):
        """يحرك اللاعب في الاتجاه المطلوب إذا كان ذلك ممكنًا."""
        dr, dc = 0, 0
        if direction == "up":
            dr, dc = -1, 0
        elif direction == "down":
            dr, dc = 1, 0
        elif direction == "left":
            dr, dc = 0, -1
        elif direction == "right":
            dr, dc = 0, 1
        else:
            return

        pr, pc = self.state.player_pos
        new_r, new_c = pr + dr, pc + dc

        target_cell = self.state.get_cell(new_r, new_c)

        # جدار أو خارج الحدود
        if target_cell is None or target_cell == "#":
            # Print results array even when move is invalid
            print("Results array:", self.results)
            return

        # 🟢 حفظ الحالة قبل أي تغيير
        self.state.save_state()

        # ----------------------------
        # إذا الخلية الهدف هي Finish
        # ----------------------------
        if target_cell == "F":
            if self.state.locks:
                # Print results array
                print("Results array:", self.results)
                return
            else:
                self._update_position(pr, pc, new_r, new_c)
                print("🎉 You won this level!")
                return

        # ----------------------------
        # إذا الخلية فارغة → يتحرك فقط
        # ----------------------------
        if target_cell == ".":
            self._update_position(pr, pc, new_r, new_c)
            self.check_expressions()
            return

        # -------------------------------------------------
        # إذا الخلية فيها عنصر قابل للدفع (رقم أو + أو -)
        # -------------------------------------------------
        if target_cell.isdigit() or target_cell in ["+", "-"]:
            # نجمع كل الكتل المتجاورة بنفس الاتجاه
            movable_blocks = []
            r, c = new_r, new_c
            while True:
                cell = self.state.get_cell(r, c)
                if cell and (cell.isdigit() or cell in ["+", "-"]):
                    movable_blocks.append((r, c, cell))
                    r += dr
                    c += dc
                else:
                    break

            next_cell = self.state.get_cell(r, c)

            # لازم الخلية التالية تكون فاضية
            if next_cell == ".":
                # نحرك الكتل ابتداءً من الأبعد
                for (br, bc, val) in reversed(movable_blocks):
                    self.state.grid[br + dr][bc + dc] = val
                    self.state.grid[br][bc] = "."

                # ثم نحرك اللاعب
                self._update_position(pr, pc, new_r, new_c)
                self.check_expressions()
                return

        # إذا ما تحقق أي شرط → لا يتحرك
        # Print results array when no movement occurs
        print("Results array:", self.results)
        return

    # --------------------------
    # 🟣 دالة التراجع (Undo)
    # --------------------------
    def undo(self):
        """تُرجع اللعبة لحالتها السابقة."""
        success = self.state.restore_state()
        if success:
            print("↩️ Undo successful.")
        else:
            print("⚠️ Nothing to undo.")

    # --------------------------
    # دوال مساعدة
    # --------------------------
    def _update_position(self, old_r, old_c, new_r, new_c):
        self.state.grid[old_r][old_c] = "."
        self.state.grid[new_r][new_c] = "P"
        self.state.player_pos = (new_r, new_c)

    def display(self):
        self.state.display()

    def check_expressions(self):
        results = scan_expressions(self.state.grid)
        
        # Only print results array if it's not empty
        if self.results:
            print("Results so far:", self.results)
        
        # Only process if we have detected expressions
        if not results:
            return
        
        # Print detected expressions for debugging
        print("New expressions found:", results)
        
        # Process each detected result
        locks_to_remove = []
        new_results_found = False

        for value in results:
            # Add the result to our results array if not already there
            if value not in self.results:
                self.results.append(value)
                new_results_found = True
                print(f"Solved: {value}")
            
            # Check if this result opens any locks
            key_to_remove = None
            for lock_key, (r, c) in self.state.locks.items():
                if lock_key.startswith("G") and lock_key[1:] == str(value):
                    print(f"🔓 Opened door {lock_key}!")
                    self.state.grid[r][c] = "."
                    key_to_remove = lock_key
                    break

            if key_to_remove:
                locks_to_remove.append(key_to_remove)

        # Remove opened locks
        for key in locks_to_remove:
            self.state.locks.pop(key, None)
            
        # If we found new results, print the updated array
        if new_results_found and self.results:
            print("All results:", self.results)

    def reset(self):
        """إعادة اللعبة إلى حالتها الأصلية"""
        from copy import deepcopy
        # نرجع الحالة الأصلية
        self.state.grid = deepcopy(self.initial_grid)
        self.state.find_positions()
        print("🔁 Game reset!")
