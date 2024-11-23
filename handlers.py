import os
from telegram import Update
from telegram.ext import CallbackContext
from utils import convert_word_to_pdf, convert_image, identify_format

# /start komandasi uchun handler
def start_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Salom! Men sizning fayllaringizni konvertatsiya qilish uchun tayyorman.\n"
        "💡 Yo'riqnoma olish uchun /help ni bosing."
    )

# /help komandasi uchun handler
def help_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📄 *Bot imkoniyatlari:*\n"
        "1. Word hujjatlarini PDF formatiga aylantirish.\n"
        "2. Rasmlarni ko‘plab formatlarga aylantirish (jpg, png, svg va boshqalar).\n\n"
        "📂 *Qo‘llab-quvvatlanadigan fayllar:* Word, rasm fayllari.\n"
        "Faylni jo‘natib konvertatsiya natijasini oling!"
    )

# Hujjatlar uchun handler
def document_handler(update: Update, context: CallbackContext):
    file = update.message.document
    file_name = file.file_name

    # Word hujjatlarini qayta ishlash
    if file_name.endswith((".doc", ".docx")):
        file_path = f"{file.file_unique_id}_{file_name}"
        file.download(file_path)

        update.message.reply_text("⏳ PDF formatiga o‘zgartirilmoqda, kuting...")
        pdf_path = convert_word_to_pdf(file_path)
        update.message.reply_document(open(pdf_path, "rb"))

        os.remove(file_path)
        os.remove(pdf_path)
    else:
        update.message.reply_text("❌ Ushbu fayl formati qo‘llab-quvvatlanmaydi.")

# Rasmlar uchun handler
def image_handler(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    file = photo.get_file()
    file_path = f"{file.file_unique_id}.jpg"
    file.download(file_path)

    update.message.reply_text("⏳ Rasm qayta ishlanmoqda, kuting...")
    new_paths = convert_image(file_path)
    for path in new_paths:
        update.message.reply_document(open(path, "rb"))
        os.remove(path)

    os.remove(file_path)
