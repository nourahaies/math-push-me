#game.py
from evaluator import scan_expressions


class Game:
    def __init__(self, level_data):
        from state import GameState
        from copy import deepcopy

        self.state = GameState(level_data)
        self.initial_grid = deepcopy(self.state.grid)
        self.results = []  

    def move_player(self, direction):
        
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

        
        if target_cell is None or target_cell == "#":
            
            print("Results array:", self.results)
            return

        
        self.state.save_state()

        
        if target_cell == "F":
            if self.state.locks:
                
                print("Results array:", self.results)
                return
            else:
                self._update_position(pr, pc, new_r, new_c)
                print("🎉 You won this level!")
                return

        
        if target_cell == ".":
            self._update_position(pr, pc, new_r, new_c)
            self.check_expressions()
            return

        
        if target_cell.isdigit() or target_cell in ["+", "-"]:
            
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

            
            if next_cell == ".":
                
                for (br, bc, val) in reversed(movable_blocks):
                    self.state.grid[br + dr][bc + dc] = val
                    self.state.grid[br][bc] = "."

                
                self._update_position(pr, pc, new_r, new_c)
                self.check_expressions()
                return

        
        print("Results array:", self.results)
        return

    
    #    (Undo)
    
    def undo(self):
        
        success = self.state.restore_state()
        if success:
            print("Undo successful.")
        else:
            print("Nothing to undo.")

    
    def _update_position(self, old_r, old_c, new_r, new_c):
        self.state.grid[old_r][old_c] = "."
        self.state.grid[new_r][new_c] = "P"
        self.state.player_pos = (new_r, new_c)

    def display(self):
        self.state.display()

    def check_expressions(self):
        results = scan_expressions(self.state.grid)
        
        
        if self.results:
            print("Results so far:", self.results)
        
        
        if not results:
            return
        
        
        print("New expressions found:", results)
        

        locks_to_remove = []
        new_results_found = False

        for value in results:
            
            if value not in self.results:
                self.results.append(value)
                new_results_found = True
                print(f"Solved: {value}")
            
            
            key_to_remove = None
            for lock_key, (r, c) in self.state.locks.items():
                if lock_key.startswith("G") and lock_key[1:] == str(value):
                    print(f"🔓 Opened door {lock_key}!")
                    self.state.grid[r][c] = "."
                    key_to_remove = lock_key
                    break

            if key_to_remove:
                locks_to_remove.append(key_to_remove)

        
        for key in locks_to_remove:
            self.state.locks.pop(key, None)
            
        
        if new_results_found and self.results:
            print("All results:", self.results)

    def reset(self):
        
        from copy import deepcopy
        
        self.state.grid = deepcopy(self.initial_grid)
        self.state.find_positions()
        print("🔁 Game reset!")
