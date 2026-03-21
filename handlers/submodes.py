from core.utils import get_modes_text

async def handle_submodes(update, context) -> None:
    await update.message.reply_text(get_modes_text())
