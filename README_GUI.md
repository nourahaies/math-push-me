# Math Push Game - GUI Version

This is a graphical interface version of the Math Push game using tkinter.

## How to Run

1. Make sure you have Python installed (Python 3.6 or higher)
2. Run the GUI version with:
   ```
   python gui_game.py
   ```

## Game Controls

- **W/A/S/D** keys: Move the player up/left/down/right
- **Arrow buttons** on screen: Alternative way to move
- **U** key or **Undo** button: Undo the last move
- **R** key or **Reset** button: Reset the level to initial state
- **Q** key: Quit the game

## Game Elements

- **Blue circle (P)**: Player
- **Gray cells (#)**: Walls (cannot be moved through)
- **Red squares (Gx)**: Locks that open when expression evaluates to x
- **Green square (F)**: Finish point (win condition)
- **Numbers (0-9)**: Movable blocks
- **Operators (+, -)**: Movable blocks

## How to Play

1. Move the player (blue circle) to push number and operator blocks
2. When a valid mathematical expression is formed (e.g., 3+2 or 5-1), it will be evaluated
3. If the result matches a lock (Gx where x is the result), that lock will open
4. Reach the finish point (green square) when all locks are open to win

## Levels

- **Level 1**: Simple level with one lock (G5)
- **Level 2**: More complex level with two locks (G5 and G1)

## Requirements

- Python 3.6+
- tkinter (usually comes with Python)

Note: This GUI version was created as an alternative to pygame since there were installation issues with pygame on Python 3.14.