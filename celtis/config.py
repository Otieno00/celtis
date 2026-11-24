"""Central configuration: constants, colours, DB schema."""
APP_NAME    = "Civil Engineering Laboratory Tests Information System"
APP_VERSION = "1.0"
APP_TITLE   = f"{APP_NAME} v {APP_VERSION}"
DB_FILENAME = "civil_engineering_lab.db"
WINDOW_SIZE = "1450x900"

FONT        = "Times New Roman"
ENTRY_FONT  = (FONT, 12)
BOLD_FONT   = (FONT, 12, "bold")
SMALL_FONT  = (FONT, 10)
SMALL_BOLD  = (FONT, 10, "bold")
ITALIC_FONT = (FONT, 12, "italic")


class C:
    CALC    = "#d4edda"
    YELLOW  = "#fffacd"
    HDR     = "#cce5ff"
    GREEN   = "#e2efda"
    BLUE    = "#dce6f1"
    RED     = "#c0392b"
    PRIMARY = "#2c3e50"
    SUCCESS = "#27ae60"
    DANGER  = "#e74c3c"
    WARNING = "#f39c12"


SCHEMA = [
    """CREATE TABLE IF NOT EXISTS concrete_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT, test_name TEXT,
        sample_id TEXT, date TEXT, cube_dimension REAL,
        load_failure REAL, age_days INTEGER, compressive_strength REAL,
        result_status TEXT, technician TEXT, notes TEXT)""",
    """CREATE TABLE IF NOT EXISTS soil_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT, test_name TEXT,
        sample_id TEXT, date TEXT, moisture_content REAL,
        liquid_limit REAL, plastic_limit REAL, plasticity_index REAL,
        soil_classification TEXT, technician TEXT, notes TEXT)""",
    """CREATE TABLE IF NOT EXISTS asphalt_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT, test_name TEXT,
        sample_id TEXT, date TEXT, stability REAL, flow REAL,
        bulk_density REAL, marshall_quotient REAL, result_status TEXT,
        technician TEXT, notes TEXT)""",
    """CREATE TABLE IF NOT EXISTS aggregate_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT, test_name TEXT,
        sample_id TEXT, date TEXT, initial_weight REAL,
        final_weight REAL, crushing_value REAL, abrasion_value REAL,
        specific_gravity REAL, water_absorption REAL,
        result_status TEXT, technician TEXT, notes TEXT)""",
    """CREATE TABLE IF NOT EXISTS test_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT, stored_at TEXT,
        category TEXT, label TEXT, data_json TEXT)""",
]