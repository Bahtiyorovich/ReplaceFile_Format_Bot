from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update
from handlers import start_handler, document_handler, image_handler, help_handler

# Botni ishga tushirish
def main():
    # Tokenni kiriting
    TOKEN = "SIZNING_BOT_TOKENINGIZ"

    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Handlerlarni o'rnatish
    dispatcher.add_handler(CommandHandler("start", start_handler))
    dispatcher.add_handler(CommandHandler("help", help_handler))
    dispatcher.add_handler(MessageHandler(Filters.document, document_handler))
    dispatcher.add_handler(MessageHandler(Filters.photo, image_handler))

    # Botni ishga tushirish
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
