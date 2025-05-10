import sys
from pathlib import Path
from typing import Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.participant import Participant
from models.team import Team
from modules.get_attr_value import get_attr_value
from util.nav_sentinels import USER_BACK


def main(
    entity: Union[Participant, Team], attr_name: str, value: str = None
) -> Union[Participant, Team]:
    try:
        new_value = value

        if not value:
            model = type(entity)
            model_type = model.__name__.lower()
            attr_config = model.CONFIG.get(attr_name)
            attr_disp_text = attr_config.get("display_text")
            new_value = get_attr_value(model_type, attr_config, attr_disp_text)

        setattr(entity, attr_name, new_value)

        return entity

    except KeyboardInterrupt:
        return USER_BACK
