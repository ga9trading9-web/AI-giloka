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

# تصميم واجهة الـ Mini App مع إعلاناتك في الأعلى وزر الانتقال المباشر لأداة الذكاء الاصطناعي
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Giloka AI Studio & Ads</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #0b0f19; color: #fff; margin: 0; padding: 15px; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; box-sizing: border-box; }
        .ads-container { background: #111827; padding: 15px; border-radius: 12px; border: 1px dashed #374151; text-align: center; width: 100%; margin-bottom: 20px; box-sizing: border-box; }
        .card { background: #1e293b; padding: 20px; border-radius: 14px; text-align: center; width: 100%; border: 1px solid #334155; box-sizing: border-box; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        h2 { color: #38bdf8; margin-top: 0; font-size: 20px; }
        p { color: #94a3b8; font-size: 13px; margin-bottom: 20px; }
        .btn { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; border: none; padding: 14px; border-radius: 10px; font-size: 16px; cursor: pointer; width: 100%; font-weight: bold; box-shadow: 0 4px 12px rgba(37,99,235,0.4); text-decoration: none; display: inline-block; box-sizing: border-box; }
        .btn:hover { background: linear-gradient(135deg, #1d4ed8, #1e40af); }
    </style>
</head>
<body>

    <!-- مساحة إعلانات Adsterra الخاصة بك في أعلى الشاشة -->
    <div class="ads-container">
        <p style="margin: 0 0 5px 0; color: #9ca3af; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;">إعلان مدعوم (ADSTERRA)</p>
        <div style="min-height: 45px; color: #6b7280; font-size: 13px; display: flex; align-items: center; justify-content: center;">
            <span>مساحة إعلانية نشطة</span>
            <!-- ضع كود إعلان Adsterra المباشر هنا مستقبلاً -->
        </div>
    </div>

    <div class="card">
        <h2>✨ استوديو Giloka الذكي</h2>
        <p>انقر على الزر أدناه لفتح أقوى موقع ذكاء اصطناعي لتعديل الصور وحذف الكتابات فوراً:</p>
        <a href="https://huggingface.co/spaces/akhaliq/latent-consistency-model" target="_blank" class="btn" onclick="openAIApp()">فتح أداة الذكاء الاصطناعي 🚀</a>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();

        function openAIApp() {
            // يمكن فتح الرابط خارج التيليجرام لضمان عمله بكفاءة عالية
            window.open("https://huggingface.co/spaces/akhaliq/latent-consistency-model", "_blank");
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
        f"أهلاً بك يا {message.from_user.first_name} في بوت **Giloka AI** 🤖🎨\n\n"
        "✨ انقر على الزر أدناه لفتح لوحة الاستوديو والإعلانات:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@dp.message(F.text)
async def handle_text(message: types.Message):
    await message.reply(
        "أهلاً بك! افتح الاستوديو عبر الزر أدناه.", 
        reply_markup=get_main_keyboard()
    )

async def main():
    await web_server()
    print("البوت يعمل بنجاح...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
