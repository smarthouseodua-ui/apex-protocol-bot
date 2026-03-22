from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from core.auth import is_allowed
from core.config import BOT_TOKEN
from core.keyboard import MAIN_KEYBOARD

from handlers.status import handle_status
from handlers.test import handle_test
from handlers.lock import handle_lock
from handlers.services import handle_services
from handlers.submodes import handle_submodes
from handlers.stop import handle_stop_request, handle_stop_confirm, handle_stop_cancel, STOP_CODE, awaiting_stop_confirm
from handlers.traffic import handle_traffic
from handlers.start_unlock import (
    handle_start_request,
    handle_start_confirm,
    handle_start_cancel,
    awaiting_start_confirm,
    START_CODE,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not is_allowed(user.id):
        return

    awaiting_stop_confirm.discard(user.id)
    awaiting_start_confirm.discard(user.id)

    await update.message.reply_text(
        "⚡ APEX SERVER CONTROL\nChoose an action:",
        reply_markup=MAIN_KEYBOARD,
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message = update.message

    if not user or not message or not is_allowed(user.id):
        return

    text = (message.text or "").strip()

    # 🧠 SMART STOP MODE
    if user.id in awaiting_stop_confirm:
        if text == STOP_CODE:
            await handle_stop_confirm(update, context)
            return

        if text == "❌ CANCEL":
            await handle_stop_cancel(update, context)
            return

        # разрешённые команды
        if text == "📊 STATUS":
            await handle_status(update, context)
            return

        if text == "🤖 SERVICES":
            await handle_services(update, context)
            return

        if text == "🧪 TEST":
            await handle_test(update, context)
            return

        await update.message.reply_text(
            f"⚠️ STOP ALL is waiting for confirmation.\n\n"
            f"Type {STOP_CODE} to confirm STOP ALL\n"
            f"or send ❌ CANCEL.\n\n"
            f"Allowed: 📊 STATUS / 🤖 SERVICES / 🧪 TEST"
        )
        return

    if user.id in awaiting_start_confirm:
        if text == START_CODE:
            await handle_start_confirm(update, context)
            return

        if text == "❌ CANCEL":
            await handle_start_cancel(update, context)
            return

        await update.message.reply_text(
            f"⚠️ Wrong code.\n\nType {START_CODE} to confirm START\nor send ❌ CANCEL."
        )
        return

    if text == "📊 STATUS":
        await handle_status(update, context)
    elif text == "🧪 TEST":
        await handle_test(update, context)
    elif text == "🔒 LOCK":
        await handle_lock(update, context)
    elif text == "🤖 SERVICES":
        await handle_services(update, context)
    elif text == "🛡 SAFE MODE":
        await handle_submodes(update, context)
    elif text == "🛑 STOP ALL":
        await handle_stop_request(update, context)
    elif text == "🟢 START":
        await handle_start_request(update, context)
    elif text == "🌐 TRAFFIC":
        await handle_traffic(update, context)
    else:
        await update.message.reply_text(
            "Use the keyboard below.",
            reply_markup=MAIN_KEYBOARD,
        )


def main() -> None:
    if not BOT_TOKEN.strip():
        raise RuntimeError("BOT_TOKEN is empty in core/config.py")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Apex Server Control started...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
