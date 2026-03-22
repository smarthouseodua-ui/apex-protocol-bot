from core.lock import is_locked
from core.actions import lock_system, unlock_system


async def handle_lock(update, context) -> None:
    user = update.effective_user
    username = user.username if user and user.username else "system"

    if is_locked():
        result = unlock_system(by=username, reason="manual unlock via telegram")
        await update.message.reply_text(
            "🔓 SERVER UNLOCKED\n\n"
            f"STATE: {result['state'].get('mode')}\n"
            f"{result['lock']}"
        )
    else:
        result = lock_system(by=username, reason="manual lock via telegram")
        await update.message.reply_text(
            "🔒 SERVER LOCKED\n\n"
            f"STATE: {result['state'].get('mode')}\n"
            f"{result['lock']}"
        )
