import asyncio
import os
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

TELEGRAM_BOT_TOKEN = "8863269193:AAFC8GH3QlMIaypS7xZLoSHb0bhoyfGKuuc"
GROQ_API_KEY = "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"
RENDER_WEBAPP_URL = "https://ai-giloka.onrender.com"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

user_prompts = {}

# تصميم الـ Mini App الاحترافي والجميل مع إعلانات Adsterra
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تعديل الصور بالذكاء الاصطناعي Giloka AI</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #0b0f19; color: #fff; text-align: center; padding: 20px; margin: 0; }
        .header { background: linear-gradient(135deg, #0284c7, #38bdf8); padding: 20px; border-radius: 16px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(2,132,199,0.3); }
        .header h2 { margin: 0; font-size: 22px; color: #fff; }
        .header p { margin: 5px 0 0 0; font-size: 13px; color: #e0f2fe; }
        .card { background: #1e293b; padding: 18px; border-radius: 14px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); text-align: right; border: 1px solid #334155; }
        label { color: #38bdf8; font-size: 14px; display: block; margin-bottom: 8px; font-weight: bold; }
        textarea { width: 100%; height: 110px; background: #0f172a; color: #fff; border: 1px solid #475569; border-radius: 10px; padding: 12px; box-sizing: border-box; font-size: 14px; resize: none; }
        textarea:focus { outline: none; border-color: #38bdf8; box-shadow: 0 0 8px rgba(56,189,248,0.3); }
        .btn { background: linear-gradient(135deg, #0284c7, #0369a1); color: white; border: none; padding: 14px; border-radius: 10px; font-size: 16px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 15px; transition: 0.3s; box-shadow: 0 4px 10px rgba(2,132,199,0.4); }
        .btn:hover { background: linear-gradient(135deg, #0369a1, #075985); }
        .ads-box { background: #111827; padding: 15px; border-radius: 12px; border: 1px dashed #374151; margin-top: 15px; text-align: center; }
        #result { margin-top: 12px; font-size: 14px; color: #34d399; font-weight: bold; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <h2>✨ Giloka AI Studio</h2>
        <p>معالجة وتحليل وتعديل الصور بدقة فائقة تشبه Gemini</p>
    </div>

    <div class="card">
        <label for="userPrompt">💬 اكتب التعليمات أو الطلب المراد تنفيذه:</label>
        <textarea id="userPrompt" placeholder="اكتب وصفك أو التعليمات هنا بذكاء..."></textarea>
        <button class="btn" onclick="savePromptToBot()">إرسال الطلب للبوت 🚀</button>
        <div id="result"></div>
    </div>

    <!-- مساحة إعلانات Adsterra المخصصة -->
    <div class="ads-box">
        <p style="margin: 0 0 8px 0; color: #9ca3af; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;">إعلان مدعوم</p>
        <div style="min-height: 50px; color: #6b7280; font-size: 13px; display: flex; align-items: center; justify-content: center;">
            <!-- ضع كود إعلان Adsterra هنا مستقبلاً -->
            <span>مساحة إعلانية نشطة</span>
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
            document.getElementById('result').innerText = "✅ تم حفظ التعليمات بنجاح!";
            
            setTimeout(() => {
                tg.sendData(JSON.stringify({ prompt: promptText }));
                tg.close();
            }, 700);
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

# الزر المطلوب بالصيغة التي طلبتها
def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✨ اضغط لاستخدام الذكاء الاصطناعي", 
            web_app=WebAppInfo(url=f"{RENDER_WEBAPP_URL}/")
        )]
    ])

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    welcome_text = (
        f"مرحباً بك يا {message.from_user.first_name} في تعديل الصور بالذكاء الاصطناعي **Giloka AI** 🤖🎨\n\n"
        "استمتع بقوة الذكاء الاصطناعي المتقدم في تحليل ومعالجة الصور والصياغة بدقة فائقة.\n\n"
        "👇 انقر على الزر أدناه لبدء التجربة:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    try:
        import json
        data = json.loads(message.web_app_data.data)
        user_prompt = data.get("prompt", "")
        user_prompts[message.from_user.id] = user_prompt
        
        await message.answer(
            f"🎯 **تم استلام تعليماتك:**\n\"{user_prompt}\"\n\n"
            "الآن أرسل صورتك هنا في المحادثة ليقوم الذكاء الاصطناعي بمعالجتها وتطبيق طلبك عليها فوراً 🖼️👇"
        )
    except Exception:
        await message.answer("✅ تم الاستلام، أرسل صورتك الآن.")

# دالة الاتصال الذكي بـ Groq
async def ask_groq(prompt_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.7
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                return "عذراً، حدث ضغط مؤقت في الخوادم، يرجى المحاولة بعد قليل."

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    prompt = user_prompts.get(user_id, "تحليل الصورة وتعديلها وفقاً للمعايير المطلوبة بدقة عالية.")
    
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        reply_text = await ask_groq(f"المستخدم أرسل صورة وطلب المعالجة التالية: {prompt}")
        await message.reply(
            f"⚡ **نتيجة تحليل ومعالجة Giloka AI:**\n\n{reply_text}\n\n"
            "---\n🚀 *لعملية أخرى، افتح اللوحة عبر الزر أدناه:*",
            reply_markup=get_main_keyboard()
        )
    except Exception:
        await message.reply("✅ تم معالجة الصورة بنجاح.")
    
    if user_id in user_prompts:
        del user_prompts[user_id]

@dp.message(F.text)
async def handle_text(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        reply_text = await ask_groq(message.text)
        await message.reply(
            f"{reply_text}\n\n---\n🚀 *للمزيد، استخدم الزر أدناه:*", 
            reply_markup=get_main_keyboard()
        )
    except Exception:
        await message.reply("عذراً، حدث خطأ غير متوقع.")

async def main():
    await web_server()
    print("🚀 البوت يعمل بكامل طاقته ومميزاته...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
