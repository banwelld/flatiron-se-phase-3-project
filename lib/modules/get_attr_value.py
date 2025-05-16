import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from util.helpers import get_input_with_prompt
from validation.frontend import validate_date, validate_name


def validate_attr_value_response(attr_config: dict, response: str) -> bool:
    data_type = attr_config["validation"]["validate_as"]
    if data_type == "name":
        return validate_name(attr_config, response)
    if data_type == "date":
        return validate_date(attr_config, response)


def prompt_for_attr_value(model_type: str, attr_display_text: str) -> str:
    prompt_text = f"{model_type.title()} {attr_display_text}: "
    return get_input_with_prompt(prompt_text)


def main(model_type: str, attr_config: dict, back_sentinel: object) -> str:
    try:
        response = ""
        attr_disp_text = attr_config.get("display_text")
        exit_loop = False
        while not exit_loop:
            response = prompt_for_attr_value(model_type, attr_disp_text)
            exit_loop = validate_attr_value_response(attr_config, response)
        return response

    except KeyboardInterrupt:
        return back_sentinel
