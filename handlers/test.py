from core.utils import get_test_text

async def handle_test(update, context) -> None:
    await update.message.reply_text(get_test_text())
