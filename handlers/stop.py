from core.keyboard import MAIN_KEYBOARD

awaiting_stop_confirm: set[int] = set()
from core.actions import stop_system
from core.lock import read_lock

STOP_CODE = "7777"


async def handle_stop_request(update, context) -> None:
    uid = update.effective_user.id
    awaiting_stop_confirm.add(uid)
    await update.message.reply_text(
        "⚠️ STOP ALL is protected.\n\n"
        "To enable STOP ALL, type this code manually:\n"
        f"{STOP_CODE}\n\n"
        "Or send: ❌ CANCEL"
    )


async def handle_stop_confirm(update, context) -> None:
    uid = update.effective_user.id
    awaiting_stop_confirm.discard(uid)

    user = update.effective_user
    username = user.username if user and user.username else "system"

    result = stop_system(by=username, reason="manual stop via telegram")

    await update.message.reply_text(
        "🛑 STOP ALL ENABLED\n\n"
        f"STATE: {result['state'].get('mode')}\n"
        f"{read_lock()}",
        reply_markup=MAIN_KEYBOARD,
    )


async def handle_stop_cancel(update, context) -> None:
    uid = update.effective_user.id
    awaiting_stop_confirm.discard(uid)
    await update.message.reply_text(
        "❌ STOP ALL cancelled.",
        reply_markup=MAIN_KEYBOARD,
    )
