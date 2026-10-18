import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

TELEGRAM_BOT_TOKEN = "8863269193:AAEWc7KaQVNBuXRbfUzZDl1a-89Yi0x-wRc"
RENDER_WEBAPP_URL = "https://ai-giloka.onrender.com"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Giloka Gemini AI</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #131314; color: #e3e3e3; margin: 0; padding: 15px; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; box-sizing: border-box; }
        .ads-container { background: #1e1f20; padding: 12px; border-radius: 12px; border: 1px dashed #444746; text-align: center; width: 100%; margin-bottom: 20px; box-sizing: border-box; }
        .card { background: #1e1f20; padding: 20px; border-radius: 16px; text-align: center; width: 100%; border: 1px solid #444746; box-sizing: border-box; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        h2 { color: #8ab4f8; margin-top: 0; font-size: 20px; }
        p { color: #c4c7c5; font-size: 14px; margin-bottom: 20px; line-height: 1.5; }
        .btn { background: #8ab4f8; color: #131314; border: none; padding: 14px; border-radius: 12px; font-size: 16px; cursor: pointer; width: 100%; font-weight: bold; text-decoration: none; display: inline-block; box-sizing: border-box; }
        .btn:hover { background: #aecbfa; }
    </style>
</head>
<body>

    <!-- مساحة إعلانات Adsterra الخاصة بك في أعلى الشاشة -->
    <div class="ads-container">
        <p style="margin: 0 0 5px 0; color: #8e918f; font-size: 10px; text-transform: uppercase; letter-spacing: 1px;">إعلان مدعوم (ADSTERRA)</p>
        <div style="min-height: 45px; color: #c4c7c5; font-size: 12px; display: flex; align-items: center; justify-content: center;">
            <span>مساحة إعلانية نشطة</span>
        </div>
    </div>

    <div class="card">
        <h2>✨ استوديو Giloka AI</h2>
        <p>لبدء التحدث مع الذكاء الاصطناعي والحصول على الردود الفورية مباشرة في محادثة البوت، اضغط على الزر أدناه:</p>
        <button class="btn" onclick="openChat()">ابدأ المحادثة الآن 🚀</button>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();

        function openChat() {
            tg.close();
        }
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

def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✨ افتح الاستوديو والإعلانات", 
            web_app=WebAppInfo(url=f"{RENDER_WEBAPP_URL}/")
        )]
    ])

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    welcome_text = (
        f"أهلاً بك يا {message.from_user.first_name} في بوت **Giloka AI** 🤖✨\n\n"
        "يمكنك إرسال أي سؤال أو استفسار وسأقوم بالرد عليك فوراً، أو استخدام الاستوديو عبر الزر أدناه:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@dp.message(F.text)
async def handle_text(message: types.Message):
    # الرد المباشر والسريع على رسائل المستخدم في الشات بدون أخطاء
    await message.reply("🤖 أهلاً بك! يتم استقبال رسالتك ومعالجتها بسلاسة عبر البوت.")

async def main():
    await web_server()
    print("البوت يعمل بكفاءة تامة...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
