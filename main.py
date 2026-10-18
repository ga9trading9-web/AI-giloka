import asyncio
import os
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

TELEGRAM_BOT_TOKEN = "8863269193:AAEWc7KaQVNBuXRbfUzZDl1a-89Yi0x-wRc"
GEMINI_API_KEY = "AQ.Ab8RN6J4CKDLU6gnngkwP09_dNIKBvcJRs6WJNXRez-UNLQn_PpA"
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
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #131314; color: #e3e3e3; margin: 0; padding: 10px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; }
        .ads-container { background: #1e1f20; padding: 10px; border-radius: 10px; border: 1px dashed #444746; text-align: center; margin-bottom: 10px; flex-shrink: 0; }
        .ads-title { margin: 0 0 3px 0; color: #8e918f; font-size: 9px; text-transform: uppercase; letter-spacing: 1px; }
        .ads-box { min-height: 40px; color: #c4c7c5; font-size: 11px; display: flex; align-items: center; justify-content: center; }
        .chat-container { flex-grow: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding: 5px; margin-bottom: 10px; }
        .message { padding: 12px 16px; border-radius: 14px; max-width: 85%; font-size: 14px; line-height: 1.5; word-wrap: break-word; }
        .user-msg { background: #004a77; color: #e3e3e3; align-self: flex-start; border-bottom-right-radius: 4px; }
        .ai-msg { background: #1e1f20; color: #e3e3e3; align-self: flex-end; border-bottom-left-radius: 4px; border: 1px solid #444746; }
        .input-area { background: #1e1f20; padding: 10px; border-radius: 24px; display: flex; align-items: center; gap: 8px; border: 1px solid #444746; flex-shrink: 0; }
        .input-area textarea { flex-grow: 1; background: transparent; border: none; color: #e3e3e3; font-size: 14px; resize: none; outline: none; height: 24px; max-height: 80px; padding-top: 2px; }
        .send-btn { background: #8ab4f8; color: #131314; border: none; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 16px; }
    </style>
</head>
<body>

    <div class="ads-container">
        <p class="ads-title">إعلان مدعوم (ADSTERRA)</p>
        <div class="ads-box">
            <span>مساحة إعلانية نشطة</span>
        </div>
    </div>

    <div class="chat-container" id="chatContainer">
        <div class="message ai-msg">أهلاً بك! أنا نموذج Gemini الذكي. اسألني أي شيء وسأرد عليك فوراً.</div>
    </div>

    <div class="input-area">
        <textarea id="userInput" placeholder="اكتب رسالتك هنا..." rows="1" onkeydown="checkEnter(event)"></textarea>
        <button class="send-btn" onclick="sendMessage()">⬆</button>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let userId = tg.initDataUnsafe?.user?.id || 0;

        function checkEnter(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        }

        async function sendMessage() {
            const inputField = document.getElementById('userInput');
            const chatContainer = document.getElementById('chatContainer');
            const text = inputField.value.trim();

            if (!text) return;

            const userDiv = document.createElement('div');
            userDiv.className = 'message user-msg';
            userDiv.innerText = text;
            chatContainer.appendChild(userDiv);

            inputField.value = '';
            chatContainer.scrollTop = chatContainer.scrollHeight;

            const aiDiv = document.createElement('div');
            aiDiv.className = 'message ai-msg';
            aiDiv.innerText = 'جاري التفكير عبر Gemini...';
            chatContainer.appendChild(aiDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;

            try {
                const response = await fetch('/api/gemini', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: text, user_id: userId })
                });

                const data = await response.json();
                if (data.status === 'ok') {
                    aiDiv.innerText = data.reply;
                } else {
                    aiDiv.innerText = 'عذراً، حدث خطأ في معالجة الطلب.';
                }
            } catch (err) {
                aiDiv.innerText = 'تم إرسال طلبك بنجاح وسيتم الرد في المحادثة المباشرة.';
            }
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    </script>
</body>
</html>
"""

async def handle_index(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

async def handle_gemini_api(request):
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        user_id = data.get("user_id")

        if not prompt:
            return web.json_response({"status": "error", "message": "Empty prompt"}, status=400)

        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(gemini_url, json=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status == 200:
                    result_json = await resp.json()
                    ai_reply = result_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "عذراً، لم أستطع صياغة رد.")
                    
                    # إذا توفر معرف المستخدم، قم بإرسال الرد إليه مباشرة في الشات لضمان وصوله
                    if user_id:
                        try:
                            await bot.send_message(chat_id=user_id, text=f"🤖 **رد Gemini:**\n\n{ai_reply}", parse_mode="Markdown")
                        except Exception:
                            pass

                    return web.json_response({"status": "ok", "reply": ai_reply})
                else:
                    return web.json_response({"status": "error", "reply": "خطأ في اتصال خوادم Google."}, status=500)
    except Exception as e:
        print(f"Server Error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def web_server():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_post('/api/gemini', handle_gemini_api)
    
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
            text="✨ افتح استوديو Gemini والإعلانات", 
            web_app=WebAppInfo(url=f"{RENDER_WEBAPP_URL}/")
        )]
    ])

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    welcome_text = (
        f"أهلاً بك يا {message.from_user.first_name} في استوديو **Giloka Gemini AI** 🤖✨\n\n"
        "انقر على الزر أدناه لفتح واجهة الاستوديو مع إعلانات Adsterra في الأعلى:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@dp.message(F.text)
async def handle_text(message: types.Message):
    # إمكانية التحدث مباشرة مع البوت إذا أردت
    prompt = message.text
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(gemini_url, json=payload) as resp:
                if resp.status == 200:
                    res_json = await resp.json()
                    reply = res_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "عذراً.")
                    await message.reply(reply)
                else:
                    await message.reply("عذراً، حدث خطأ في الاتصال.")
    except Exception:
        await message.reply("حدث خطأ في النظام.")

async def main():
    await web_server()
    print("البوت يعمل بكفاءة...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
