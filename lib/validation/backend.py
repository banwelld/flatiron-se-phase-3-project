import functools


def validation_config(model_type: str, attr_name: str):
    from models.participant import Participant
    from models.team import Team

    if model_type == "participant":
        attr = Participant.CONFIG.get(attr_name)
    elif model_type == "team":
        attr = Team.CONFIG.get(attr_name)
    else:
        raise ValueError(
            f"Unexpteced class type '{model_type}'. Expected 'participant' or 'team."
        )
    return attr.get("validation", "Validation type missing")


def validate_name(entity_name: str, attr_name: str):
    """
    Decorator to validate a name setter.
    """

    def decorator(setter):
        @functools.wraps(setter)
        def wrapper(self, value):
            from validation.enforcers import enforce_range
            from validation.enforcers import enforce_valid_chars

            constraints = validation_config(entity_name, attr_name)
            enforce_range(
                len(value), constraints.get("min_length"), constraints.get("max_length")
            )
            enforce_valid_chars(value, constraints.get("regex"))
            return setter(self, value)

        return wrapper

    return decorator


def validate_date(entity_name: str, attr_name: str):
    """
    Decorator to validate a date setter.
    """

    def decorator(setter):
        @functools.wraps(setter)
        def wrapper(self, value):
            from validation.enforcers import enforce_valid_date

            constraints = validation_config(entity_name, attr_name)
            enforce_valid_date(value, constraints.get("regex"))
            return setter(self, value)

        return wrapper

    return decorator
