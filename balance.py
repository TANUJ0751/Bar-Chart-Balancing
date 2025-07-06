def balance_values(values, step, mode, max_iterations=100):
    """
    Recursively balance values between dynamic min and max line using given mode.
    Modes: 'add', 'subtract', 'both'
    """
    values = values[:]  # clone input list

    for _ in range(max_iterations):
        avg = sum(values) / len(values)
        max_line = (max(values) + avg) / 2
        min_line = (min(values) + avg) / 2

        updated = False
        for i, val in enumerate(values):
            if mode == 'add' and val < avg:
                values[i] = min(val + step, max_line)
                updated = True
            elif mode == 'subtract' and val > avg:
                values[i] = max(val - step, min_line)
                updated = True
            elif mode == 'both':
                if val < avg:
                    values[i] = min(val + step, max_line)
                    updated = True
                elif val > avg:
                    values[i] = max(val - step, min_line)
                    updated = True

        if not updated:
            break

    return [round(v, 2) for v in values]
