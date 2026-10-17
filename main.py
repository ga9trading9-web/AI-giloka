import asyncio
import os
from io import BytesIO
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from rembg import remove

# =================== البيانات الأساسية الخاصة بك ===================
TELEGRAM_BOT_TOKEN = "8863269193:AAFC8GH3QlMIaypS7xZLoSHb0bhoyfGKuuc"
POLLINATIONS_API_KEY = "sk_1uA0RH6GnFEZOHl3Tgw1mpHlSGvcBt7W"
WEBAPP_URL = "https://ga9trading9-web.github.io/Al-giloka/"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# خادم ويب وهمي بسيط لإبقاء الخدمة المجانية على Render تعمل بدون توقف
async def handle(request):
    return web.Response(text="Bot is running successfully 24/7!")

async def web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# زر فتح الـ WebApp وعرض الإعلانات المتدورة
def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✨ فتح شاشة الذكاء الاصطناعي والإعلانات", 
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])

# 1. أمر البداية /start
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    text = (
        f"أهلاً بك يا {message.from_user.first_name} في بوت الذكاء الاصطناعي والميزات المتقدمة! 🤖\n\n"
        "💬 **الدردشة:** أرسل لي أي سؤال وسأجيبك فوراً.\n"
        "🖼️ **الصور:** أرسل لي أي صورة وسأزيل خلفيتها مجاناً وبدقة عالية.\n\n"
        "اضغط على الزر أدناه لفتح لوحة الخدمات والمكافآت 👇"
    )
    await message.answer(text, reply_markup=get_main_keyboard())

# 2. معالجة النصوص والأسئلة عبر Pollinations AI
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
            f"{reply_text}\n\n--- \n🚀 *المزيد من الأدوات عبر الزر أدناه:*", 
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        await message.reply("حدث خطأ غير متوقع، يرجى المحاولة لاحقاً.")

# 3. إزالة الخلفيات من الصور مجاناً
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    status_msg = await message.reply("⏳ جاري معالجة الصورة وإزالة الخلفية بالذكاء الاصطناعي...")
    
    try:
        photo_io = BytesIO()
        file_info = await bot.get_file(message.photo[-1].file_id)
        await bot.download_file(file_info.file_path, photo_io)
        
        input_bytes = photo_io.getvalue()
        output_bytes = remove(input_bytes)
        
        result_file = types.BufferedInputFile(output_bytes, filename="no_bg.png")
        await message.answer_photo(
            photo=result_file, 
            caption="✅ تم إزالة الخلفية بنجاح!",
            reply_markup=get_main_keyboard()
        )
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text("حدث خطأ أثناء معالجة الصورة، تأكد من جودتها وحجمها.")

async def main():
    # تشغيل خادم الويب الوهمي والبوت معاً في نفس الوقت
    await web_server()
    print("🚀 البوت وخادم الويب يعملان الآن بنجاح...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
