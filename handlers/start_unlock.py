from core.keyboard import MAIN_KEYBOARD
from core.state import awaiting_stop_confirm
from core.utils import disable_stop_all, lock_state_text

START_CODE = "1111"

awaiting_start_confirm: set[int] = set()

async def handle_start_request(update, context) -> None:
    uid = update.effective_user.id
    awaiting_start_confirm.add(uid)
    await update.message.reply_text(
        "🟢 START is protected.\n\n"
        "To DISABLE STOP ALL, type code:\n"
        f"{START_CODE}\n\n"
        "Or send: ❌ CANCEL"
    )

async def handle_start_confirm(update, context) -> None:
    uid = update.effective_user.id
    awaiting_start_confirm.discard(uid)
    disable_stop_all()
    await update.message.reply_text(
        "🟢 SYSTEM ENABLED\n\n"
        f"{lock_state_text()}",
        reply_markup=MAIN_KEYBOARD,
    )

async def handle_start_cancel(update, context) -> None:
    uid = update.effective_user.id
    awaiting_start_confirm.discard(uid)
    await update.message.reply_text(
        "❌ START cancelled.",
        reply_markup=MAIN_KEYBOARD,
    )
