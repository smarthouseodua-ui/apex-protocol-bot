from core.config import ALLOWED_USER_ID

def is_allowed(user_id: int | None) -> bool:
    if user_id is None:
        return False
    return ALLOWED_USER_ID == 0 or user_id == ALLOWED_USER_ID
