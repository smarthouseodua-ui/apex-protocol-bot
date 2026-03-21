from core.utils import get_services_text

async def handle_services(update, context) -> None:
    await update.message.reply_text(get_services_text())
