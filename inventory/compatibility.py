"""
Compatibility engine.

Checks whether a set of selected components can work together.
Three rules only:
  1. CPU socket must match the motherboard socket.
  2. RAM generation must match what the motherboard supports.
  3. Total wattage must not exceed 85% of the PSU's rated wattage.
"""

# Safety margin: never load a PSU beyond 85% of its rating.
PSU_HEADROOM = 0.85


def _first(products, category_name):
    """Return the first selected product of a given category, or None."""
    for product in products:
        if product.category.name == category_name:
            return product
    return None


def _all(products, category_name):
    """Return every selected product of a given category."""
    return [p for p in products if p.category.name == category_name]


def check_socket(products):
    """Rule 1 — the CPU must fit the motherboard's socket."""
    cpu = _first(products, "CPU")
    board = _first(products, "Motherboard")

    if not cpu or not board:
        return None  # cannot check without both parts

    cpu_socket = cpu.attributes.get("socket")
    board_socket = board.attributes.get("socket")

    if cpu_socket != board_socket:
        return (
            f"Socket mismatch: the CPU uses {cpu_socket} but the "
            f"motherboard uses {board_socket}."
        )
    return None


def check_ram_generation(products):
    """Rule 2 — the RAM generation must match the motherboard."""
    board = _first(products, "Motherboard")
    ram_sticks = _all(products, "RAM")

    if not board or not ram_sticks:
        return None

    board_gen = board.attributes.get("ddr_gen")

    for ram in ram_sticks:
        ram_gen = ram.attributes.get("ddr_gen")
        if ram_gen != board_gen:
            return (
                f"RAM mismatch: {ram.name} is {ram_gen} but the "
                f"motherboard supports {board_gen}."
            )
    return None


def check_power(products):
    """Rule 3 — the PSU must supply the total load with headroom to spare."""
    psu = _first(products, "PSU")

    if not psu:
        return None

    psu_watts = psu.attributes.get("wattage", 0)

    # Add up everything except the PSU itself.
    total_watts = 0
    for product in products:
        if product.category.name == "PSU":
            continue
        total_watts += product.attributes.get("wattage", 0)

    usable_watts = psu_watts * PSU_HEADROOM

    if total_watts > usable_watts:
        return (
            f"Insufficient power: the components draw {total_watts}W but the "
            f"{psu_watts}W PSU can safely supply only {usable_watts:.0f}W "
            f"(85% of its rating)."
        )
    return None


def check_compatibility(products):
    """
    Run all three rules against the selected products.

    Returns a dictionary:
        {
          "compatible": True/False,
          "errors": [list of readable error messages],
          "total_wattage": int
        }
    """
    errors = []

    for rule in (check_socket, check_ram_generation, check_power):
        problem = rule(products)
        if problem:
            errors.append(problem)

    total_watts = sum(
        p.attributes.get("wattage", 0)
        for p in products
        if p.category.name != "PSU"
    )

    return {
        "compatible": len(errors) == 0,
        "errors": errors,
        "total_wattage": total_watts,
    }
