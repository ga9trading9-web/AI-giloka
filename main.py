import asyncio
import os
import aiohttp
import base64
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, BufferedInputFile

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
    <title>Giloka Gemini Studio</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #131314; color: #e3e3e3; margin: 0; padding: 12px; box-sizing: border-box; }
        .ads-container { background: #1e1f20; padding: 10px; border-radius: 10px; border: 1px dashed #444746; text-align: center; margin-bottom: 12px; }
        .ads-title { margin: 0 0 3px 0; color: #8e918f; font-size: 9px; text-transform: uppercase; letter-spacing: 1px; }
        .card { background: #1e1f20; padding: 15px; border-radius: 14px; border: 1px solid #444746; margin-bottom: 12px; }
        label { color: #8ab4f8; font-size: 13px; display: block; margin-bottom: 6px; font-weight: bold; }
        .file-upload { border: 2px dashed #444746; padding: 15px; border-radius: 10px; text-align: center; cursor: pointer; background: #111315; color: #9aa0a6; font-size: 13px; }
        .file-upload input { display: none; }
        textarea { width: 100%; height: 80px; background: #111315; color: #e3e3e3; border: 1px solid #444746; border-radius: 10px; padding: 10px; box-sizing: border-box; font-size: 13px; resize: none; margin-top: 8px; outline: none; }
        textarea:focus { border-color: #8ab4f8; }
        .btn { background: #8ab4f8; color: #131314; border: none; padding: 12px; border-radius: 10px; font-size: 15px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 12px; transition: 0.2s; }
        .btn:hover { background: #aecbfa; }
        #status { margin-top: 10px; font-size: 13px; font-weight: bold; text-align: center; }
    </style>
</head>
<body>

    <!-- إعلانات Adsterra في أعلى الشاشة -->
    <div class="ads-container">
        <p class="ads-title">إعلان مدعوم (ADSTERRA)</p>
        <div style="min-height: 35px; color: #c4c7c5; font-size: 11px; display: flex; align-items: center; justify-content: center;">
            <span>مساحة إعلانية نشطة</span>
        </div>
    </div>

    <div class="card">
        <label>🖼️ حدد الصورة المراد معالجتها:</label>
        <div class="file-upload" onclick="document.getElementById('imageInput').click()">
            <span id="fileName">اضغط هنا لاختيار صورة من هاتفك</span>
            <input type="file" id="imageInput" accept="image/*" onchange="previewFile()">
        </div>

        <label style="margin-top: 12px;">💬 اطلب ما تريد تنفيذه بالصورة (مثل تحليل، وصف، أو تعديل):</label>
        <textarea id="userPrompt" placeholder="اكتب تعليماتك هنا..."></textarea>
        
        <button class="btn" id="submitBtn" onclick="processAndSend()">إرسال إلى Gemini 🚀</button>
        <div id="status"></div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let userId = tg.initDataUnsafe?.user?.id || 0;
        let base64Image = "";

        function previewFile() {
            const file = document.getElementById('imageInput').files[0];
            if (file) {
                document.getElementById('fileName').innerText = "✅ تم اختيار: " + file.name;
                const reader = new FileReader();
                reader.onload = function(e) {
                    base64Image = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        }

        async function processAndSend() {
            const promptText = document.getElementById('userPrompt').value.trim();
            const statusDiv = document.getElementById('status');
            const submitBtn = document.getElementById('submitBtn');

            if (!base64Image) {
                statusDiv.style.color = "#f28b82";
                statusDiv.innerText = "⚠️ يرجى اختيار الصورة أولاً!";
                return;
            }
            if (!promptText) {
                statusDiv.style.color = "#f28b82";
                statusDiv.innerText = "⚠️ يرجى كتابة الطلب!";
                return;
            }

            statusDiv.style.color = "#8ab4f8";
            statusDiv.innerText = "⏳ جاري إرسال الصورة والطلب إلى Gemini... يرجى الانتظار";
            submitBtn.disabled = true;

            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: userId,
                        image: base64Image,
                        prompt: promptText
                    })
                });

                const data = await response.json();
                if (response.ok && data.status === 'ok') {
                    statusDiv.style.color = "#81c995";
                    statusDiv.innerText = "✅ تم تنفيذ الطلب بنجاح! تم إرسال النتيجة إلى محادثة البوت 🚀";
                    setTimeout(() => { tg.close(); }, 1500);
                } else {
                    statusDiv.style.color = "#f28b82";
                    statusDiv.innerText = "⚠️ " + (data.message || "حدث خطأ أثناء المعالجة.");
                    submitBtn.disabled = false;
                }
            } catch (err) {
                statusDiv.style.color = "#f28b82";
                statusDiv.innerText = "⚠️ حدث خطأ في الاتصال بالخادم.";
                submitBtn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

async def handle_index(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

async def handle_process(request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        image_base64 = data.get("image", "")
        prompt = data.get("prompt", "")

        if not image_base64 or not user_id or not prompt:
            return web.json_response({"status": "error", "message": "بيانات غير مكتملة"}, status=400)

        header, encoded = image_base64.split(",", 1)
        image_bytes = base64.b64decode(encoded)

        # الاتصال بـ Gemini API لمعالجة الصورة والطلب بصرياً ونضج الرد
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": encoded}}
                    ]
                }
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(gemini_url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    result_json = await resp.json()
                    ai_reply = result_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "تمت معالجة الطلب.")
                else:
                    ai_reply = "عذراً، لمطابقة الطلب حدث خطأ من خوادم الذكاء الاصطناعي."

        # إرسال الصورة الأصلية والنتيجة الذكية للمستخدم مباشرة في شات البوت
        photo_file = BufferedInputFile(image_bytes, filename="giloka_input.jpg")
        await bot.send_photo(
            chat_id=user_id,
            photo=photo_file,
            caption=(
                f"🤖 **نتيجة تحليل وتنفيذ طلب Gemini:**\n\n"
                f"📌 **الطلب:** {prompt}\n\n"
                f"💡 **الرد:**\n{ai_reply}"
            ),
            parse_mode="Markdown"
        )

        return web.json_response({"status": "ok"})
    except Exception as e:
        print(f"API Error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def web_server():
    app = web.Application(client_max_size=1024*1024*35)
    app.router.add_get('/', handle_index)
    app.router.add_post('/api/process', handle_process)
    
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
        "انقر على الزر أدناه لرفع صورتك وكتابة طلبك للحصول على النتيجة الفورية:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@dp.message(F.text)
async def handle_text(message: types.Message):
    await message.reply("أهلاً بك! افتح الاستوديو الذكي عبر الزر أدناه.", reply_markup=get_main_keyboard())

async def main():
    await web_server()
    print("البوت يعمل بكفاءة تامة...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
