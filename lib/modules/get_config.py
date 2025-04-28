import json
from pathlib import Path


config_filepath = Path(__file__).parent.parent / "config"


# open navigation operation config file for reading

nav_filepath = config_filepath / "navigation" / "config.json"

with nav_filepath.open("r", encoding="utf-8") as nav:
    NAV_OPS_CONFIG = json.load(nav)


# open menu operation config file for reading

menu_filepath = config_filepath / "menu" / "config.json"

with menu_filepath.open("r", encoding="utf-8") as menu:
    MENU_OPS_CONFIG = json.load(menu)


# open primary operations config file for reading

ops_filepath = config_filepath / "operation" / "config.json"

with ops_filepath.open("r", encoding="utf-8") as ops:
    OPS_CONFIG = json.load(ops)


# open database config files for reading

team_table_filepath = config_filepath / "database" / "team" / "config.json"

with team_table_filepath.open("r", encoding="utf-8") as team_table:
    TEAM_TABLE_CONFIG = json.load(team_table)


participant_table_filepath = (
    config_filepath / "database" / "participant" / "config.json"
)

with participant_table_filepath.open("r", encoding="utf-8") as participant_table:
    PARTICIPANT_TABLE_CONFIG = json.load(participant_table)


# open model config files for reading

team_model_filepath = config_filepath / "model" / "team" / "config.json"

with team_model_filepath.open("r", encoding="utf-8") as team_model:
    TEAM_MODEL_CONFIG = json.load(team_model)


participant_model_filepath = config_filepath / "model" / "participant" / "config.json"

with participant_model_filepath.open("r", encoding="utf-8") as participant_model:
    PARTICIPANT_MODEL_CONFIG = json.load(participant_model)
