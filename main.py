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

# واجهة Web App تدمج إعلاناتك في الأعلى وموقع/أداة الذكاء الاصطناعي الحقيقية بالأسفل
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Giloka AI Studio & Ads</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #0b0f19; color: #fff; margin: 0; padding: 10px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; }
        .ads-container { background: #111827; padding: 10px; border-radius: 10px; border: 1px dashed #374151; text-align: center; margin-bottom: 10px; flex-shrink: 0; }
        .iframe-container { flex-grow: 1; width: 100%; border-radius: 12px; overflow: hidden; border: 1px solid #334155; background: #fff; }
        iframe { width: 100%; height: 100%; border: none; }
    </style>
</head>
<body>

    <!-- مساحة إعلانات Adsterra الخاصة بك في أعلى الشاشة -->
    <div class="ads-container">
        <p style="margin: 0 0 3px 0; color: #9ca3af; font-size: 9px; text-transform: uppercase; letter-spacing: 1px;">إعلان مدعوم (ADSTERRA)</p>
        <div style="min-height: 35px; color: #6b7280; font-size: 11px; display: flex; align-items: center; justify-content: center;">
            <span>مساحة إعلانية نشطة</span>
            <!-- يمكنك وضع كود إعلان Adsterra المباشر هنا مستقبلاً -->
        </div>
    </div>

    <!-- نافذة موقع أو أداة الذكاء الاصطناعي الجاهزة لتعديل الصور وحذف الكتابات -->
    <div class="iframe-container">
        <!-- هنا يمكنك وضع رابط أداة إزالة الكتابات أو موقع الذكاء الاصطناعي الذي ترغب في عرضه -->
        <iframe src="https://huggingface.co/spaces/akhaliq/latent-consistency-model" title="AI Image Editor"></iframe>
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

def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✨ افتح استوديو الذكاء الاصطناعي والإعلانات", 
            web_app=WebAppInfo(url=f"{RENDER_WEBAPP_URL}/")
        )]
    ])

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    welcome_text = (
        f"أهلاً بك يا {message.from_user.first_name} في استوديو **Giloka AI** 🤖🎨\n\n"
        "✨ اضغط على الزر أدناه لفتح الاستوديو المتكامل (تعديل الصور بالذكاء الاصطناعي + إعلاناتك في الأعلى):"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@dp.message(F.text)
async def handle_text(message: types.Message):
    await message.reply(
        "أهلاً بك! افتح الاستوديو الذكي عبر الزر أدناه.", 
        reply_markup=get_main_keyboard()
    )

async def main():
    await web_server()
    print("البوت يعمل بنجاح مع عرض الـ Web App والإعلانات...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
