from telegram import ReplyKeyboardMarkup

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📊 STATUS", "🤖 SERVICES"],
        ["🛡 SAFE MODE", "🔒 LOCK"],
        ["🛑 STOP ALL", "🟢 START"],
        ["🌐 TRAFFIC", "🧪 TEST"],
    ],
    resize_keyboard=True,
)

CONFIRM_KEYBOARD = ReplyKeyboardMarkup(
    [["❌ CANCEL"]],
    resize_keyboard=True,
)
