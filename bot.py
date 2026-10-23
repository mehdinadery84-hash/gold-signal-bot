

import os
import json
import time
import urllib.parse
import urllib.request

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PRICE_URL = "https://api.gold-api.com/price/XAU"

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN تنظیم نشده است")

BOT_URL = f"https://api.telegram.org/bot{TOKEN}/"
last_update_id = 0
chat_id = None
previous_price = None
next_check = 0


def api_call(method, data=None):
    url = BOT_URL + method
    body = None

    if data is not None:
        body = urllib.parse.urlencode(data).encode()

    request = urllib.request.Request(url, data=body)

    with urllib.request.urlopen(request, timeout=25) as response:
        result = json.loads(response.read().decode())

    if not result.get("ok"):
        raise RuntimeError("Telegram API error")

    return result["result"]


def get_gold_price():
    request = urllib.request.Request(PRICE_URL)

    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.loads(response.read().decode())

    return float(data["price"])


def send_message(destination, message):
    api_call("sendMessage", {
        "chat_id": destination,
        "text": message
    })


def price_message(price):
    return (
        f"🟡 قیمت جهانی طلا (XAU)\n"
        f"💵 هر اونس: ${price:,.2f}\n"
        "قیمت به دلار برای هر اونس تروا است؛ "
        "قیمت طلای آب‌شده ایران نیست."
    )


def handle_updates():
    global last_update_id, chat_id, previous_price, next_check

    updates = api_call("getUpdates", {
        "offset": last_update_id + 1,
        "timeout": 10
    })

    for update in updates:
        last_update_id = update["update_id"]
        message = update.get("message", {})
        text = message.get("text", "")
        sender = message.get("chat", {}).get("id")

        if not sender:
            continue

        if text.startswith("/start"):
            chat_id = sender
            price = get_gold_price()
            previous_price = price
            next_check = time.time() + 900

            send_message(
                chat_id,
                "ربات آزمایشی طلا فعال شد.\n\n"
                + price_message(price)
                + "\n\nهر ۱۵ دقیقه روند قیمت را بررسی می‌کنم."
            )

        elif text.startswith("/price"):
            chat_id = sender
            price = get_gold_price()
            send_message(chat_id, price_message(price))


def check_price():
    global previous_price, next_check

    if chat_id is None:
        return

    price = get_gold_price()

    if previous_price is None:
        previous_price = price
        return

    change = (price - previous_price) / previous_price * 100

    if change >= 0.15:
        signal = "📈 روند کوتاه‌مدت صعودی"
    elif change <= -0.15:
        signal = "📉 روند کوتاه‌مدت نزولی"
    else:
        signal = "⏸️ تغییر کم؛ فعلاً صبر و بررسی"

    send_message(
        chat_id,
        price_message(price)
        + f"\n\n{signal}"
        + f"\nتغییر نسبت به بررسی قبلی: {change:+.3f}%"
        + "\n⚠️ سیگنال آزمایشی است، نه توصیه قطعی خرید یا فروش."
    )

    previous_price = price
    next_check = time.time() + 900


print("ربات آزمایشی در حال اجراست.")

while True:
    try:
        handle_updates()

        if chat_id is not None and time.time() >= next_check:
            check_price()

    except Exception as error:
        print("خطا:", str(error))
        time.sleep(10)
