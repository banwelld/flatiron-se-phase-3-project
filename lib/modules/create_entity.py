import sys
from pathlib import Path
from typing import Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.participant import Participant
from models.team import Team
from util.helpers import fmt_participant_name, generate_disp_text
from modules.get_confirmation import get_confirmation
from modules.get_attr_value import get_attr_value
from modules.user_sentinels import USER_CANCEL


# user input collection and validation


def collect_user_responses(model_type: str, attr_config: dict) -> Union[str, object]:
    collection = {}

    for key, val in attr_config.items():
        attr_value = get_attr_value(model_type, val, val.get("display_text"))
        collection[key] = attr_value

    return collection


def collect_instantiation_data(
    model: Union[Participant, Team], model_type: str
) -> dict:
    attr_config = generate_attr_config(model)
    return collect_user_responses(model_type, attr_config)


# utility functions


def generate_attr_config(model: Union[Participant, Team]) -> dict:
    """
    Generates a dictionary of attributes required for the instantiation of a model.
    """
    required_attrs = {
        attr_name: attr_val
        for attr_name, attr_val in model.CONFIG.items()
        if attr_val["req_for_initialization"]
    }
    return required_attrs


# control flow


def create_entity(model: Union[Participant, Team]) -> Union[Participant, Team]:
    """
    Collects data necessary for instantiating a participant or team, gets user confirmation
    and - if the user chooses "y" - instantiates the entity. If user selects "n" in the
    confirmation process or hits CRTL + C returns the escape sentinel to cancel the
    operation immediately.
    """
    try:
        model_type = model.__name__.lower()
        attr_values = collect_instantiation_data(model, model_type)

        if model_type == "participant":
            entity_name = fmt_participant_name(
                attr_values.get("first_name"), attr_values.get("last_name")
            )
            entity_disp_name = generate_disp_text(entity_name)
        else:
            entity_disp_name = generate_disp_text(attr_values.get("name"))

        if not get_confirmation(f"Create {model_type}: {entity_disp_name}?"):
            return USER_CANCEL

        return model.create(**attr_values)

    except KeyboardInterrupt:
        return USER_CANCEL
