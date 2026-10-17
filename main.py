import asyncio
import os
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

TELEGRAM_BOT_TOKEN = "8863269193:AAFC8GH3QlMIaypS7xZLoSHb0bhoyfGKuuc"
POLLINATIONS_API_KEY = "sk_1uA0RH6GnFEZOHl3Tgw1mpHlSGvcBt7W"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# محتوى صفحة الـ WebApp (الواجهة المدمجة لتجنب أخطاء 404)
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تعديل الصور وخدمات الذكاء الاصطناعي</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: Tahoma, sans-serif; background: #0f172a; color: #fff; text-align: center; padding: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 12px; margin-top: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        h2 { color: #38bdf8; }
        p { color: #94a3b8; }
        .btn { background: #0284c7; color: white; border: none; padding: 12px 20px; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 15px; width: 100%; }
        .btn:hover { background: #0369a1; }
    </style>
</head>
<body>
    <h2>🎨 لوحة خدمات Giloka AI</h2>
    <p>أهلاً بك في منصة معالجة الصور الذكية والدردشة التفاعلية.</p>
    
    <div class="card">
        <h3>إزالة الخلفيات وتعديل الصور</h3>
        <p>ارفع صورتك لمعالجتها عبر تقنيات الذكاء الاصطناعي بدقة عالية.</p>
        <button class="btn" onclick="alert('جاهز للاستخدام!')">بدء المعالجة</button>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
    </script>
</body>
</html>
"""

async def handle_index(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

async def web_server():
    app = web.Application()
    app.router.add_get('/', handle_index)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    try:
        await site.start()
    except Exception:
        pass

def get_main_keyboard(render_url):
    webapp_url = f"{render_url}/"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✨ فتح شاشة الذكاء الاصطناعي والإعلانات", 
            web_app=WebAppInfo(url=webapp_url)
        )]
    ])

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    # الحصول على رابط السيرفر الأساسي على Render لتوجيه الـ WebApp إليه تلقائياً
    # (يمكنك استبدال الرابط أدناه برابط تطبيقك الفعلي على Render لتثبيته)
    render_domain = os.environ.get("RENDER_EXTERNAL_URL", "https://ai-giloka.onrender.com")
    
    text = (
        f"أهلاً بك يا {message.from_user.first_name} في بوت الذكاء الاصطناعي والميزات المتقدمة! 🤖\n\n"
        "💬 **الدردشة:** أرسل لي أي سؤال وسأجيبك فوراً.\n"
        "🖼️ **الصور:** لمعالجة الصور وإزالة الخلفيات بوضوح عالي، استخدم الزر أدناه.\n\n"
        "اضغط على الزر أدناه لفتح لوحة الخدمات والمكافآت 👇"
    )
    await message.answer(text, reply_markup=get_main_keyboard(render_domain))

@dp.message(F.text)
async def handle_text(message: types.Message):
    render_domain = os.environ.get("RENDER_EXTERNAL_URL", "https://ai-giloka.onrender.com")
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
            reply_markup=get_main_keyboard(render_domain)
        )
    except Exception:
        await message.reply("حدث خطأ غير متوقع، يرجى المحاولة لاحقاَ.")

async def main():
    await web_server()
    print("🚀 البوت وخادم الويب والواجهة يعملان الآن بنجاح...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
