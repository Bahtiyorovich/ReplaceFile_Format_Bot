import os
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from docx import Document

# .env fayldan tokenni yuklash
load_dotenv()
TOKEN = os.getenv('BOT_API_TOKEN')

# Telegram botni sozlash
application = Application.builder().token(TOKEN).build()

# Qo'llab-quvvatlanadigan kirish va chiqish formatlari
SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'docx']
OUTPUT_FORMATS = ['jpg', 'png', 'pdf']

# Fayllarni vaqtinchalik saqlash
user_files = {}


def generate_random_key():
    """Callback data uchun tasodifiy kalit yaratish."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


async def handle_how_it_works(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot qanday ishlashini tushuntirish uchun yo'riqnoma."""
    if update.message:
        await update.message.reply_text(
            "Bot quyidagicha ishlaydi:\n\n"
            "1. Menga rasm yoki DOCX faylini yuboring.\n"
            "2. Faylni kerakli formatga o'zgartirishingiz uchun tanlovlar paydo bo'ladi.\n"
            "3. Tanlovdan so'ng, o'zgartirilgan faylni yuklab olishingiz mumkin.\n\n"
            "Qo'llab-quvvatlanadigan formatlar: JPG, PNG, PDF.\n"
            "DOCX fayllar faqat PDF formatiga aylantiriladi."
        )
    else:
        await update.callback_query.message.reply_text(
            "Bot qanday ishlashini tushuntirish uchun:\n\n"
            "1. Menga rasm yoki DOCX fayl yuboring.\n"
            "2. Keyin faylni kerakli formatga aylantiring.\n\n"
            "Qo'llab-quvvatlanadigan formatlar: JPG, PNG, PDF."
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Boshlang'ich xabar va yo'riqnoma."""
    keyboard = [
        [KeyboardButton("/start")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # Foydalanuvchiga salomlashuv xabari
    await update.message.reply_text(
        "Salom! Menga rasm yoki DOCX fayl yuboring va men uni formatini o'zgartiraman.\n"
        "Eslatma! Jarayon biroz vaqt olishi mumkin.",
        reply_markup=reply_markup
    )

    # Foydalanuvchiga botning ishlash yo'riqnomasi
    await handle_how_it_works(update, context)



async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi rasm yuborganida."""
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    try:
        downloaded_file = BytesIO()
        await file.download_to_memory(downloaded_file)
        downloaded_file.seek(0)

        image = Image.open(downloaded_file)
        input_format = image.format.lower()

        if input_format not in SUPPORTED_FORMATS:
            await update.message.reply_text("Kechirasiz, bu fayl formati qo'llab-quvvatlanmaydi.")
            return

        random_key = generate_random_key()
        user_files[random_key] = downloaded_file

        keyboard = [
            [InlineKeyboardButton("JPG", callback_data=f"convert|{random_key}|jpg")],
            [InlineKeyboardButton("PNG", callback_data=f"convert|{random_key}|png")],
            [InlineKeyboardButton("PDF", callback_data=f"convert|{random_key}|pdf")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Qaysi formatga o'zgartirishni xohlaysiz?", reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text(f"Kechirasiz, rasmni qayta ishlashda xatolik yuz berdi: {e}")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi DOCX fayl yuborganida."""
    document = update.message.document
    file = await context.bot.get_file(document.file_id)

    if not document.file_name.endswith('.docx'):
        await update.message.reply_text("Faqat DOCX formatdagi fayllarni qabul qilaman.")
        return

    try:
        downloaded_file = BytesIO()
        await file.download_to_memory(downloaded_file)
        downloaded_file.seek(0)

        random_key = generate_random_key()
        user_files[random_key] = downloaded_file

        keyboard = [
            [InlineKeyboardButton("PDF", callback_data=f"convert|{random_key}|pdf")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("DOCX faylni qaysi formatga aylantirishni xohlaysiz?", reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text(f"Faylni qayta ishlashda xatolik yuz berdi: {e}")


async def convert_photo_or_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Faylni tanlangan formatga o'zgartirish."""
    query = update.callback_query
    await query.answer()

    _, random_key, target_format = query.data.split('|')

    if random_key not in user_files:
        await query.message.reply_text("Kechirasiz, bu fayl mavjud emas yoki yaroqsiz.")
        return

    downloaded_file = user_files[random_key]

    try:
        output = BytesIO()
        if target_format in ['jpg', 'png']:
            image = Image.open(downloaded_file)
            image.save(output, format=target_format.upper())
        elif target_format == 'pdf':
            if downloaded_file.getbuffer().nbytes > 0 and downloaded_file.readable():
                if downloaded_file.getvalue().startswith(b'PK'):  # DOCX faylni tekshirish
                    doc = Document(downloaded_file)
                    output_file = output
                    doc.save(output_file)
                else:
                    image = Image.open(downloaded_file)
                    image.convert("RGB").save(output, format="PDF")
        else:
            await query.message.reply_text("Tanlangan format qo'llab-quvvatlanmaydi.")
            return

        output.seek(0)
        output_filename = f"converted.{target_format}"

        await query.message.reply_document(output, filename=output_filename)

    except Exception as e:
        await query.message.reply_text(f"Faylni qayta ishlashda xatolik yuz berdi: {e}")


def main():
    """Botni ishga tushirish."""
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(CallbackQueryHandler(convert_photo_or_doc, pattern="^convert"))

    application.run_polling()


if __name__ == '__main__':
    main()
