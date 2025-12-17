import tkinter as tk
from tkinter import messagebox, scrolledtext
import sys
import traceback
import os
import glob

try:
    from level_loader import load_level
    from game import Game
    # Import solvers
    from solver_dfs import dfs_solve
    from solver_bfs import bfs_solve
    from solver_astar import astar_solve
    from solver_ucs import ucs_solve
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class MathPushGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Push Game")
        self.root.geometry("1000x800")
        self.root.minsize(900, 700)
        self.root.resizable(True, True)
        self.game_won = False  # Track if game is won
        self.last_direction = "up"  # Track last movement direction for player orientation
        
        try:
            # Load level and initialize game
            self.level = load_level("levels/level1.json")
            self.game = Game(self.level)
            
            # Create UI elements
            self.create_widgets()
            
            # Draw initial game state
            self.draw_game()
            
            # Bind keyboard events
            self.root.bind("<KeyPress>", self.on_key_press)
            self.root.focus_set()
        except Exception as e:
            error_msg = f"Error initializing game: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
            sys.exit(1)

    def create_widgets(self):
        # Create main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_container, text="Math Push Game", font=("Arial", 20, "bold"))
        title_label.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(
            main_container, 
            text="Use WASD keys to move. U to undo. R to reset. Q to quit.",
            font=("Arial", 10)
        )
        instructions.pack(pady=5)
        
        # Level selector with improved styling
        level_frame = tk.Frame(main_container, bg="#f0f0f0", padx=10, pady=5)
        level_frame.pack(pady=5)
        
        tk.Label(level_frame, text="Select Level:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(side=tk.LEFT)
        
        # Get all level files from the levels directory
        level_files = glob.glob("levels/level*.json")
        # Also include field files
        field_files = glob.glob("levels/field*.json")
        all_level_files = level_files + field_files
        level_names = [os.path.basename(f) for f in all_level_files]
        level_names.sort()
        
        # If no levels found, provide default options
        if not level_names:
            level_names = ["level1.json", "level2.json", "field5.json"]
        
        self.level_var = tk.StringVar(value=level_names[0] if level_names else "level1.json")
        
        # Create a styled OptionMenu
        level_menu = tk.OptionMenu(
            level_frame, 
            self.level_var, 
            *level_names,
            command=self.change_level
        )
        level_menu.config(
            font=("Arial", 10),
            width=10,
            bg="pink",
            fg="deeppink",
            activebackground="lightpink",
            relief=tk.RAISED,
            borderwidth=2
        )
        level_menu.pack(side=tk.LEFT, padx=5)
        
        # Configure the dropdown menu colors
        level_menu["menu"].config(
            font=("Arial", 10),
            bg="white",
            fg="black"
        )
        
        # Create a frame for the game area
        game_frame = tk.Frame(main_container)
        game_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Left side - Game canvas and controls
        left_frame = tk.Frame(game_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Game canvas
        canvas_frame = tk.Frame(left_frame)
        canvas_frame.pack(pady=10)
        
        self.canvas = tk.Canvas(
            canvas_frame, 
            width=350, 
            height=350, 
            bg="white", 
            highlightthickness=2, 
            highlightbackground="black"
        )
        self.canvas.pack()
        
        # Control buttons
        button_frame = tk.Frame(left_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="↑", command=lambda: self.move("up"), width=5, height=2).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="←", command=lambda: self.move("left"), width=5, height=2).grid(row=1, column=0, padx=5)
        tk.Button(button_frame, text="↓", command=lambda: self.move("down"), width=5, height=2).grid(row=1, column=1, padx=5)
        tk.Button(button_frame, text="→", command=lambda: self.move("right"), width=5, height=2).grid(row=1, column=2, padx=5)
        
        tk.Button(button_frame, text="Undo (U)", command=self.undo_move, width=10).grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="Reset (R)", command=self.reset_game, width=10).grid(row=1, column=3, padx=5)
        
        # Right side - Solvers and results
        right_frame = tk.Frame(game_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        # Solver buttons
        solver_frame = tk.LabelFrame(right_frame, text="Solvers", font=("Arial", 12, "bold"), padx=10, pady=10)
        solver_frame.pack(pady=10, fill=tk.X)
        
        # Frame for solver buttons
        buttons_frame = tk.Frame(solver_frame)
        buttons_frame.pack()
        
        tk.Button(buttons_frame, text="DFS", command=self.run_dfs, width=10, height=2, bg="lightblue", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5)
        tk.Button(buttons_frame, text="BFS", command=self.run_bfs, width=10, height=2, bg="lightgreen", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=5)
        tk.Button(buttons_frame, text="A*", command=self.run_astar, width=10, height=2, bg="lightyellow", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5)
        tk.Button(buttons_frame, text="UCS", command=self.run_ucs, width=10, height=2, bg="lightcoral", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=5)
        
        # Results display area
        results_frame = tk.LabelFrame(right_frame, text="Solver Results", font=("Arial", 12, "bold"), padx=10, pady=10)
        results_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, width=50, height=15, wrap=tk.WORD)
        self.results_text.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Use WASD to move")
        self.status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var, 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def change_level(self, level_name):
        """Change the current level"""
        try:
            level_file = f"levels/{level_name}"
            self.level = load_level(level_file)
            self.game = Game(self.level)
            self.game_won = False  # Reset win status
            self.last_direction = "up"  # Reset player direction
            self.draw_game()
            self.status_var.set(f"Level changed to {level_name}")
        except Exception as e:
            error_msg = f"Failed to load level: {str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)

    def draw_game(self):
        """Draw the current game state on the canvas"""
        self.canvas.delete("all")
        
        try:
            # Get actual canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # If canvas dimensions are not yet available, use configured size
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 350
                canvas_height = 350
            
            # Cell size calculation
            rows = self.game.state.rows
            cols = self.game.state.cols
            cell_size = min(canvas_width // cols, canvas_height // rows)
            offset_x = (canvas_width - cols * cell_size) // 2
            offset_y = (canvas_height - rows * cell_size) // 2
            
            # Draw grid
            for r in range(rows):
                for c in range(cols):
                    x1 = offset_x + c * cell_size
                    y1 = offset_y + r * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    
                    cell = self.game.state.grid[r][c]
                    
                    # Draw cell background
                    if cell == "#":
                        # Walls (changed to purple)
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill="purple", outline="black")
                    else:
                        # Empty cells (changed to pink)
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill="pink", outline="black")
                    
                    # Draw cell content
                    if cell == "P":
                        # Player (triangle pointing in last movement direction)
                        self.draw_player_triangle(x1, y1, x2, y2)
                    elif cell == "F":
                        # Finish (changed to red)
                        self.canvas.create_rectangle(
                            x1 + 5, y1 + 5, x2 - 5, y2 - 5, 
                            fill="red", outline="darkred", width=2
                        )
                    elif cell.startswith("G"):
                        # Lock (changed to white with black number)
                        self.canvas.create_rectangle(
                            x1 + 5, y1 + 5, x2 - 5, y2 - 5, 
                            fill="white", outline="black", width=2
                        )
                        self.canvas.create_text(
                            (x1 + x2) // 2, (y1 + y2) // 2, 
                            text=cell[1:], font=("Arial", 12, "bold"), fill="black"
                        )
                    elif cell.isdigit() or cell in ["+", "-"]:
                        # Number or operator
                        self.canvas.create_text(
                            (x1 + x2) // 2, (y1 + y2) // 2, 
                            text=cell, font=("Arial", 16, "bold"), fill="black"
                        )
                    elif cell == ".":
                        # Empty cell
                        pass
                        
        except Exception as e:
            error_msg = f"Error drawing game: {str(e)}"
            print(error_msg)
            self.status_var.set(error_msg)

    def move(self, direction):
        """Move player in the specified direction"""
        try:
            self.game.move_player(direction)
            self.last_direction = direction  # Track the direction for player orientation
            
            # Check win condition
            if self.is_game_won():
                self.game_won = True
                self.status_var.set("Level completed! Select another level.")
            else:
                self.status_var.set(f"Moved {direction}")
                
            self.draw_game()
            
            # Show win message on GUI if game is won
            if self.game_won:
                self.show_win_message()
        except Exception as e:
            error_msg = f"Error moving player: {str(e)}"
            print(error_msg)
            self.status_var.set(error_msg)

    def undo_move(self):
        """Undo the last move"""
        try:
            self.game.undo()
            self.game_won = False  # Reset win status when undoing
            self.draw_game()
            self.status_var.set("Move undone")
        except Exception as e:
            error_msg = f"Error undoing move: {str(e)}"
            print(error_msg)
            self.status_var.set(error_msg)

    def reset_game(self):
        """Reset the game to initial state"""
        try:
            self.game.reset()
            self.game_won = False  # Reset win status
            self.last_direction = "up"  # Reset player direction
            self.draw_game()
            self.status_var.set("Game reset")
        except Exception as e:
            error_msg = f"Error resetting game: {str(e)}"
            print(error_msg)
            self.status_var.set(error_msg)

    def is_game_won(self):
        """Check if the game is won"""
        try:
            # Check if player reached the finish and there are no locks
            pr, pc = self.game.state.player_pos
            cell = self.game.state.grid[pr][pc]
            return cell == "F" and not self.game.state.locks
        except Exception as e:
            print(f"Error checking win condition: {str(e)}")
            return False

    def on_key_press(self, event):
        """Handle keyboard input"""
        try:
            key = event.keysym.lower()
            
            if key == "w":
                self.move("up")
            elif key == "s":
                self.move("down")
            elif key == "a":
                self.move("left")
            elif key == "d":
                self.move("right")
            elif key == "u":
                self.undo_move()
            elif key == "r":
                self.reset_game()
            elif key == "q":
                if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
                    self.root.quit()
        except Exception as e:
            error_msg = f"Error handling key press: {str(e)}"
            print(error_msg)
            self.status_var.set(error_msg)

    def show_win_message(self):
        """Display win message in a small container below the grid"""
        # Create a small container below the grid
        self.canvas.create_rectangle(150, 520, 350, 550, fill="lightblue", outline="blue", width=2)
        # Display congratulatory message
        self.canvas.create_text(250, 535, text="واو لقد فزت يا شطور", font=("Arial", 14, "bold"), fill="darkblue")

    def draw_player_triangle(self, x1, y1, x2, y2):
        """Draw player as a triangle pointing in the direction of movement"""
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        size = (x2 - x1) // 2 - 5  # Triangle size with some padding
        
        # Define triangle points based on direction
        if self.last_direction == "up":
            # Pointing up: top point at top, base at bottom
            points = [
                center_x, center_y - size,  # Top point
                center_x - size, center_y + size,  # Bottom left
                center_x + size, center_y + size   # Bottom right
            ]
        elif self.last_direction == "down":
            # Pointing down: bottom point at bottom, base at top
            points = [
                center_x, center_y + size,  # Bottom point
                center_x - size, center_y - size,  # Top left
                center_x + size, center_y - size   # Top right
            ]
        elif self.last_direction == "left":
            # Pointing left: left point at left, base at right
            points = [
                center_x - size, center_y,  # Left point
                center_x + size, center_y - size,  # Top right
                center_x + size, center_y + size   # Bottom right
            ]
        elif self.last_direction == "right":
            # Pointing right: right point at right, base at left
            points = [
                center_x + size, center_y,  # Right point
                center_x - size, center_y - size,  # Top left
                center_x - size, center_y + size   # Bottom left
            ]
        else:
            # Default to pointing up if no direction set
            points = [
                center_x, center_y - size,
                center_x - size, center_y + size,
                center_x + size, center_y + size
            ]
        
        # Draw the triangle
        self.canvas.create_polygon(points, fill="white", outline="black", width=2)

    def run_solver(self, solver_func, solver_name):
        """Run a solver and display results"""
        try:
            self.results_text.insert(tk.END, f"Running {solver_name} solver...\n")
            self.results_text.see(tk.END)
            self.root.update_idletasks()
            
            # Run the solver (matching the way it's called in main.py)
            goal_snapshot, generated_count, path = solver_func(self.game)
            
            # Display results
            self.results_text.insert(tk.END, f"\n{solver_name} Results:\n")
            self.results_text.insert(tk.END, f"Generated nodes: {generated_count}\n")
            
            if goal_snapshot is None:
                self.results_text.insert(tk.END, "No solution found within node limit.\n")
            else:
                self.results_text.insert(tk.END, f"Solution found!\n")
                self.results_text.insert(tk.END, f"Path length: {len(path)}\n")
                # Limit path display to first 20 moves to avoid overwhelming the display
                if len(path) > 20:
                    self.results_text.insert(tk.END, f"Path (first 20 moves): {path[:20]}...\n")
                else:
                    self.results_text.insert(tk.END, f"Path: {path}\n")
            
            self.results_text.insert(tk.END, "-" * 50 + "\n")
            self.results_text.see(tk.END)
            self.root.update_idletasks()  # Ensure the text is displayed immediately
        except Exception as e:
            error_msg = f"Error running {solver_name}: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()  # Print full traceback for debugging
            self.results_text.insert(tk.END, error_msg + "\n")
            self.results_text.see(tk.END)

    def run_dfs(self):
        """Run DFS solver"""
        print("DFS button clicked")  # Debug print
        self.run_solver(dfs_solve, "DFS")

    def run_bfs(self):
        """Run BFS solver"""
        print("BFS button clicked")  # Debug print
        self.run_solver(bfs_solve, "BFS")

    def run_astar(self):
        """Run A* solver"""
        print("A* button clicked")  # Debug print
        self.run_solver(astar_solve, "A*")

    def run_ucs(self):
        """Run UCS solver"""
        print("UCS button clicked")  # Debug print
        self.run_solver(ucs_solve, "UCS")


def main():
    try:
        root = tk.Tk()
        app = MathPushGUI(root)
        root.mainloop()
    except Exception as e:
        error_msg = f"Error running application: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        messagebox.showerror("Error", error_msg)


if __name__ == "__main__":
    main()