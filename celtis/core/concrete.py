import math


def compressive_mpa(cube_mm, load_kn):
    return (load_kn * 1000) / (cube_mm ** 2)


def slump_mm(initial_mm, final_mm):
    return initial_mm - final_mm


def slump_class(slump):
    if slump < 25:  return "Very Low"
    if slump < 50:  return "Low"
    if slump < 100: return "Medium"
    if slump < 175: return "High"
    return "Very High / Collapsed"


def flexural_mpa(width_mm, depth_mm, span_mm, load_kn):
    b, d, L, P = width_mm / 1000, depth_mm / 1000, span_mm / 1000, load_kn * 1000
    return (P * L) / (b * d ** 2) / 1e6


def split_tensile_mpa(diameter_mm, length_mm, load_kn):
    return (2 * load_kn * 1000) / (math.pi * diameter_mm * length_mm)


def cube_strength_mpa(load_kn, area_mm2):
    return (load_kn * 1000) / area_mm2