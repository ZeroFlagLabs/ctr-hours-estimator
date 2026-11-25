def calculate_total_hours(
    new_pn_qty, new_pn_hrs,
    rev_pn_qty, rev_pn_hrs,
    new_dwg_qty, new_dwg_hrs,
    rev_dwg_qty, rev_dwg_hrs,
    additional_hours
):
    total = (
        new_pn_qty * new_pn_hrs +
        rev_pn_qty * rev_pn_hrs +
        new_dwg_qty * new_dwg_hrs +
        rev_dwg_qty * rev_dwg_hrs +
        additional_hours
    )
    return total


def calculate_employees(total_hours, weeks, hours_per_week=37.5, efficiency=0.8):
    if weeks <= 0:
        raise ValueError("Weeks must be greater than zero.")

    effective_hours = hours_per_week * efficiency
    fte = total_hours / (weeks * effective_hours)

    return fte