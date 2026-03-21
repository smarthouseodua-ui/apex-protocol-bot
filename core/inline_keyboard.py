from telegram import InlineKeyboardMarkup, InlineKeyboardButton

INLINE_MAIN = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📊 STATUS", callback_data="status"),
        InlineKeyboardButton("🤖 SERVICES", callback_data="services"),
    ],
    [
        InlineKeyboardButton("🛡 SAFE MODE", callback_data="modes"),
        InlineKeyboardButton("🔒 LOCK", callback_data="lock"),
    ],
    [
        InlineKeyboardButton("🛑 STOP ALL", callback_data="stop"),
        InlineKeyboardButton("🟢 START", callback_data="start"),
    ],
    [
        InlineKeyboardButton("🌐 TRAFFIC", callback_data="traffic"),
        InlineKeyboardButton("🧪 TEST", callback_data="test"),
    ],
])
