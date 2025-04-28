import sys
from pathlib import Path
from typing import Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.participant import Participant
from models.team import Team
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
        attr_name: value
        for attr_name, value in model.CONFIG.items()
        if value["required"]
    }
    return required_attrs


def get_entity_name(model: Union[Participant, Team], attr_values: dict) -> str:
    if model == Participant:
        return " ".join((attr_values["first_name"], attr_values["last_name"]))
    return attr_values.get("name")


# runner function

def create_entity(model: Union[Participant, Team]) -> Union[Participant, Team]:
    """
    Collects data necessary for instantiating a participant or team, gets user confirmation
    and - if the user chooses "y" - instantiates the entity. If user selects "n" in the
    confirmation process or hits CRTL + C returns the escape sentinel to cancel the
    operation immediately.
    """
    from cli import selected_entities
    try:
        model_type = model.__name__.lower()
        attr_values = collect_instantiation_data(model, model_type)
        entity_name = get_entity_name(model, attr_values)

        if not get_confirmation(f"Create {model_type}: {entity_name}?"):
            selected_entities.reset()
            return USER_CANCEL

        return model.create(**attr_values)

    except KeyboardInterrupt:
        return USER_CANCEL


#  test setup

if __name__ == "__main__":
    test_entity = create_entity(Participant, object())
    print(test_entity.first_name, test_entity.last_name, test_entity.birth_date)
