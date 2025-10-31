# parameters/belasting_2025.py
BELASTING_SCHIJVEN = [
    (10570, 0.00),
    (15200, 0.25),
    (26830, 0.40),
    (46440, 0.45),
    (float('inf'), 0.50)
]
def bereken_personenbelasting(belastbaar_inkomen: float) -> float:
    belasting = 0.0
    vorige = 0.0
    for grens, tarief in BELASTING_SCHIJVEN:#een for-loop die over de schijven gaat
        deel = min(belastbaar_inkomen, grens) - vorige
        if deel > 0:
            belasting += deel * tarief
        if belastbaar_inkomen <= grens:
            break
        vorige = grens
    return round(belasting + 1e-9, 2)
