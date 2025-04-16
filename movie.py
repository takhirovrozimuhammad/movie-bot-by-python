from telegram import Update, ParseMode
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackContext)

# Bosqichlar
TITLE, LANGUAGE, GENRE, CHANNEL, VIDEO = range(5)

ADMIN_ID = 7498261631
movies = {}  # Kodlar asosida kinolar ro'yxati

# Admin: /addmovie
def start_add_movie(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        update.message.reply_text("⛔ Sizda kino qo‘shish huquqi yo‘q!")
        return ConversationHandler.END

    update.message.reply_text("🎬 Kino kodini kiriting:")
    return TITLE

def receive_title(update: Update, context: CallbackContext):
    context.user_data["code"] = update.message.text.strip()
    update.message.reply_text("🎬 Kino nomini kiriting:")
    return LANGUAGE

def receive_language(update: Update, context: CallbackContext):
    context.user_data["title"] = update.message.text.strip()
    update.message.reply_text("🌐 Tilini kiriting:")
    return GENRE

def receive_genre(update: Update, context: CallbackContext):
    context.user_data["language"] = update.message.text.strip()
    update.message.reply_text("🎭 Janrini kiriting:")
    return CHANNEL

def receive_channel(update: Update, context: CallbackContext):
    context.user_data["genre"] = update.message.text.strip()
    update.message.reply_text("📺 Kanal usernamesini kiriting (masalan: @kanalim):")
    return VIDEO

def receive_video(update: Update, context: CallbackContext):
    context.user_data["channel"] = update.message.text.strip()
    update.message.reply_text("📤 Endi videoni yuboring:")
    return 5  # keyingi state: video

def finalize_video(update: Update, context: CallbackContext):
    file_id = update.message.video.file_id

    code = context.user_data["code"]
    movies[code] = {
        "title": context.user_data["title"],
        "language": context.user_data["language"],
        "genre": context.user_data["genre"],
        "channel": context.user_data["channel"],
        "video_id": file_id
    }

    update.message.reply_text(f"✅ Kino saqlandi! Kod: {code}")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END

# /start komandasi
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Salom! Kino kodini yuboring:")

# Foydalanuvchi kod kiritsa
def check_movie_code(update: Update, context: CallbackContext):
    code = update.message.text.strip()
    movie = movies.get(code)

    if movie:
        caption = (
            f"🎬 <b>Kino nomi:</b> {movie['title']}\n"
            f"🌐 <b>Til:</b> {movie['language']}\n"
            f"🎭 <b>Janr:</b> {movie['genre']}\n"
            f"📺 <b>Kanal:</b> {movie['channel']}"
        )
        update.message.reply_video(movie["video_id"], caption=caption, parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text("❗ Bunday kodli kino topilmadi.")

# Botni ishga tushirish
def main():
    updater = Updater("7846673134:AAEn1ydm5vC-q1ruUtkgRSANhrCub92H5mw", use_context=True)
    dp = updater.dispatcher

    # Admin kino qo‘shish muloqoti
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("addmovie", start_add_movie)],
        states={
            TITLE: [MessageHandler(Filters.text & ~Filters.command, receive_title)],
            LANGUAGE: [MessageHandler(Filters.text & ~Filters.command, receive_language)],
            GENRE: [MessageHandler(Filters.text & ~Filters.command, receive_genre)],
            CHANNEL: [MessageHandler(Filters.text & ~Filters.command, receive_channel)],
            VIDEO: [MessageHandler(Filters.text & ~Filters.command, receive_video)],
            5: [MessageHandler(Filters.video, finalize_video)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Foydalanuvchi uchun kino kodi handler
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_movie_code))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
