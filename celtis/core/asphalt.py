def bitumen_content(A, B, C, D):
    """All in grams. Returns (E, F, G, H%) or None."""
    E = D - C
    F = B + E
    G = A - F
    H = (G / F * 100) if F > 0 else 0
    return E, F, G, H


def air_voids(gmm, gmb):
    if not gmm:
        return None
    return (gmm - gmb) / gmm * 100


def core_density_water(air, water, soak):
    vol = soak - water
    return (air / vol if vol > 0 else None), vol


def spray_rate(tray_bit, tray_wt, density, tray_area):
    bit = tray_bit - tray_wt
    if bit <= 0 or density <= 0 or tray_area <= 0:
        return None, None, None
    vol = bit / density
    return bit, vol, vol / tray_area


def specific_gravity(dry, under, sat):
    vol = sat - under
    if vol <= 0 or dry <= 0:
        return None, None, vol
    return dry / vol, (sat - dry) / dry * 100, vol


def gmm_theoretical(A, B, C, K):
    """A=dry sample, B=jar+water, C=jar+sample+water, K=temp correction."""
    denom = A + B - C
    return (K * A / denom) if denom else None