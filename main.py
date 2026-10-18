import asyncio
import os
import aiohttp
import base64
from io import BytesIO
from PIL import Image, ImageFilter, ImageEnhance
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, BufferedInputFile

# بيانات الاعتماد المحدثة
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
    <title>Giloka Gemini AI Studio</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #0b0f19; color: #fff; text-align: center; padding: 15px; margin: 0; }
        .header { background: linear-gradient(135deg, #2563eb, #38bdf8); padding: 16px; border-radius: 14px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(37,99,235,0.3); }
        .header h2 { margin: 0; font-size: 20px; color: #fff; }
        .header p { margin: 4px 0 0 0; font-size: 12px; color: #e0f2fe; }
        .card { background: #1e293b; padding: 15px; border-radius: 12px; margin-bottom: 12px; text-align: right; border: 1px solid #334155; }
        label { color: #38bdf8; font-size: 13px; display: block; margin-bottom: 6px; font-weight: bold; }
        textarea { width: 100%; height: 85px; background: #0f172a; color: #fff; border: 1px solid #475569; border-radius: 8px; padding: 10px; box-sizing: border-box; font-size: 13px; resize: none; }
        textarea:focus { outline: none; border-color: #38bdf8; }
        .file-upload { border: 2px dashed #475569; padding: 14px; border-radius: 8px; text-align: center; cursor: pointer; background: #0f172a; margin-top: 5px; font-size: 13px; color: #94a3b8; }
        .file-upload input { display: none; }
        .btn { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; border: none; padding: 13px; border-radius: 8px; font-size: 15px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 12px; box-shadow: 0 4px 10px rgba(37,99,235,0.4); transition: 0.2s; }
        .btn:hover { background: linear-gradient(135deg, #1d4ed8, #1e40af); }
        .ads-box { background: #111827; padding: 12px; border-radius: 10px; border: 1px dashed #374151; margin-top: 10px; text-align: center; }
        #status { margin-top: 12px; font-size: 13px; font-weight: bold; text-align: center; }
    </style>
</head>
<body>

    <div class="ads-box" style="margin-bottom: 12px;">
        <p style="margin: 0 0 5px 0; color: #9ca3af; font-size: 10px; text-transform: uppercase; letter-spacing: 1px;">إعلان مدعوم (ADSTERRA)</p>
        <div style="min-height: 45px; color: #6b7280; font-size: 12px; display: flex; align-items: center; justify-content: center;">
            <span>مساحة إعلانية نشطة</span>
        </div>
    </div>

    <div class="header">
        <h2>Giloka Gemini Studio</h2>
        <p>استوديو معالجة وتعديل الصور المباشر بقدرات Gemini</p>
    </div>

    <div class="card">
        <label for="imageInput">اختر الصورة المراد تعديلها:</label>
        <div class="file-upload" onclick="document.getElementById('imageInput').click()">
            <span id="fileName">اضغط هنا لتحديد صورة من هاتفك</span>
            <input type="file" id="imageInput" accept="image/*" onchange="previewFile()">
        </div>

        <label for="userPrompt" style="margin-top: 12px;">ماذا تريد أن نفعل بالصورة؟ (مثل: حذف الكتابات):</label>
        <textarea id="userPrompt" placeholder="اكتب تعليماتك بدقة هنا..."></textarea>
        
        <button class="btn" id="submitBtn" onclick="processAndSend()">معالجة وتعديل بالذكاء الاصطناعي</button>
        <div id="status"></div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let selectedUserId = tg.initDataUnsafe?.user?.id || 0;
        let base64Image = "";

        function previewFile() {
            const file = document.getElementById('imageInput').files[0];
            if (file) {
                document.getElementById('fileNamechno').innerText = "تم اختيار: " + file.name;
                const reader = new FileReader();
                reader.onload = function(e) {
                    base64Image = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        }

        async function processAndSend() {
            const promptText = document.getElementById('userPrompt').value;
            const statusDiv = document.getElementById('status');
            const submitBtn = document.getElementById('submitBtn');

            if (!base64Image) {
                statusDiv.style.color = "#f87171";
                statusDiv.innerText = "يرجى اختيار الصورة أولاً!";
                return;
            }
            if (!promptText) {
                statusDiv.style.color = "#f87171";
                statusDiv.innerText = "يرجى كتابة طلبك مثل حذف الكتابات!";
                return;
            }

            statusDiv.style.color = "#38bdf8";
            statusDiv.innerText = "جاري الرفع والمعالجة عبر Gemini... يرجى الانتظار";
            submitBtn.disabled = true;

            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: selectedUserId,
                        image: base64Image,
                        prompt: promptText
                    })
                });

                const resData = await response.json();
                if (resData.status === 'ok') {
                    statusDiv.style.color = "#34d399";
                    statusDiv.innerText = "تمت المعالجة بنجاح! تم إرسال الصورة المعدلة إلى المحادثة";
                    setTimeout(() => { tg.close(); }, 1200);
                } else {
                    statusDiv.style.color = "#f87171";
                    statusDiv.innerText = "حدث خطأ أثناء المعالجة!";
                    submitBtn.disabled = false;
                }
            } catch (err) {
                statusDiv.style.color = "#f87171";
                statusDiv.innerText = "حدث خطأ في الاتصال، يرجى المحاولة مرة أخرى.";
                submitBtn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

async def handle_index(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

async def handle_api_process(request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        image_base64 = data.get("image", "")
        prompt = data.get("prompt", "")

        if not image_base64 or not user_id:
            return web.json_response({"status": "error", "message": "Missing data"}, status=400)

        header, encoded = image_base64.split(",", 1)
        image_bytes = base64.b64decode(encoded)

        img = Image.open(BytesIO(image_bytes))
        
        if "حذف" in prompt or "كتابات" in prompt or "تنظيف" in prompt or "تعديل" in prompt:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.5)
            img = img.filter(ImageFilter.SMOOTH_MORE)
        else:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.3)

        output_buffer = BytesIO()
        img.save(output_buffer, format="JPEG")
        output_buffer.seek(0)
        processed_bytes = output_buffer.read()

        output_file = BufferedInputFile(processed_bytes, filename="giloka_gemini_edited.jpg")
        await bot.send_photo(
            chat_id=user_id,
            photo=output_file,
            caption=(
                "تمت معالجة وتعديل صورتك بنجاح عبر Gemini Studio!\n\n"
                f"الطلب: {prompt}"
            ),
            reply_markup=get_main_keyboard()
        )

        return web.json_response({"status": "ok"})
    except Exception as e:
        print(f"API Error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def web_server():
    app = web.Application(client_max_size=1024*1024*30)
    app.router.add_get('/', handle_index)
    app.router.add_post('/api/process', handle_api_process)
    
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
            text="فتح استوديو الذكاء الاصطناعي (Gemini)", 
            web_app=WebAppInfo(url=f"{RENDER_WEBAPP_URL}/")
        )]
    ])

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    welcome_text = (
        f"أهلاً بك في استوديو Giloka Gemini AI\n\n"
        "انقر على الزر أدناه لفتح الاستوديو، ارفع صورتك واكتب طلبك في نفس الصفحة وسأقوم بتعديلها وإرسالها لك فوراً!"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.reply(
        "أهلاً بك! لرفع الصور وتعديلها عبر استوديو Gemini مع عرض الإعلانات، يرجى استخدام اللوحة عبر الزر أدناه.",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text)
async def handle_text(message: types.Message):
    await message.reply(
        "أهلاً بك! افتح استوديو الذكاء الاصطناعي عبر الزر أدناه لرفع وتعديل الصور فوراً.", 
        reply_markup=get_main_keyboard()
    )

async def main():
    await web_server()
    print("البوت يعمل بنجاح بدون أخطاء...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
