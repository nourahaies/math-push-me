from level_loader import load_level
from game import Game

if __name__ == "__main__":
    level = load_level("levels/level2.json")
    game = Game(level)

    print("Math Push (Move with W/A/S/D, Q to quit)\n")

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

        game.display()
