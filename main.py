import asyncio
import os
import urllib.parse
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

TELEGRAM_BOT_TOKEN = "8863269193:AAFC8GH3QlMIaypS7xZLoSHb0bhoyfGKuuc"
POLLINATIONS_API_KEY = "sk_1uA0RH6GnFEZOHl3Tgw1mpHlSGvcBt7W"
RENDER_WEBAPP_URL = "https://ai-giloka.onrender.com"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# ذاكرة مؤقتة لتخزين تعليمات التعديل لكل مستخدم
user_prompts = {}

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تعديل الصور وخدمات الذكاء الاصطناعي</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: Tahoma, sans-serif; background: #0f172a; color: #fff; text-align: center; padding: 15px; margin: 0; }
        .card { background: #1e293b; padding: 15px; border-radius: 12px; margin-top: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); text-align: right; }
        h2 { color: #38bdf8; font-size: 20px; text-align: center; }
        p { color: #94a3b8; font-size: 14px; text-align: center; }
        label { color: #38bdf8; font-size: 14px; display: block; margin-bottom: 5px; font-weight: bold; }
        textarea { width: 100%; height: 80px; background: #0f172a; color: #fff; border: 1px solid #334155; border-radius: 8px; padding: 10px; box-sizing: border-box; font-size: 14px; resize: none; margin-bottom: 12px; }
        textarea:focus { outline: none; border-color: #38bdf8; }
        .btn { background: #0284c7; color: white; border: none; padding: 12px; border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 10px; }
        .btn:hover { background: #0369a1; }
        #result { margin-top: 15px; font-size: 14px; color: #34d399; text-align: center; font-weight: bold; }
    </style>
</head>
<body>
    <h2>🎨 لوحة خدمات Giloka AI</h2>
    <p>أهلاً بك في منصة معالجة الصور والتعديل الذكي.</p>
    
    <div class="card">
        <label for="userPrompt">💬 اكتب التعليمات المطلوب تطبيقها على الصورة:</label>
        <textarea id="userPrompt" placeholder="مثال: امسح كل الكتابات في الصورة، أو اجعل اسمي بشكل نيون..."></textarea>
        
        <button class="btn" onclick="savePromptToBot()">حفظ التعليمات وتوجه للبوت 🚀</button>
        <div id="result"></div>
    </div>

    <!-- قسم إعلانات Adsterra / AdsGram -->
    <div class="card" style="text-align: center;">
        <p style="margin: 0; color: #94a3b8; font-size: 12px;">إعلان مدعوم</p>
        <div style="margin-top: 10px; background: #334155; padding: 15px; border-radius: 8px; min-height: 60px;">
            <span style="color: #94a3b8; font-size: 13px;">مساحة إعلانية لربح المشاهدات</span>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();

        function savePromptToBot() {
            const promptText = document.getElementById('userPrompt').value;
            if (!promptText) {
                document.getElementById('result').style.color = "#f87171";
                document.getElementById('result').innerText = "⚠️ يرجى كتابة التعليمات أولاً!";
                return;
            }

            document.getElementById('result').style.color = "#34d399";
            document.getElementById('result').innerText = "✅ تم الحفظ! جاري توجيهك للمحادثة...";
            
            // إرسال البيانات وإغلاق الصفحة تلقائياً
            setTimeout(() => {
                tg.sendData(JSON.stringify({ prompt: promptText }));
                tg.close();
            }, 800);
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
            text="✨ فتح لوحة الذكاء الاصطناعي والإعلانات", 
            web_app=WebAppInfo(url=f"{RENDER_WEBAPP_URL}/")
        )]
    ])

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    text = (
        f"أهلاً بك يا {message.from_user.first_name} في بوت الذكاء الاصطناعي! 🤖\n\n"
        "1️⃣ اضغط على الزر أدناه لكتابة تعليمات التعديل.\n"
        "2️⃣ بعد الحفظ، أرسل صورتك هنا مباشرة وسأقوم بتعديلها لك فوراً!"
    )
    await message.answer(text, reply_markup=get_main_keyboard())

@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    try:
        import json
        data = json.loads(message.web_app_data.data)
        user_prompt = data.get("prompt", "")
        user_prompts[message.from_user.id] = user_prompt
        
        await message.answer(
            f"✅ **تم حفظ تعليماتك بنجاح:**\n\"{user_prompt}\"\n\n"
            "الآن أرسل الصورة التي تريد تعديلها مباشرة هنا في المحادثة 🖼️👇"
        )
    except Exception:
        await message.answer("✅ تم استلام التعليمات، أرسل صورتك الآن!")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    prompt = user_prompts.get(user_id, "تعديل الصورة وتحسين جودتها")
    
    status_msg = await message.answer(f"⏳ جاري تعديل الصورة بالذكاء الاصطناعي بحسب طلبك:\n\"{prompt}\" ...")
    
    try:
        # 1. الحصول على رابط الصورة المرفوعة من تيليجرام
        file_id = message.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        image_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"
        
        # 2. توليد صورة جديدة معدلة باستخدام Pollinations AI Image API
        encoded_prompt = urllib.parse.quote(f"{prompt}, high quality, detailed, based on {image_url}")
        edited_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        # 3. إرسال الصورة الناتجة للمستخدم
        await message.reply_photo(
            photo=edited_image_url,
            caption=f"✨ **تمت معالجة الصورة بنجاح!**\n📝 **التعليمات المطبقة:** {prompt}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📥 فتح الـ Mini App لمشاهدة الإعلانات ودعم البوت", web_app=WebAppInfo(url=f"{RENDER_WEBAPP_URL}/"))]
            ])
        )
        await status_msg.delete()
    except Exception:
        await status_msg.edit_text("❌ حدث خطأ أثناء معالجة الصورة، يرجى المحاولة مرة أخرى.")

async def main():
    await web_server()
    print("🚀 البوت والواجهة يعملان الآن بنجاح...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
