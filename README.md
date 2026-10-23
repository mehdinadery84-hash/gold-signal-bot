# gold-signal-botdef gold_signal(price, previous_price):
    if price > previous_price:
        return "📈 روند صعودی؛ فقط بررسی کن"
    elif price < previous_price:
        return "📉 روند نزولی؛ فقط بررسی کن"
    else:
        return "⏸️ بازار بدون تغییر"

price = 10000000
previous_price = 9950000

print("🟡 سیگنال آزمایشی طلای آب‌شده")
print(gold_signal(price, previous_price))
