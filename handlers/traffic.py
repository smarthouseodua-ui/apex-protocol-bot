from core.utils import get_traffic_text, get_connections_text

def evaluate_risk(rx_text: str, connections_text: str) -> str:
    # очень простая базовая логика (потом усложним)
    risk = "🟢 NORMAL"

    # считаем количество IP
    conn_lines = connections_text.strip().splitlines()
    conn_count = len(conn_lines)

    # грубая оценка
    if conn_count > 10:
        risk = "🟡 WARNING"
    if conn_count > 20:
        risk = "🔴 DANGER"

    return risk

async def handle_traffic(update, context) -> None:
    traffic = get_traffic_text()
    connections = get_connections_text()

    risk = evaluate_risk(traffic, connections)

    text = (
        f"🌐 TRAFFIC STATUS: {risk}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{traffic}\n\n"
        f"🔗 CONNECTIONS:\n{connections}"
    )

    await update.message.reply_text(text)
