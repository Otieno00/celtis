def moisture_content(m1, m2, m3):
    moisture = m2 - m3
    dry_mass = m3 - m1
    return moisture, dry_mass, (moisture / dry_mass * 100) if dry_mass else 0


def relative_density_apparent(D, B, C):
    d2 = D - (B - C)
    return D / d2 if d2 else None


def water_absorption(A, D):
    return (A - D) / D * 100 if D else None


def acv(m2, m1):
    return (m2 / m1 * 100) if m1 else 0


def laa_value(m1, m2):
    return ((m1 - m2) / m1 * 100) if m1 else 0


def aiv_dry(m2, m1):
    return (m2 / m1 * 100) if m1 else 0


def aiv_soaked(m2, m1, blows):
    return (m2 / m1 * (15 / blows) * 100) if (m1 and blows) else 0


def flakiness_index(m3, m2):
    return (m3 / m2 * 100) if m2 else 0