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
            if len(tokens) >= 3:
                value = evaluate_expression(tokens)
                if value is not None:
                    results.append(value)
            tokens = []  # نعيد الضبط عند أول فاصل
    # إذا بقي شيء في النهاية
    if len(tokens) >= 3:
        value = evaluate_expression(tokens)
        if value is not None:
            results.append(value)

    return results


def evaluate_expression(tokens):
    """
    تحسب ناتج تعبير بسيط من الشكل:
    رقم + رقم - رقم ...
    """
    try:
        # يجب أن تبدأ وتنتهي برقم
        if not tokens[0].isdigit() or not tokens[-1].isdigit():
            return None

        result = int(tokens[0])
        i = 1
        while i < len(tokens) - 1:
            op = tokens[i]
            num = tokens[i + 1]
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
    except Exception:
        return None
