from evaluator import scan_expressions


class Game:
    def __init__(self, level_data):
        # إنشاء حالة اللعبة
        from state import GameState
        self.state = GameState(level_data)

    def move_player(self, direction):
        """
        يحرك اللاعب في الاتجاه المطلوب إذا كان ذلك ممكنًا.
        الاتجاهات المقبولة: up, down, left, right
        """
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
            return  # اتجاه غير معروف

        pr, pc = self.state.player_pos
        new_r, new_c = pr + dr, pc + dc

        # الخلية الهدف
        target_cell = self.state.get_cell(new_r, new_c)

        if target_cell is None or target_cell == "#":
            return  # جدار أو خارج الحدود → لا يتحرك

        # إذا الخلية فارغة → يتحرك فقط
        if target_cell == ".":
            self._update_position(pr, pc, new_r, new_c)
            # بعد الحركة، نفحص التعابير
            self.check_expressions()
            return

        # إذا الخلية فيها عنصر قابل للدفع (رقم أو + أو -)
        if target_cell.isdigit() or target_cell in ["+", "-"]:
            push_r, push_c = new_r + dr, new_c + dc
            next_cell = self.state.get_cell(push_r, push_c)

            # نتأكد إنو المكان يلي رح ندفع فيه فاضي
            if next_cell == ".":
                # نحرك الكتلة
                self.state.grid[push_r][push_c] = target_cell
                self._update_position(pr, pc, new_r, new_c)
                self.state.grid[new_r][new_c] = "P"
                # بعد الحركة، نفحص التعابير
                self.check_expressions()
                return

       

        # إذا ما تحقق أي شرط → لا يتحرك
        return

    def _update_position(self, old_r, old_c, new_r, new_c):
        """تحديث موقع اللاعب على الخريطة"""
        self.state.grid[old_r][old_c] = "."
        self.state.grid[new_r][new_c] = "P"
        self.state.player_pos = (new_r, new_c)

    def display(self):
        """عرض الخريطة"""
        self.state.display()

    def check_expressions(self):
        """تفحص الخريطة وتعرض النتائج المكتشفة."""
        results = scan_expressions(self.state.grid)
        if results:
            print("Detected expressions → Results:", results)