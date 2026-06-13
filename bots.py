import telebot
from telebot import types
import os
from flask import Flask

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot Alive"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🏫 About School"),
        types.KeyboardButton("🎤 Art. Hachalu Hundessa"),
        types.KeyboardButton("🎓 Student Guide"),
        types.KeyboardButton("📧 Contact"),
        types.KeyboardButton("ℹ️ Help")
    )
    bot.send_message(
        message.chat.id,
        f"🎓 *Welcome, {message.from_user.first_name}!*\n\n"
        f"*Art. Hachalu Hundessa Memorial*\n"
        f"*Gimbi Special Secondary School*\n\n"
        f"🌟 *Educating with Purpose*",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda msg: msg.text == "ℹ️ Help")
def send_help(message):
    bot.send_message(message.chat.id, "/start | /about | /hachalu | /contact")

@bot.message_handler(commands=['about'])
@bot.message_handler(func=lambda msg: msg.text == "🏫 About School")
def about(message):
    bot.send_message(message.chat.id, "🏫 Est. 2013 E.C. | Gimbi, Oromia | 144+ students", parse_mode="Markdown")

@bot.message_handler(commands=['hachalu'])
@bot.message_handler(func=lambda msg: msg.text == "🎤 Art. Hachalu Hundessa")
def hachalu(message):
    bot.send_message(message.chat.id, "🎤 1986-2020 | Voice of Oromo People | \"Maalan Jiraa?\"", parse_mode="Markdown")

@bot.message_handler(commands=['contact'])
@bot.message_handler(func=lambda msg: msg.text == "📧 Contact")
def contact(message):
    bot.send_message(message.chat.id, "📍 Gimbi Town, West Wollega, Oromia, Ethiopia")

@bot.message_handler(func=lambda msg: True)
def fallback(message):
    bot.send_message(message.chat.id, "Type /start for menu")

if __name__ == '__main__':
    import threading
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
    print("🤖 Bot running...")
    bot.infinity_polling()         
