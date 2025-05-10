# user action sentinels

USER_BACK = object()
USER_RESET = object()
USER_QUIT = object
PROCESS_CANCEL = object()


def is_cancelled(value: any) -> object:
    """
    If value is a sentinel, returns the sentinel. If value is not a sentinel, returns None.
    """
    return (
        value if value in (USER_BACK, USER_RESET, USER_QUIT, PROCESS_CANCEL) else None
    )
