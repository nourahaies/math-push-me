#main.py
from solver_dfs import dfs_solve    
from solver_astar import astar_solve
from level_loader import load_level
from game import Game
from successor import get_successors


if __name__ == "__main__":
    #level = load_level("levels/level1.json")
    level = load_level("levels/field5.json")
    game = Game(level)

    print("Math Push (Move with W/A/S/D, Q to quit, t to know possible states)\n")

    game.display()

    while True:
        move = input("Move: ").lower()

        if move == "q":
            print("Exiting game...")
            break

        if move == "w":
            game.move_player("up")
        elif move == "s":
            game.move_player("down")
        elif move == "a":
            game.move_player("left")
        elif move == "d":
            game.move_player("right")

        elif move == "u":
            game.undo()  

        elif move == "r":
            game.reset()

        elif move == "t":
            succs = get_successors(game)
            if not succs:
                print("No legal successor states from current position.")
            else:
                for s in succs:
                    print("---- State from action:", s["action"], "----")
                    print("Player:", s["player_pos"])
                    print("Locks:", list(s["locks"].keys()))
                    if s["exprs_solved"]:
                        print("New expressions solved:", s["exprs_solved"])
                    print("Results after move:", s["results"])
                    print("Grid:")
                    for row in s["grid"]:
                        print(" ".join(row))
                    print()
                    print("---------------------------------------------------------------------------------------------")
        elif move == "z":
            print("Running DFS solver... (this may take a while)")
            goal_snapshot, generated_count, path = dfs_solve(game, max_nodes=100000)
            if goal_snapshot is None:
                print("No solution found within node limit.")
                print("Generated nodes:", generated_count)
            else:
                print("Goal found!")
                print("Generated nodes:", generated_count)
                print("Goal player position:", goal_snapshot["player_pos"])
                print("Path length:", len(path))
                print("Path actions:", path)

        elif move == "h":
            print("Running A* solver... (this may take a while)")
            
            goal_snapshot, generated_count, path = astar_solve(game, max_nodes=1000000)
            if goal_snapshot is None:
                print("No solution found within node limit.")
                print("Generated nodes:", generated_count)
            else:
                print("Goal found!")
                print("Generated nodes:", generated_count)
                print("Goal player position:", goal_snapshot["player_pos"])
                print("Path length:", len(path))
                print("Path actions:", path)


        game.display()
