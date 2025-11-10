from evaluator import scan_expressions


class Game:
    def __init__(self, level_data):
        from state import GameState
        from copy import deepcopy

        self.state = GameState(level_data)
        self.initial_grid = deepcopy(self.state.grid)


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
            return

        # 🟢 حفظ الحالة قبل أي تغيير
        self.state.save_state()

        # ----------------------------
        # إذا الخلية الهدف هي Finish
        # ----------------------------
        if target_cell == "F":
            if self.state.locks:
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
        if not results:
            return

        print("Detected expressions → Results:", results)
        locks_to_remove = []

        for value in results:
            key_to_remove = None
            for lock_key, (r, c) in self.state.locks.items():
                if lock_key.startswith("G") and lock_key[1:] == str(value):
                    print(f"🔓 Lock {lock_key} opened!")
                    self.state.grid[r][c] = "."
                    key_to_remove = lock_key
                    break

            if key_to_remove:
                locks_to_remove.append(key_to_remove)

        for key in locks_to_remove:
            self.state.locks.pop(key, None)

    def reset(self):
        """إعادة اللعبة إلى حالتها الأصلية"""
        from copy import deepcopy
        # نرجع الحالة الأصلية
        self.state.grid = deepcopy(self.initial_grid)
        self.state.find_positions()
        print("🔁 Game reset!")
