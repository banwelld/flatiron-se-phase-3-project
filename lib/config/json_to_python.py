import os
import json

script_dir = os.path.dirname(__file__)

# open navigation operation config file for reading
nav_path = os.path.join(script_dir, "navigation", "config.json")
with open(nav_path, "r", encoding="utf-8") as nav:
    NAV_OPS_CONFIG = json.load(nav)


# open menu operation config file for reading
menu_path = os.path.join(script_dir, "menu", "config.json")
with open(menu_path, "r", encoding="utf-8") as menu:
    MENU_OPS_CONFIG = json.load(menu)


# open primary operations config file for reading
op_path = os.path.join(script_dir, "operation", "config.json")
with open(op_path, "r", encoding="utf-8") as ops:
    OPS_CONFIG = json.load(ops)


# open database config files for reading
db_team_path = os.path.join(script_dir, "database", "team", "config.json")
with open(db_team_path, "r", encoding="utf-8") as team_table:
    TEAM_TABLE_CONFIG = json.load(team_table)


db_participant_path = os.path.join(script_dir, "database", "participant", "config.json")
with open(db_participant_path, "r", encoding="utf-8") as participant_table:
    PARTICIPANT_TABLE_CONFIG = json.load(participant_table)


# open model config files for reading
model_team_path = os.path.join(script_dir, "model", "team", "config.json")
with open(model_team_path, "r", encoding="utf-8") as team_model:
    TEAM_MODEL_CONFIG = json.load(team_model)


model_participant_path = os.path.join(script_dir, "model", "participant", "config.json")
with open(model_participant_path, "r", encoding="utf-8") as participant_model:
    PARTICIPANT_MODEL_CONFIG = json.load(participant_model)


# open text color map config file for reading
col_map_path = os.path.join(script_dir, "text_color_map.json")
with open(col_map_path, "r", encoding="utf-8") as col_map:
    TEXT_COLOR_MAP = json.load(col_map)