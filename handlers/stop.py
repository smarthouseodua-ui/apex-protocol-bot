from core.keyboard import MAIN_KEYBOARD
from core.state import awaiting_stop_confirm
from core.utils import enable_stop_all, lock_state_text

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
    enable_stop_all()
    await update.message.reply_text(
        "🛑 STOP ALL ENABLED\n\n"
        f"{lock_state_text()}",
        reply_markup=MAIN_KEYBOARD,
    )

async def handle_stop_cancel(update, context) -> None:
    uid = update.effective_user.id
    awaiting_stop_confirm.discard(uid)
    await update.message.reply_text(
        "❌ STOP ALL cancelled.",
        reply_markup=MAIN_KEYBOARD,
    )
