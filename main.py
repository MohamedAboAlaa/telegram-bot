from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.ext import AIORateLimiter

import os

BOT_TOKEN = os.getenv("BOT_TOKEN") or "7674738071:AAF7FcDI8l8s0oIgEOvQdtFOz2TSrJgd5cU"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or "https://your-app-name.railway.app"  # ✅ غيّره بالرابط الفعلي

REQUIRED_CHANNELS = ["@AboAlaachannel1", "@AboAlaachannel2"]

app = FastAPI()

telegram_app = Application.builder().token(BOT_TOKEN).rate_limiter(AIORateLimiter()).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("✅ Verify Subscription", callback_data="check_subscription")]]
    links = "\n".join([f"🔗 {channel}" for channel in REQUIRED_CHANNELS])
    text = f"👋 Welcome!\nPlease join the following channels before using the bot:\n\n{links}"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    subscribed = []
    not_subscribed = []

    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["member", "administrator", "creator"]:
                subscribed.append(channel)
            else:
                not_subscribed.append(channel)
        except:
            not_subscribed.append(channel)

    retry_keyboard = [[InlineKeyboardButton("🔁 Try Again", callback_data="check_subscription")]]

    if not_subscribed:
        sub_text = "\n".join([f"✅ {ch}" for ch in subscribed]) if subscribed else ""
        not_sub_text = "\n".join([f"❌ {ch}" for ch in not_subscribed])
        full_text = (
            f"You need to join all the required channels:\n\n"
            f"{sub_text}\n{not_sub_text}\n\n"
            f"Once you're done, click the button below to verify again."
        )
    else:
        full_text = "✅ Subscription verified! You may now use the bot."

    await update.callback_query.answer()
    if update.callback_query.message.text != full_text:
        await update.callback_query.edit_message_text(
            full_text, reply_markup=InlineKeyboardMarkup(retry_keyboard)
        )
    else:
        await update.callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(retry_keyboard)
        )


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(check_subscription, pattern="check_subscription"))


# ✅ نقطة الدخول لـ Telegram webhook
@app.post("/")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


# ✅ عند تشغيل السكربت لأول مرة (مثلاً في Railway)
@app.on_event("startup")
async def set_webhook():
    await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/")
    print(f"Webhook set to: {WEBHOOK_URL}/")
