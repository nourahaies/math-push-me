#state.py
import copy

class GameState:
    def __init__(self, level_data):
        self.rows = level_data["rows"]
        self.cols = level_data["cols"]
        self.grid = level_data["grid"]

        self.player_pos = None
        self.goal_pos = None
        self.locks = {}

        self.history = []
        self.max_history = 100 

        self.find_positions()

    def find_positions(self):

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]

                if cell == "P":
                    self.player_pos = (r, c)
                elif cell.startswith("G"):
                    self.locks[cell] = (r, c)
                elif cell == "F":
                    self.goal_pos = (r, c)

    
    #    Undo
    
    def save_state(self):
        
        snapshot = {
            "grid": copy.deepcopy(self.grid),
            "player_pos": self.player_pos,
            "locks": copy.deepcopy(self.locks)
        }
        self.history.append(snapshot)
        # إذا تجاوزت الحد → احذف الأقدم
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def restore_state(self):
        
        if not self.history:
            print("No previous state to undo.")
            return False

        snapshot = self.history.pop()
        self.grid = copy.deepcopy(snapshot["grid"])
        self.player_pos = snapshot["player_pos"]
        self.locks = copy.deepcopy(snapshot["locks"])
        return True

    
    def display(self):
        for r in range(self.rows):
            print(" ".join(self.grid[r]))
        print()

    def get_cell(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return self.grid[r][c]
        return None
