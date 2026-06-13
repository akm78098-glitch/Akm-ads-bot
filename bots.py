import telebot
from telebot import types
import os
from flask import Flask

# ========== BOT SETUP ==========
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ========== FLASK KEEP-ALIVE ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Art. Hachalu Hundessa Memorial School Bot is Alive!"

# ========== /start COMMAND ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"🎓 *Greetings, {message.from_user.first_name}!*\n\n"
        f"*Welcome to*\n"
        f"Art. Hachalu Hundessa Memorial\n"
        f"Gimbi Special Secondary School\n\n"
        f"🏫 _Est. 2013 E.C. | Gimbi, Oromia, Ethiopia_\n\n"
        f"🌟 *\"Educating with Purpose\"*\n"
        f"🌟 *\"Continuing Hachalu's Vision\"*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 *How may I assist you today?*\n\n"
        f"Please select an option below or type /help"
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🏫 About School")
    btn2 = types.KeyboardButton("🎤 Art. Hachalu Hundessa")
    btn3 = types.KeyboardButton("🎓 Student Guide")
    btn4 = types.KeyboardButton("📅 Academic Calendar")
    btn5 = types.KeyboardButton("🏆 Achievements")
    btn6 = types.KeyboardButton("🖼️ Gallery")
    btn7 = types.KeyboardButton("📚 Resources")
    btn8 = types.KeyboardButton("📧 Contact")
    btn9 = types.KeyboardButton("⏱️ Pomodoro Timer")
    btn10 = types.KeyboardButton("ℹ️ Help")

    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10)
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)


# ========== /help COMMAND ==========
@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda msg: msg.text == "ℹ️ Help")
def send_help(message):
    help_text = (
        f"📖 *Help Menu*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"*Commands:*\n"
        f"/start — Main menu & greeting\n"
        f"/help — This help guide\n"
        f"/about — School information\n"
        f"/hachalu — Artist biography\n"
        f"/guide — Student success tips\n"
        f"/calendar — Academic calendar\n"
        f"/achievements — School awards\n"
        f"/gallery — Photo gallery\n"
        f"/resources — Study materials\n"
        f"/contact — Contact details\n"
        f"/timer — Pomodoro instructions\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 *Or use the menu buttons below.*"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")


# ========== ABOUT SCHOOL ==========
@bot.message_handler(commands=['about'])
@bot.message_handler(func=lambda msg: msg.text == "🏫 About School")
def about_school(message):
    text = (
        f"🏫 *About Our School*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"*Full Name:*\n"
        f"Art. Hachalu Hundessa Memorial\n"
        f"Gimbi Special Secondary School\n\n"
        f"*Established:* 2013 E.C.\n\n"
        f"*Location:* Gimbi Town, West Wollega Zone\n"
        f"Oromia Regional State, Ethiopia\n\n"
        f"*Students Trained:* 144+\n\n"
        f"*Mission:*\n"
        f"To produce competent, adaptable, innovative\n"
        f"manpower through outcome-based education.\n\n"
        f"*Vision:*\n"
        f"To become a centre of excellence in\n"
        f"building technology training.\n\n"
        f"*Key Activities:*\n"
        f"• Building Technology Array\n"
        f"• Small Scale Micro Enterprise Support\n"
        f"• Technology Accumulation & Transfer\n"
        f"• Producing Competent Industry Manpower\n"
        f"• Capacity Building\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🌟 *\"Educating with Purpose\"*"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


# ========== ART. HACHALU HUNDESSA ==========
@bot.message_handler(commands=['hachalu'])
@bot.message_handler(func=lambda msg: msg.text == "🎤 Art. Hachalu Hundessa")
def hachalu_bio(message):
    text = (
        f"🎤 *Art. Hachalu Hundessa*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📅 *1986 — June 29, 2020*\n\n"
        f"*Born:* Ambo, Oromia, Ethiopia\n\n"
        f"*Occupation:*\n"
        f"Singer, Songwriter, Civil Rights Activist\n\n"
        f"*Parents:* Hundessa Bonsa & Gudatu Hora\n\n"
        f"*Albums:*\n"
        f"🎵 Sanyii Mootii (2009)\n"
        f"🎵 Waa'ee Keenya (2013)\n"
        f"🎵 Maal Mallisaa (2021 - Posthumous)\n\n"
        f"*Iconic Song:* \"Maalan Jiraa?\"\n\n"
        f"*Legacy:*\n"
        f"Voice of the Oromo people. His music\n"
        f"became the soundtrack of the struggle\n"
        f"for freedom and equality.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎵 *Listen on YouTube*\n"
        f"Search: Hachalu Hundessa"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)


# ========== STUDENT GUIDE ==========
@bot.message_handler(commands=['guide'])
@bot.message_handler(func=lambda msg: msg.text == "🎓 Student Guide")
def student_guide(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📝 Exam Preparation Tips", callback_data="guide_exam")
    btn2 = types.InlineKeyboardButton("🎓 Scholarship Guide", callback_data="guide_scholarship")
    btn3 = types.InlineKeyboardButton("📚 Best Study Techniques", callback_data="guide_study")
    btn4 = types.InlineKeyboardButton("😰 Stress Management", callback_data="guide_stress")
    btn5 = types.InlineKeyboardButton("⏰ Time Management", callback_data="guide_time")
    btn6 = types.InlineKeyboardButton("💡 Growth Mindset", callback_data="guide_mindset")
    btn7 = types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_menu")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)

    text = (
        f"🎓 *Student Success Guide*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Select a topic to get practical advice\n"
        f"from your professors:"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)


# ========== STUDENT GUIDE CALLBACKS ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("guide_"))
def guide_callback(call):
    guide_data = {
        "guide_exam": (
            f"📝 *Exam Preparation Tips*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"1. Start studying *3-4 months* early\n"
            f"2. Collect & practice *past exam papers*\n"
            f"3. Study under *timed conditions*\n"
            f"4. Join or form a *study group*\n"
            f"5. Review all *mistakes carefully*\n"
            f"6. Get *7-8 hours* of sleep nightly\n"
            f"7. Eat healthy food before exams\n"
            f"8. Arrive *early* on exam day\n\n"
            f"💡 *Consistency beats cramming!*"
        ),
        "guide_scholarship": (
            f"🎓 *Scholarship Guide*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"1. Start applying *6-12 months* early\n"
            f"2. Prepare: transcripts, recommendations, essay\n"
            f"3. Write a *powerful personal story*\n"
            f"4. Connect goals to *community needs*\n"
            f"5. Apply to *multiple* scholarships\n"
            f"6. Check government & NGO websites\n"
            f"7. Ask teachers to *review* your application\n\n"
            f"💡 *Show how you'll give back to community!*"
        ),
        "guide_study": (
            f"📚 *Best Study Techniques*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"1. Use *active recall* - test yourself\n"
            f"2. Create *mind maps* for each topic\n"
            f"3. *Teach others* what you learn\n"
            f"4. Use the *Pomodoro Technique*\n"
            f"5. Take notes using *Cornell method*\n"
            f"6. Review material *within 24 hours*\n"
            f"7. Use *mnemonics* for memorization\n\n"
            f"💡 *If you can't explain it simply,\n"
            f"you don't understand it well enough.*"
        ),
        "guide_stress": (
            f"😰 *Stress Management*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"1. Practice *deep breathing* exercises\n"
            f"2. *Exercise* regularly\n"
            f"3. Break study into *small tasks*\n"
            f"4. Talk to *friends, family, or counselor*\n"
            f"5. Avoid *comparing yourself* to others\n"
            f"6. Take *regular breaks* during study\n"
            f"7. Remember: *One exam doesn't define you*\n\n"
            f"💡 *Your mental health comes first!*"
        ),
        "guide_time": (
            f"⏰ *Time Management*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"1. Create a *weekly study schedule*\n"
            f"2. Use *45-minute* focused study blocks\n"
            f"3. Prioritize *difficult subjects first*\n"
            f"4. Take *10-minute breaks* between blocks\n"
            f"5. Set *SMART goals*\n"
            f"6. Use the *2-minute rule* for small tasks\n"
            f"7. Remove *distractions* during study\n\n"
            f"💡 *Small daily efforts = massive results!*"
        ),
        "guide_mindset": (
            f"💡 *Growth Mindset*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*Fixed:* \"I'm not good at this.\"\n"
            f"*Growth:* \"I'm not good at this *yet.*\"\n\n"
            f"1. Embrace *challenges*\n"
            f"2. Learn from *criticism*\n"
            f"3. Persist through *setbacks*\n"
            f"4. Celebrate *effort*, not just results\n"
            f"5. Be inspired by *others' success*\n\n"
            f"💡 *Abilities can be developed\n"
            f"through dedication and hard work!*"
        ),
    }

    bot.answer_callback_query(call.id)
    if call.data in guide_data:
        bot.send_message(call.message.chat.id, guide_data[call.data], parse_mode="Markdown")


# ========== BACK TO MENU ==========
@bot.callback_query_handler(func=lambda call: call.data == "back_menu")
def back_to_menu(call):
    bot.answer_callback_query(call.id)
    send_welcome(call.message)


# ========== ACADEMIC CALENDAR ==========
@bot.message_handler(commands=['calendar'])
@bot.message_handler(func=lambda msg: msg.text == "📅 Academic Calendar")
def academic_calendar(message):
    text = (
        f"📅 *Academic Calendar*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🗓 *September* - New Academic Year\n"
        f"🗓 *Oct 2* - Hachalu Memorial Lecture\n"
        f"🗓 *December* - Mid-Semester Exams\n"
        f"🗓 *Jan 7* - Ethiopian Christmas\n"
        f"🗓 *Jan 19* - Timket (Epiphany)\n"
        f"🗓 *February* - Semester 1 Finals\n"
        f"🗓 *March* - Semester Break\n"
        f"🗓 *April* - Semester 2 Begins\n"
        f"🗓 *May 1* - Workers' Day\n"
        f"🗓 *June 29* - Hachalu Memorial Day\n"
        f"🗓 *July* - Final Exams\n"
        f"🗓 *August* - Graduation Ceremony\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


# ========== ACHIEVEMENTS ==========
@bot.message_handler(commands=['achievements'])
@bot.message_handler(func=lambda msg: msg.text == "🏆 Achievements")
def achievements(message):
    text = (
        f"🏆 *School Achievements*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏅 *Institutional Awards:*\n"
        f"• 2015 - Best Emerging Technical School\n"
        f"• 2017 - Excellence in Building Technology\n"
        f"• 2019 - Top Student Enterprise Performer\n"
        f"• 2021 - Community Impact Award\n"
        f"• 2023 - Best Memorial School Award\n\n"
        f"🎓 *Top Students:*\n"
        f"• Tolosa Gudeta - Regional 🥇\n"
        f"• Bontu Tadesse - National Scholarship\n"
        f"• Gammachiis Lemma - Entrepreneurship\n"
        f"• Faaya Gutama - Employed by Top Firm\n"
        f"• Milkii Dirribaa - Innovation Prize\n"
        f"• Caalaa Bultum - Community Leadership\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


# ========== GALLERY ==========
@bot.message_handler(commands=['gallery'])
@bot.message_handler(func=lambda msg: msg.text == "🖼️ Gallery")
def gallery(message):
    text = (
        f"🖼️ *Photo Gallery*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📸 Main School Building - Gimbi Town\n"
        f"📸 Students Q&A Program Event\n"
        f"📸 Sports & Athletics Training\n"
        f"📸 Agricultural Farm Practice\n"
        f"📸 Senior Students Ceremony\n"
        f"📸 Cultural Community Event\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🌐 *Visit our website for full gallery!*"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


# ========== RESOURCES ==========
@bot.message_handler(commands=['resources'])
@bot.message_handler(func=lambda msg: msg.text == "📚 Resources")
def resources(message):
    text = (
        f"📚 *Resources & Downloads*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📄 *Documents:*\n"
        f"• Top 50 Aptitude Test (PDF)\n"
        f"• School Handbook 2026 (PDF)\n"
        f"• Student Code of Conduct (PDF)\n\n"
        f"📚 *Study Materials:*\n"
        f"• Past Papers - Mathematics\n"
        f"• Past Papers - Technical Drawing\n"
        f"• Scholarship Application Guide\n\n"
        f"🔗 *Links:*\n"
        f"• Oromia Education Bureau Portal\n"
        f"• Ethiopian Ministry of Education\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🌐 *Download from our website!*"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


# ========== CONTACT ==========
@bot.message_handler(commands=['contact'])
@bot.message_handler(func=lambda msg: msg.text == "📧 Contact")
def contact(message):
    text = (
        f"📧 *Contact Us*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📍 *Address:*\n"
        f"Gimbi Town, West Wollega Zone\n"
        f"Oromia Regional State, Ethiopia\n\n"
        f"📞 *Phone:*\n"
        f"(To be updated by school)\n\n"
        f"✉️ *Email:*\n"
        f"(To be updated by school)\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🌐 *Visit our website to send a message!*"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


# ========== POMODORO TIMER ==========
@bot.message_handler(commands=['timer'])
@bot.message_handler(func=lambda msg: msg.text == "⏱️ Pomodoro Timer")
def pomodoro(message):
    text = (
        f"⏱️ *Pomodoro Study Timer*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🍅 *Study:* 25 minutes focused work\n"
        f"☕ *Break:* 5 minutes rest\n"
        f"🔄 *Repeat:* 4 times total\n"
        f"🌴 *Long Break:* 15-30 minutes\n\n"
        f"*Benefits:*\n"
        f"✅ Better focus & concentration\n"
        f"✅ Prevents burnout\n"
        f"✅ Improves time awareness\n"
        f"✅ Reduces procrastination\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏰ *Your 25 minutes starts... NOW!*\n"
        f"💡 *Use our website timer for auto-tracking!*"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


# ========== FALLBACK ==========
@bot.message_handler(func=lambda msg: True)
def fallback(message):
    bot.send_message(
        message.chat.id,
        "❓ *I didn't understand that.*\n\nType /start to see the menu or /help for guidance.",
        parse_mode="Markdown"
    )


# ========== RUN BOT ==========
if __name__ == '__main__':
    import threading
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    print("🤖 Bot is running...")
    bot.infinity_polling()