import numpy as np


# --- Atterberg ---
def moisture_content(wet_wt, dry_wt, tin_wt):
    dry_soil = dry_wt - tin_wt
    if dry_soil <= 0:
        return None
    return (wet_wt - dry_wt) / dry_soil * 100


def liquid_limit_from_cone(cones, mcs):
    """Interpolate LL at 20 mm cone penetration."""
    if not cones:
        return None, None
    for c, mc in zip(cones, mcs):
        if abs(c - 20.0) <= 0.2:
            return mc, None
    if len(cones) == 1:
        return mcs[0], None
    pts = [(c, m) for c, m in zip(cones, mcs) if 15 <= c <= 25]
    pts = pts if len(pts) >= 2 else list(zip(cones, mcs))
    c_arr, m_arr = zip(*pts)
    coeffs = np.polyfit(c_arr, m_arr, 1)
    return float(np.polyval(coeffs, 20)), coeffs


def plasticity_index(ll, pl):
    return None if (ll is None or pl is None) else ll - pl


def linear_shrinkage(initial_mm, final_mm):
    if not initial_mm:
        return None
    return 100 * (1 - final_mm / initial_mm)


# --- Compaction ---
def dry_density_kgm3(wet_mass_g, volume_cm3, moisture_pct):
    bulk = wet_mass_g / volume_cm3
    return bulk * 1000 / (1 + moisture_pct / 100)


def proctor_fit(moistures, dry_densities):
    coeffs = np.polyfit(moistures, dry_densities, 2)
    omc = float(-coeffs[1] / (2 * coeffs[0]))
    mdd = float(np.polyval(coeffs, omc))
    return omc, mdd, coeffs


# --- CBR ---
def cbr_dry_density(wt_mould, wt_wet, volume_l, moisture_pct):
    wet_soil = wt_wet - wt_mould
    bulk = (wet_soil / volume_l) * 1000
    return bulk / (1 + moisture_pct / 100)


def cbr_percent(dial_reading, ring_factor, standard_load):
    return (dial_reading * ring_factor) / standard_load * 100


def cbr_interp_at_95mdd(mdd, dry_densities, cbr_values):
    if not dry_densities or not cbr_values:
        return None
    target = mdd * 0.95
    pairs = sorted(zip(dry_densities, cbr_values))
    for (d1, c1), (d2, c2) in zip(pairs, pairs[1:]):
        if (d1 <= target <= d2) or (d2 <= target <= d1):
            if d2 - d1:
                return c1 + (target - d1) / (d2 - d1) * (c2 - c1)
            return c1
    for d, c in pairs:
        if abs(d - target) < 1:
            return c
    return None