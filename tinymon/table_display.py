"""
table_display.py

Module for displaying tabular data with ASCII formatting
"""
from termcolor import colored, cprint

def display_table(title, col_names, rows):
    cprint(title, "green")
    print()
    widths = [max([len(col_names[i])]+[len(row[i]) for row in rows]) for i in range(len(col_names))]
    _print_table(col_names, rows, widths)

# Utility function for printing a table
def _print_table(col_names, rows, widths):
    total_width = sum(widths) + 3*(len(widths)-1) + 4

    BAR = colored("|", "blue", attrs=["bold"])
    cprint(f"{BAR} ", end="")
    cprint(f" {BAR} ".join(colored(x, attrs=["bold"]) for x in _justify_all(col_names, widths)),
           attrs=["bold"], end="")
    cprint(f" {BAR}")

    cprint(f"|-", "blue", attrs=["bold"], end="")
    cprint(f"-|-".join("-"*x for x in widths), "blue", attrs=["bold"], end="")
    cprint(f"-|", "blue", attrs=["bold"])

    for row in rows:
        cprint(f"{BAR} ", end="")
        cprint(f" {BAR} ".join(_justify_all(row, widths)), end="")
        cprint(f" {BAR}")

    print()

# Justify all fields in a line to the respective widths
def _justify_all(fields, widths):
    assert len(fields) == len(widths)
    return [fields[i].ljust(widths[i]) for i in range(len(fields))]
