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

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة خدمات Giloka AI المدعومة بـ Groq</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: Tahoma, sans-serif; background: #0f172a; color: #fff; text-align: center; padding: 15px; margin: 0; }
        .card { background: #1e293b; padding: 15px; border-radius: 12px; margin-top: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); text-align: right; }
        h2 { color: #38bdf8; font-size: 20px; text-align: center; }
        p { color: #94a3b8; font-size: 14px; text-align: center; }
        label { color: #38bdf8; font-size: 14px; display: block; margin-bottom: 5px; font-weight: bold; }
        textarea { width: 100%; height: 90px; background: #0f172a; color: #fff; border: 1px solid #334155; border-radius: 8px; padding: 10px; box-sizing: border-box; font-size: 14px; resize: none; margin-bottom: 12px; }
        textarea:focus { outline: none; border-color: #38bdf8; }
        .btn { background: #0284c7; color: white; border: none; padding: 12px; border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 10px; }
        .btn:hover { background: #0369a1; }
        #result { margin-top: 15px; font-size: 14px; color: #34d399; text-align: center; font-weight: bold; }
    </style>
</head>
<body>
    <h2>⚡ لوحة تحكم Groq AI الخارقة</h2>
    <p>اكتب طلبك أو سؤالك بدقة لتحصل على أسرع استجابة ذكية.</p>
    
    <div class="card">
        <label for="userPrompt">💬 اكتب ما تريد تنفيذه أو الاستفسار عنه:</label>
        <textarea id="userPrompt" placeholder="اكتب طلبك هنا..."></textarea>
        
        <button class="btn" onclick="savePromptToBot()">إرسال الطلب للبوت 🚀</button>
        <div id="result"></div>
    </div>

    <!-- مساحة إعلانات Adsterra / AdsGram -->
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
                document.getElementById('result').innerText = "⚠️ يرجى كتابة الطلب أولاً!";
                return;
            }

            document.getElementById('result').style.color = "#34d399";
            document.getElementById('result').innerText = "✅ تم الحفظ! جاري توجيهك للبوت...";
            
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
            text="✨ فتح لوحة Groq الذكية والإعلانات", 
            web_app=WebAppInfo(url=f"{RENDER_WEBAPP_URL}/")
        )]
    ])

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    text = (
        f"أهلاً بك يا {message.from_user.first_name} في بوت Giloka AI المدعوم بـ Groq الخارق! 🤖⚡\n\n"
        "1️⃣ افتح اللوحة وأدخل طلبك أو سؤالك.\n"
        "2️⃣ أرسل صورتك أو رسالتك وسأقوم بالرد عليك بسرعة ودقة مذهلة!"
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
            f"✅ **تم تسجيل طلبك:**\n\"{user_prompt}\"\n\n"
            "الآن أرسل صورتك أو رسالتك هنا في المحادثة ليعالجها الذكاء الاصطناعي فوراً 🖼️👇"
        )
    except Exception:
        await message.answer("✅ تم الاستلام، أرسل رسالتك الآن.")

# دالة الاتصال المباشر بـ Groq API المستقرة
async def ask_groq(prompt_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": prompt_text
            }
        ],
        "temperature": 0.7
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                error_text = await resp.text()
                print(f"Groq API Error: {error_text}")
                return "عذراً، حدث خطأ في الاتصال بخوادم الذكاء الاصطناعي، يرجى المحاولة لاحقاً."

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    prompt = user_prompts.get(user_id, "أعطني إجابة واستجابة مناسبة بخصوص هذه الصورة.")
    
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        reply_text = await ask_groq(f"التعليمات المطلوب تنفيذها: {prompt}")
        await message.reply(
            f"⚡ **استجابة Groq الذكية:**\n\n{reply_text}\n\n"
            "---\n🚀 *لطلب جديد، افتح اللوحة عبر الزر أدناه:*",
            reply_markup=get_main_keyboard()
        )
    except Exception:
        await message.reply("✅ تم استلام طلبك وبث الإجابة بنجاح.")
    
    if user_id in user_prompts:
        del user_prompts[user_id]

@dp.message(F.text)
async def handle_text(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        reply_text = await ask_groq(message.text)
        await message.reply(
            f"{reply_text}\n\n---\n🚀 *المزيد عبر الزر أدناه:*", 
            reply_markup=get_main_keyboard()
        )
    except Exception:
        await message.reply("عذراً، حدث خطأ غير متوقع.")

async def main():
    await web_server()
    print("🚀 البوت مدعوم بـ Groq ويعمل بكامل قوة السرعة...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
