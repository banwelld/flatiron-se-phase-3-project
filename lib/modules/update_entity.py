import sys
from pathlib import Path
from typing import Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.participant import Participant
from models.team import Team
from modules.get_attr_value import get_attr_value
from modules.get_confirmation import get_confirmation
from modules.user_sentinels import USER_CANCEL


# utility functions

def update_attr_and_persist(
    entity: Union[Participant, Team], attr_name: str, new_value: str
):
    """
    Updates the attribute of the team or participant instance passed in as 'entity' with a new value.
    """
    setattr(entity, attr_name, new_value)
    entity.update()


# runner function

def update_entity(entity: Union[Participant, Team], attr_name: str) -> None:
    try:
        model = type(entity)
        model_type = model.__name__.lower()
        attr_config = model.CONFIG.get(attr_name)
        display_text = attr_config.get("display_text")

        new_value = get_attr_value(model_type, attr_config, display_text)

        if not get_confirmation(f"Update {model_type} {display_text} to {new_value}?"):
            return USER_CANCEL

        update_attr_and_persist(entity, attr_name, new_value)

    except KeyboardInterrupt:
        return USER_CANCEL


# test setup

if __name__ == "__main__":
    new_participant = Participant("John", "Doe", "1999-09-09")
    update_entity(new_participant, Participant, "first_name", object())
    print(
        "\n",
        new_participant.first_name,
        new_participant.last_name,
        new_participant.birth_date,
    )
