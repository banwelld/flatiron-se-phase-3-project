import sys
from pathlib import Path
from typing import Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from util.helpers import get_user_input_std
from validation.frontend import validate_date, validate_name


def validate_attr_value_response(
    attr_display_name: str, attr_config: dict, response: str
):
    data_type = attr_config["validation"]["validate_as"]

    if data_type == "name":
        return validate_name(attr_config, response)

    if data_type == "date":
        return validate_date(attr_config, response)


def prompt_for_attr_value(
    model_type: str, attr_display_text: str
) -> Union[str, object]:
    prompt_text = f"{model_type.title()} {attr_display_text}: "
    return get_user_input_std(prompt_text)


# runner function

def get_attr_value(
    model_type: str, attr_config: dict, display_text: str
) -> Union[str, object]:
    response = ""

    exit_loop = False

    while not exit_loop:
        response = prompt_for_attr_value(model_type, display_text)
        exit_loop = validate_attr_value_response(display_text, attr_config, response)

    return response
