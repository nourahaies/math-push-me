# هذا الملف مسؤول عن اكتشاف وتقييم التعابير الحسابية داخل الخريطة

def scan_expressions(grid):
    """
    يبحث في الخريطة عن جميع التعابير الصحيحة (أفقياً وعمودياً)
    ويعيد قائمة بالنتائج المكتشفة.
    """
    results = []

    rows = len(grid)
    cols = len(grid[0])

    # --- البحث الأفقي ---
    for r in range(rows):
        row = grid[r]
        exprs = extract_expressions_from_line(row)
        results.extend(exprs)

    # --- البحث العمودي ---
    for c in range(cols):
        col = [grid[r][c] for r in range(rows)]
        exprs = extract_expressions_from_line(col)
        results.extend(exprs)

    return results


def extract_expressions_from_line(line):
    """
    تبحث في سطر (قائمة من الخلايا) عن تعابير من الشكل:
    رقم - عملية - رقم - عملية - رقم ...
    """
    results = []
    tokens = []

    for cell in line:
        if cell.isdigit() or cell in ["+", "-"]:
            tokens.append(cell)
        else:
            # نحاول تحليل ما جمعناه حتى الآن
            if tokens:  # Only process if we have tokens
                cleaned = clean_edges(tokens)
                if cleaned is not None and len(cleaned) >= 3:
                    value = evaluate_expression(cleaned)
                    if value is not None:
                        results.append(value)
                tokens = []  # نعيد الضبط عند أول فاصل

    # إذا بقي شيء في النهاية
    if tokens:  # Only process if we have tokens
        cleaned = clean_edges(tokens)
        if cleaned is not None and len(cleaned) >= 3:
            value = evaluate_expression(cleaned)
            if value is not None:
                results.append(value)

    return results


def clean_edges(tokens):
    """تحذف العملية من البداية أو النهاية فقط"""
    if not tokens:
        return None

    # Make a copy to avoid modifying the original
    cleaned_tokens = tokens[:]

    # حذف العملية من البداية
    while cleaned_tokens and cleaned_tokens[0] in ["+", "-"]:
        cleaned_tokens = cleaned_tokens[1:]
        if not cleaned_tokens:
            return None

    # حذف العملية من النهاية
    while cleaned_tokens and cleaned_tokens[-1] in ["+", "-"]:
        cleaned_tokens = cleaned_tokens[:-1]
        if not cleaned_tokens:
            return None

    if len(cleaned_tokens) < 3:
        return None

    return cleaned_tokens


def evaluate_expression(tokens):
    """
    تحسب ناتج تعبير بسيط من الشكل:
    رقم + رقم - رقم ...
    """
    try:
        # Handle empty or too short tokens
        if not tokens or len(tokens) < 3:
            return None
            
        # Handle expressions that start with + or -
        working_tokens = tokens[:]
        if working_tokens[0] in ["+", "-"]:
            # Insert a 0 at the beginning to make it valid
            working_tokens = ["0"] + working_tokens
            
        # Handle expressions that end with + or -
        if working_tokens[-1] in ["+", "-"]:
            # Append a 0 at the end to make it valid
            working_tokens = working_tokens + ["0"]

        # Must start and end with a digit
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
