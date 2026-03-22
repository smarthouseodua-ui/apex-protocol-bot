from core.services import get_services_status


async def handle_services(update, context) -> None:
    services = get_services_status()

    text = ["🧰 SERVICES STATUS\n"]

    for name, status in services.items():
        icon = "🟢" if status == "OK" else "🔴"
        text.append(f"{icon} {name.upper()}: {status}")

    await update.message.reply_text("\n".join(text))
