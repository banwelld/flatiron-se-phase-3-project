# user action sentinels

USER_CANCEL = object()
USER_CLEAR = object()
PROCESS_CANCEL = object()

def is_cancelled(value: any) -> object:
    """
    If value is a sentinel, returns the sentinel. If value is not a sentinel, returns None.
    """
    return value if value in (USER_CANCEL, USER_CLEAR, PROCESS_CANCEL) else None
