from core.keyboard import MAIN_KEYBOARD
from core.actions import unlock_system

START_CODE = "1111"

awaiting_start_confirm: set[int] = set()


async def handle_start_request(update, context) -> None:
    uid = update.effective_user.id
    awaiting_start_confirm.add(uid)
    await update.message.reply_text(
        "🟢 START is protected.\n\n"
        "To ENABLE system and clear STOP/LOCK state, type code:\n"
        f"{START_CODE}\n\n"
        "Or send: ❌ CANCEL"
    )


async def handle_start_confirm(update, context) -> None:
    uid = update.effective_user.id
    awaiting_start_confirm.discard(uid)

    user = update.effective_user
    username = user.username if user and user.username else "system"

    result = unlock_system(by=username, reason="manual start via telegram")

    await update.message.reply_text(
        "🟢 SYSTEM ENABLED\n\n"
        f"STATE: {result['state'].get('mode')}\n"
        f"{result['lock']}",
        reply_markup=MAIN_KEYBOARD,
    )


async def handle_start_cancel(update, context) -> None:
    uid = update.effective_user.id
    awaiting_start_confirm.discard(uid)
    await update.message.reply_text(
        "❌ START cancelled.",
        reply_markup=MAIN_KEYBOARD,
    )
