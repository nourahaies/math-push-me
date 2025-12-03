from copy import deepcopy
from evaluator import scan_expressions

#check expressions on a GameState copy and update results_copy & locks
def _check_expressions_on_state(state, results_copy):
    
    new_exprs = []
    exprs = scan_expressions(state.grid)
    if not exprs:
        return new_exprs

    for value in exprs:
        # if this expr value is new, add to results_copy
        if value not in results_copy:
            results_copy.append(value)
            new_exprs.append(value)
        # open door(s) that match this value (keys like "G5")
        keys_to_remove = []
        for key, (r, c) in list(state.locks.items()):
            if key.startswith("G") and key[1:] == str(value):
                # open door on grid and mark key for removal
                state.grid[r][c] = "."
                keys_to_remove.append(key)
        for k in keys_to_remove:
            state.locks.pop(k, None)

    return new_exprs


def _simulate_move_state(state, results_copy, direction):
   
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
        return None

    pr, pc = state.player_pos
    new_r, new_c = pr + dr, pc + dc

    target_cell = state.get_cell(new_r, new_c)

    # invalid move (wall or outside)
    if target_cell is None or target_cell == "#":
        return None

    # If target is Finish "F"
    if target_cell == "F":
        # if there are still locks -> can't move
        if state.locks:
            return None
        else:
            # move player
            state.grid[pr][pc] = "."
            state.grid[new_r][new_c] = "P"
            state.player_pos = (new_r, new_c)
            # check expressions after move
            newly = _check_expressions_on_state(state, results_copy)
            return {
                "action": f"move_{direction}",
                "grid": deepcopy(state.grid),
                "player_pos": state.player_pos,
                "locks": deepcopy(state.locks),
                "results": list(results_copy),
                "exprs_solved": newly
            }

    # If target is empty
    if target_cell == ".":
        state.grid[pr][pc] = "."
        state.grid[new_r][new_c] = "P"
        state.player_pos = (new_r, new_c)
        newly = _check_expressions_on_state(state, results_copy)
        return {
            "action": f"move_{direction}",
            "grid": deepcopy(state.grid),
            "player_pos": state.player_pos,
            "locks": deepcopy(state.locks),
            "results": list(results_copy),
            "exprs_solved": newly
        }

    # If target is pushable (digit or + or -)
    if (isinstance(target_cell, str) and (target_cell.isdigit() or target_cell in ["+", "-"])):
        # collect contiguous pushable blocks in that direction
        movable_blocks = []
        r, c = new_r, new_c
        while True:
            cell = state.get_cell(r, c)
            if cell and (cell.isdigit() or cell in ["+", "-"]):
                movable_blocks.append((r, c, cell))
                r += dr
                c += dc
            else:
                break

        next_cell = state.get_cell(r, c)
        # can only push if the cell after the sequence is empty
        if next_cell == ".":
            # push blocks (from furthest to nearest)
            for (br, bc, val) in reversed(movable_blocks):
                state.grid[br + dr][bc + dc] = val
                state.grid[br][bc] = "."
            # move player into first block's spot
            state.grid[pr][pc] = "."
            state.grid[new_r][new_c] = "P"
            state.player_pos = (new_r, new_c)
            newly = _check_expressions_on_state(state, results_copy)
            return {
                "action": f"move_{direction}_push",
                "grid": deepcopy(state.grid),
                "player_pos": state.player_pos,
                "locks": deepcopy(state.locks),
                "results": list(results_copy),
                "exprs_solved": newly
            }
        else:
            # cannot push (no free space)
            return None

    # otherwise not a recognized cell type => invalid
    return None


def get_successors(game):
    """
    Given your Game instance, return list of possible successor states (full snapshots).
    Each successor is a dict with keys:
      - action: 'move_up' / 'move_left' / etc.
      - grid: deep-copied grid after the simulated move
      - player_pos: (r,c)
      - locks: dict of remaining locks
      - results: list of discovered results after the move
      - exprs_solved: list of new expression values solved by this move
    """
    successors = []
    directions = ["up", "down", "left", "right"]

    for d in directions:
        # deep copy the state and results, simulate on the copy
        state_copy = deepcopy(game.state)
        results_copy = deepcopy(game.results)
        succ = _simulate_move_state(state_copy, results_copy, d)
        if succ:
            successors.append(succ)

    return successors
