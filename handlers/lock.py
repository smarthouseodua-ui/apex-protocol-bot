from core.utils import toggle_server_lock, lock_state_text

async def handle_lock(update, context) -> None:
    result = toggle_server_lock()
    await update.message.reply_text(f"{result}\n\n{lock_state_text()}")
