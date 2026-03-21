from core.utils import get_status_text

async def handle_status(update, context) -> None:
    await update.message.reply_text(get_status_text())
