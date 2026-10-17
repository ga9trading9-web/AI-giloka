import asyncio
import os
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

TELEGRAM_BOT_TOKEN = "8863269193:AAFC8GH3QlMIaypS7xZLoSHb0bhoyfGKuuc"
POLLINATIONS_API_KEY = "sk_1uA0RH6GnFEZOHl3Tgw1mpHlSGvcBt7W"
WEBAPP_URL = "https://ga9trading9-web.github.io/Al-giloka/"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

async def handle(request):
    return web.Response(text="Bot is running successfully 24/7!")

async def web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    try:
        await site.start()
    except Exception:
        pass

def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✨ فتح شاشة الذكاء الاصطناعي والإعلانات", 
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    text = (
        f"أهلاً بك يا {message.from_user.first_name} في بوت الذكاء الاصطناعي والميزات المتقدمة! 🤖\n\n"
        "💬 **الدردشة:** أرسل لي أي سؤال وسأجيبك فوراً.\n"
        "🖼️ **الصور:** لمعالجة الصور وإزالة الخلفيات بوضوح عالي، استخدم الزر أدناه.\n\n"
        "اضغط على الزر أدناه لفتح لوحة الخدمات والمكافآت 👇"
    )
    await message.answer(text, reply_markup=get_main_keyboard())

@dp.message(F.text)
async def handle_text(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        headers = {"Authorization": f"Bearer {POLLINATIONS_API_KEY}"}
        payload = {
            "messages": [{"role": "user", "content": message.text}],
            "model": "openai"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post("https://text.pollinations.ai/", json=payload, headers=headers) as resp:
                if resp.status == 200:
                    reply_text = await resp.text()
                else:
                    reply_text = "عذراً، حدث ضغط مؤقت على الخادم، يرجى المحاولة مرة أخرى."
        await message.reply(
            f"{reply_text}\n\n---\n🚀 *المزيد من الأدوات عبر الزر أدناه:*", 
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    except Exception:
        await message.reply("حدث خطأ غير متوقع، يرجى المحاولة لاحقاَ.")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.reply(
        "🖼️ لمعالجة الصور وإزالة الخلفيات بدقة عالية مجاناً، اضغط على زر شاشة الذكاء الاصطناعي أدناه 👇",
        reply_markup=get_main_keyboard()
    )

async def main():
    await web_server()
    print("🚀 البوت وخادم الويب يعملان الآن بنجاح...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
