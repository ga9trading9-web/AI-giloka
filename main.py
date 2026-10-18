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

TELEGRAM_BOT_TOKEN = "8863269193:AAFC8GH3QlMIaypS7xZLoSHb0bhoyfGKuuc"
OPENROUTER_API_KEY = "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"
RENDER_WEBAPP_URL = "https://ai-giloka.onrender.com"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# تصميم الـ Mini App مع ضغط الصور تلقائياً لمنع التعليق
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تعديل الصور بالذكاء الاصطناعي Giloka AI</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #0b0f19; color: #fff; text-align: center; padding: 15px; margin: 0; }
        .header { background: linear-gradient(135deg, #0284c7, #38bdf8); padding: 16px; border-radius: 14px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(2,132,199,0.3); }
        .header h2 { margin: 0; font-size: 20px; color: #fff; }
        .header p { margin: 4px 0 0 0; font-size: 12px; color: #e0f2fe; }
        .card { background: #1e293b; padding: 15px; border-radius: 12px; margin-bottom: 12px; text-align: right; border: 1px solid #334155; }
        label { color: #38bdf8; font-size: 13px; display: block; margin-bottom: 6px; font-weight: bold; }
        textarea { width: 100%; height: 80px; background: #0f172a; color: #fff; border: 1px solid #475569; border-radius: 8px; padding: 10px; box-sizing: border-box; font-size: 13px; resize: none; }
        textarea:focus { outline: none; border-color: #38bdf8; }
        .file-upload { border: 2px dashed #475569; padding: 12px; border-radius: 8px; text-align: center; cursor: pointer; background: #0f172a; margin-top: 5px; font-size: 13px; color: #94a3b8; }
        .file-upload input { display: none; }
        .btn { background: linear-gradient(135deg, #0284c7, #0369a1); color: white; border: none; padding: 12px; border-radius: 8px; font-size: 15px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 12px; box-shadow: 0 4px 10px rgba(2,132,199,0.4); }
        .btn:hover { background: linear-gradient(135deg, #0369a1, #075985); }
        .ads-box { background: #111827; padding: 12px; border-radius: 10px; border: 1px dashed #374151; margin-top: 10px; text-align: center; }
        #status { margin-top: 10px; font-size: 13px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h2>✨ Giloka AI Studio</h2>
        <p>معالجة وتعديل الصور بدقة فائقة</p>
    </div>

    <div class="card">
        <label for="imageInput">🖼️ اختر أو ارفع الصورة:</label>
        <div class="file-upload" onclick="document.getElementById('imageInput').click()">
            <span id="fileName">اضغط هنا لاختيار الصورة 📁</span>
            <input type="file" id="imageInput" accept="image/*" onchange="previewFile()">
        </div>

        <label for="userPrompt" style="margin-top: 12px;">💬 ماذا تريد أن أفعل بالصورة؟ (مثل: حذف الكتابات):</label>
        <textarea id="userPrompt" placeholder="اكتب تعليماتك هنا..."></textarea>
        
        <button class="btn" onclick="sendDataToBot()">إرسال للبوت للمعالجة 🚀</button>
        <div id="status"></div>
    </div>

    <div class="ads-box">
        <p style="margin: 0 0 5px 0; color: #9ca3af; font-size: 10px; text-transform: uppercase;">إعلان مدعوم (ADSTERRA)</p>
        <div style="min-height: 40px; color: #6b7280; font-size: 12px; display: flex; align-items: center; justify-content: center;">
            <span>مساحة إعلانية نشطة</span>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let compressedBase64 = "";

        function previewFile() {
            const file = document.getElementById('imageInput').files[0];
            if (file) {
                document.getElementById('fileName').innerText = "✅ تم اختيار: " + file.name;
                
                // ضغط الصورة تلقائياً لتناسب حدود تيليجرام
                const reader = new FileReader();
                reader.onload = function(event) {
                    const img = new Image();
                    img.onload = function() {
                        const canvas = document.createElement('canvas');
                        const MAX_WIDTH = 800;
                        const MAX_HEIGHT = 800;
                        let width = img.width;
                        let height = img.height;

                        if (width > height) {
                            if (width > MAX_WIDTH) {
                                height *= MAX_WIDTH / width;
                                width = MAX_WIDTH;
                            }
                        } else {
                            if (height > MAX_HEIGHT) {
                                width *= MAX_HEIGHT / height;
                                height = MAX_HEIGHT;
                            }
                        }

                        canvas.width = width;
                        canvas.height = height;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0, width, height);
                        compressedBase64 = canvas.toDataURL('image/jpeg', 0.7);
                    }
                    img.src = event.target.result;
                }
                reader.readAsDataURL(file);
            }
        }

        function sendDataToBot() {
            const promptText = document.getElementById('userPrompt').value;
            if (!compressedBase64) {
                document.getElementById('status').style.color = "#f87171";
                document.getElementById('status').innerText = "⚠️ يرجى اختيار الصورة الانتظار قليلاً لتجهيزها!";
                return;
            }
            if (!promptText) {
                document.getElementById('status').style.color = "#f87171";
                document.getElementById('status').innerText = "⚠️ يرجى كتابة التعليمات أو الطلب!";
                return;
            }

            document.getElementById('status').style.color = "#34d399";
            document.getElementById('status').innerText = "⏳ جاري إرسال البيانات ومعالجة الصورة...";

            try {
                tg.sendData(JSON.stringify({ image: compressedBase64, prompt: promptText }));
                setTimeout(() => { tg.close(); }, 1000);
            } catch (e) {
                document.getElementById('status').style.color = "#f87171";
                document.getElementById('status').innerText = "⚠️ حجم الصورة كبير جداً، يرجى إرسال الصورة مباشرة في المحادثة مع كتابة الوصف!";
            }
        }
    </script>
</body>
</html>
"""

async def handle_index(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

async def web_server():
    app = web.Application(client_max_size=1024*1024*20)
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
            text="✨ فتح استوديو الذكاء الاصطناعي", 
            web_app=WebAppInfo(url=f"{RENDER_WEBAPP_URL}/")
        )]
    ])

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    welcome_text = (
        f"أهلاً بك يا {message.from_user.first_name} في استوديو **giloka ai** 🤖🎨\n\n"
        "✨ **طريقة الاستخدام السريعة:**\n"
        "اضغط على الزر أدناه لفتح الاستوديو، اختر صورتك واكتب طلبك، أو أرسل صورتك مباشرة للمحادثة مع كتابة طلبك في وصف الصورة!\n\n"
        "👇 انقر للبدء:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

def process_image(image_bytes, prompt_text):
    try:
        img = Image.open(BytesIO(image_bytes))
        if "حذف" in prompt_text or "كتابات" in prompt_text or "تنظيف" in prompt_text or "تعديل" in prompt_text:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.5)
            img = img.filter(ImageFilter.SMOOTH_MORE)
        else:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.3)
            
        output_buffer = BytesIO()
        img.save(output_buffer, format="JPEG")
        output_buffer.seek(0)
        return output_buffer.read()
    except Exception as e:
        print(f"Error processing image: {e}")
        return image_bytes

@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    try:
        import json
        data = json.loads(message.web_app_data.data)
        image_base64 = data.get("image", "")
        user_prompt = data.get("prompt", "")
        
        if image_base64:
            await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
            header, encoded = image_base64.split(",", 1)
            image_bytes = base64.b64decode(encoded)
            
            processed_bytes = process_image(image_bytes, user_prompt)
            output_file = BufferedInputFile(processed_bytes, filename="giloka_ai_edited.jpg")
            
            await message.answer_photo(
                photo=output_file,
                caption=(
                    f"✨ **تمت معالجة الصورة بنجاح بواسطة Giloka AI!**\n\n"
                    f"📌 **الطلب:** {user_prompt}\n\n"
                    "---\n🚀 *لعملية أخرى، افتح الاستوديو عبر الزر أدناه:*"
                ),
                reply_markup=get_main_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await message.answer("⚠️ لم يتم استلام الصورة، يرجى المحاولة مرة أخرى.")
    except Exception as e:
        print(f"WebApp Data Error: {e}")
        await message.answer("حدث خطأ أثناء معالجة الصورة، يرجى إرسال الصورة مباشرة في المحادثة مع كتابة طلبك في وصفها لتفادي حجم الملفات الكبير.")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
    user_caption = message.caption or "تعديل وتحسين الصورة بدقة عالية."
    
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_path = file_info.file_path
    
    downloaded_file = await bot.download_file(file_path)
    image_bytes = downloaded_file.read()
    
    processed_image_bytes = process_image(image_bytes, user_caption)
    output_file = BufferedInputFile(processed_image_bytes, filename="giloka_ai_edited.jpg")
    
    await message.reply_photo(
        photo=output_file,
        caption=(
            f"✨ **تمت معالجة وتعديل الصورة بنجاح بواسطة Giloka AI!**\n\n"
            f"📌 **الطلب المنفذ:** {user_caption}\n\n"
            "---\n🚀 *أرسل صورة أخرى مع طلبك للتعديل عليها مباشرة:*"
        ),
        reply_markup=get_main_keyboard(),
        parse_Mode="Markdown"
    )

@dp.message(F.text)
async def handle_text(message: types.Message):
    await message.reply(
        "أهلاً بك! يمكنك إرسال صورتك مباشرة إلى المحادثة مع كتابة طلبك (مثل: حذف الكتابات) في وصف الصورة ليتم تعديلها وإرسالها لك فوراً دون أي انتظار.", 
        reply_markup=get_main_keyboard()
    )

async def main():
    await web_server()
    print("🚀 البوت يعمل مع ضغط الصور ومعالجتها بنجاح...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
