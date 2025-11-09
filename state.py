class GameState:
    def __init__(self, level_data):
        self.rows = level_data["rows"]
        self.cols = level_data["cols"]
        self.grid = level_data["grid"]

        # عناصر اللعبة المهمة
        self.player_pos = None
        self.goal_pos = None
        self.locks = {} 

        # نكتشف مواقع العناصر
        self.find_positions()

    def find_positions(self):
        """تبحث في الخريطة عن موقع اللاعب، الأقفال، والهدف."""
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]

                if cell == "P":
                    self.player_pos = (r, c)

                elif cell.startswith("G"):
                    self.locks[cell] = (r, c)

                elif cell == "F":
                    self.goal_pos = (r, c)

    def display(self):
        """.................تطبع الخريطة الحالية في التيرمينال."""
        for r in range(self.rows):
            print(" ".join(self.grid[r]))
        print()

    def get_cell(self, r, c):
        """ترجع محتوى خلية معينة."""
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return self.grid[r][c]
        return None
