
def scan_expressions(grid):
    
    results = []

    rows = len(grid)
    cols = len(grid[0])

    #   أفقي 
    for r in range(rows):
        row = grid[r]
        exprs = extract_expressions_from_line(row)
        results.extend(exprs)

    #   عمودي 
    for c in range(cols):
        col = [grid[r][c] for r in range(rows)]
        exprs = extract_expressions_from_line(col)
        results.extend(exprs)

    return results


def extract_expressions_from_line(line):
    
    results = []
    tokens = []

    for cell in line:
        if cell.isdigit() or cell in ["+", "-"]:
            tokens.append(cell)
        else:

            if tokens:  
                cleaned = clean_edges(tokens)
                if cleaned is not None and len(cleaned) >= 3:
                    value = evaluate_expression(cleaned)
                    if value is not None:
                        results.append(value)
                tokens = []  

    
    if tokens:  
        cleaned = clean_edges(tokens)
        if cleaned is not None and len(cleaned) >= 3:
            value = evaluate_expression(cleaned)
            if value is not None:
                results.append(value)

    return results


def clean_edges(tokens):
    
    if not tokens:
        return None

    
    cleaned_tokens = tokens[:]

    
    while cleaned_tokens and cleaned_tokens[0] in ["+", "-"]:
        cleaned_tokens = cleaned_tokens[1:]
        if not cleaned_tokens:
            return None

    
    while cleaned_tokens and cleaned_tokens[-1] in ["+", "-"]:
        cleaned_tokens = cleaned_tokens[:-1]
        if not cleaned_tokens:
            return None

    if len(cleaned_tokens) < 3:
        return None

    return cleaned_tokens


def evaluate_expression(tokens):

    try:
        
        if not tokens or len(tokens) < 3:
            return None
            
        
        working_tokens = tokens[:]
        if working_tokens[0] in ["+", "-"]:
            
            working_tokens = ["0"] + working_tokens
            
        
        if working_tokens[-1] in ["+", "-"]:
            
            working_tokens = working_tokens + ["0"]

        
        if not working_tokens[0].isdigit() or not working_tokens[-1].isdigit():
            return None

        result = int(working_tokens[0])
        i = 1
        while i < len(working_tokens) - 1:
            op = working_tokens[i]
            num = working_tokens[i + 1]

            if not num.isdigit():
                return None

            if op == "+":
                result += int(num)
            elif op == "-":
                result -= int(num)
            else:
                return None

            i += 2

        return result
    except:
        return None
