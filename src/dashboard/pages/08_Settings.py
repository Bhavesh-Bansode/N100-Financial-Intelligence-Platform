import streamlit as st
import json
from pathlib import Path

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Settings")

# --------------------------------------------------
# SETTINGS FILE
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CONFIG_DIR = PROJECT_ROOT / "src" / "dashboard" / "config"

CONFIG_DIR.mkdir(exist_ok=True)

SETTINGS_FILE = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {

    "theme": "Light",

    "accent": "Blue",

    "font_size": "Medium",

    "show_charts": True,

    "show_metrics": True,

    "show_tables": True,

    "auto_refresh": False,

    "export_format": "CSV",

    "decimal_places": 2

}

# --------------------------------------------------
# LOAD SETTINGS
# --------------------------------------------------

def load_settings():

    if SETTINGS_FILE.exists():

        with open(SETTINGS_FILE, "r") as f:

            return json.load(f)

    return DEFAULT_SETTINGS.copy()


# --------------------------------------------------
# SAVE SETTINGS
# --------------------------------------------------

def save_settings(data):

    with open(SETTINGS_FILE, "w") as f:

        json.dump(data, f, indent=4)


settings = load_settings()

# --------------------------------------------------
# APPEARANCE
# --------------------------------------------------

st.subheader("🎨 Appearance")

theme = st.selectbox(

    "Theme",

    ["Light", "Dark", "System Default"],

    index=["Light","Dark","System Default"].index(
        settings["theme"]
    )

)

accent = st.selectbox(

    "Accent Colour",

    ["Blue","Green","Purple","Orange","Red"],

    index=["Blue","Green","Purple","Orange","Red"].index(
        settings["accent"]
    )

)

font_size = st.selectbox(

    "Font Size",

    ["Small","Medium","Large"],

    index=["Small","Medium","Large"].index(
        settings["font_size"]
    )

)

st.divider()

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

st.subheader("📊 Dashboard")

show_charts = st.toggle(

    "Show Charts",

    value=settings["show_charts"]

)

show_metrics = st.toggle(

    "Show KPI Cards",

    value=settings["show_metrics"]

)

show_tables = st.toggle(

    "Show Tables",

    value=settings["show_tables"]

)

auto_refresh = st.toggle(

    "Auto Refresh",

    value=settings["auto_refresh"]

)

st.divider()

# --------------------------------------------------
# EXPORT
# --------------------------------------------------

st.subheader("📁 Export")

export_format = st.radio(

    "Default Export",

    ["CSV","Excel","PDF"],

    index=["CSV","Excel","PDF"].index(
        settings["export_format"]
    )

)

decimal_places = st.slider(

    "Decimal Places",

    0,

    5,

    settings["decimal_places"]

)

st.divider()

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

st.subheader("🗄 Database")

st.success("Connected")

st.code("SQLite : nifty100.db")

st.divider()

# --------------------------------------------------
# SAVE
# --------------------------------------------------

if st.button(

    "💾 Save Settings",

    use_container_width=True

):

    settings = {

        "theme": theme,

        "accent": accent,

        "font_size": font_size,

        "show_charts": show_charts,

        "show_metrics": show_metrics,

        "show_tables": show_tables,

        "auto_refresh": auto_refresh,

        "export_format": export_format,

        "decimal_places": decimal_places

    }

    save_settings(settings)

    st.success("Settings saved successfully.")

st.divider()

st.subheader("Current Settings")

st.json(load_settings())

st.caption("Settings are stored in config/settings.json")