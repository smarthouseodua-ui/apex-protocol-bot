from core.state import load_state
from core.lock import is_locked


async def handle_test(update, context) -> None:
    state = load_state()
    locked = is_locked()

    text = (
        "🧪 TEST OK\n\n"
        "BOT: ONLINE\n"
        f"STATE: {state.get('mode')}\n"
        f"LOCK: {'ON' if locked else 'OFF'}"
    )

    await update.message.reply_text(text)
