import functools
from models.participant.config import config as participant_config
from models.team.config import config as team_config


def validation_config(model: str, attrib_name: str):
    if model == "participant":
        attrib = participant_config[attrib_name]
    elif model == "team":
        attrib = team_config[attrib_name]
    else:
        raise ValueError(
            f"Unexpteced class type '{model}'. Expected 'participant' or 'team."
        )
    return attrib["validation"]


def validate_name(entity_name: str, attrib_name: str):
    """
    Decorator to validate a name setter.
    """

    def decorator(setter):
        @functools.wraps(setter)
        def wrapper(self, value):
            from util.validation.enforcers import enforce_range
            from util.validation.enforcers import enforce_valid_chars

            constraints = validation_config(entity_name, attrib_name)
            enforce_range(
                len(value), constraints["min_length"], constraints["max_length"]
            )
            enforce_valid_chars(value, constraints["regex"])
            return setter(self, value)

        return wrapper

    return decorator


def validate_date(entity_name: str, attrib_name: str):
    """
    Decorator to validate a date setter.
    """

    def decorator(setter):
        @functools.wraps(setter)
        def wrapper(self, value):
            from util.validation.enforcers import enforce_valid_date

            constraints = validation_config(entity_name, attrib_name)
            enforce_valid_date(value, constraints["regex"])
            return setter(self, value)

        return wrapper

    return decorator
