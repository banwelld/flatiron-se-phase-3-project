import sys
from pathlib import Path
from typing import Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.participant import Participant
from models.team import Team
from modules.get_attr_value import get_attr_value
from modules.get_confirmation import get_confirmation
from modules.user_sentinels import USER_CANCEL
from util.helpers import generate_disp_text


# utility functions


def update_attr_and_persist(
    entity: Union[Participant, Team], attr_name: str, new_value: str
):
    """
    Updates the attribute of the team or participant instance passed in as 'entity' with a new value.
    """
    setattr(entity, attr_name, new_value)
    entity.update()


# operational control flow


def update_entity(entity: Union[Participant, Team], attr_name: str) -> None:
    try:
        model = type(entity)
        model_type = model.__name__.lower()
        attr_config = model.CONFIG.get(attr_name)
        attr_disp_text = attr_config.get("display_text")

        new_value = get_attr_value(model_type, attr_config, attr_disp_text)
        new_value_disp_text = generate_disp_text(new_value)

        if not get_confirmation(
            f"Update {model_type} {attr_disp_text} to {new_value_disp_text}?"
        ):
            from cli import selected_entities

            selected_entities.reset()
            return USER_CANCEL

        update_attr_and_persist(entity, attr_name, new_value)

    except KeyboardInterrupt:
        return USER_CANCEL
