import sqlite3
import requests
import bs4
import os
import smtplib
import telegram
from telegram.ext import *
from telegram.ext.dispatcher import run_async
import telepot 

bot = telepot.Bot("653252548:AAGMGOpwXgNxd9QkjY34XCa5oXBtTNNSdw")

def start(bot, update):
    key = ['/start','/help','/movie_list']
    custom_keyboard = [[item] for item in key]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.sendMessage(chat_id=update.message.chat_id, text="bot started! Please give me a movie name or choose ;)", reply_markup=reply_markup)

def back2mainlist(bot, update):
    key = ['/start','/help','/movie_list']
    custom_keyboard = [[item] for item in key]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.sendMessage(chat_id=update.message.chat_id, text="Please give me a movie name or choose ;)", reply_markup=reply_markup)

@run_async
def movie_name(bot, update):
    try:
        user = update.message.from_user
        user_msg = update.message.text
        bot.sendMessage(chat_id=update.message.chat_id, text="Please wait, it takes some moment :)")
        print("user",user['username'],"by id",user['id'],"with name",user['first_name'],user['last_name'],"searched:",user_msg)
        conn = sqlite3.connect('IMDB_BOT.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS search_result(result TEXT)')
        c.execute('SELECT * FROM search_result')
        result_data = c.fetchall()
        flag = True
        for x in result_data:
            if user_msg == x[0]:
                flag = False
                break
        if flag:
            c.execute('INSERT INTO search_result (result) VALUES (?)', (str(user_msg),))
            conn.commit()
        c.close()
        conn.close()
        name = user_msg.split(' ')
        name = '+'.join(name)
        msg_text = "Movie Name: "+user_msg
        page = requests.get("http://www.imdb.com/find?ref_=nv_sr_fn&q="+name+"&s=all")
        soup = bs4.BeautifulSoup(page.content, "lxml")
        link = soup.findAll("td","result_text")
        know = requests.get("http://www.imdb.com/"+link[0].a['href'])
        soup = bs4.BeautifulSoup(know.content, "lxml")
        story_text = soup.find('div', "inline canwrap")
        story_text = story_text.findAll("p")[0]

        info = soup.findAll('div',"ratingValue")
        for i in info:
            bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
            msg_text += "\n#Rating: "+i.strong['title']

        bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        msg_text += "\n-----------Story------------\n" + story_text.text

        genre_types = soup.find('div', itemprop="genre")
        if genre_types is not None:
            genre_types = genre_types.find_all('a')
            bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
            msg_text += "\n-----------Genres------------\n"
            for i in genre_types:
                msg_text += i.string+" "
            bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

            bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        msg_text += "\n-----------Details------------\n"

        info = soup.findAll('div', "txt-block")
        msg_text += "\n#Country: "
        for node in info:
            a = node.findAll('a')
            for i in a:
                if "country_of_origin" in i['href']:
                    msg_text += i.string+" "

        bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        msg_text += "\n#Language: "
        for node in info:
            a = node.findAll('a')
            for i in a:
                if "primary_language" in i['href']:
                    msg_text += i.string+" "

        bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        info = soup.findAll('div', "rec_item")
        msg_text += "\n#Similar_movies:\n"
        for i in info:
            a = i.findAll('a')[0]
            msg_text += a.img['title']+"\n"
        bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

        det = requests.get("http://www.imdb.com/"+(link[0].a['href'])[0:16]+"/releaseinfo?ref_=tt_dt_dt")
        soup = bs4.BeautifulSoup(det.content, "lxml")
        info = soup.findAll('td', "release_date")
        bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        msg_text += "#Release_Date: " + info[0].text
        msg_text += "\n--------------------\nProvided by: IMDB-knowledge bot\n@soroush_mybot"
        update.message.reply_text(msg_text)
        updater.start_polling()

    except Exception as e:
        print('---------------------------------ERROR--------------------------------',str(e),'----------------------------------------------------------------------')
        update.message.reply_text("#Err:\nSorry! An Error happened. Make sure the name is correct and try again.")
        updater.start_polling()

def movie_list(bot, update):
    conn = sqlite3.connect('IMDB_BOT.db')
    c = conn.cursor()
    c.execute("SELECT * FROM search_result")
    data = c.fetchall()
    c.close()
    conn.close()
    custom_keyboard = [[name[0].strip("\n")] for name in data]
    custom_keyboard.append(["/back"])
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.sendMessage(chat_id=update.message.chat_id, text="Please enter a name...", reply_markup=reply_markup)
    updater.start_polling()

def help(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    update.message.reply_text("/start : start the bot\n/movie_list : get the list of movies users have been searched\n/feedback : leave a feedback for the developer\n/stop : stop the bot")
    updater.start_polling()

def feedback(bot, update, args):
    if args == []:
        update.message.reply_text('Usage:\n/feedback [type your message here]')
        return
    update.message.reply_text("Thanks a lot")
    user = update.message.from_user
    print("user "+user['username']+" by id "+user['id']+" with name "+user['first_name']+' '+user['last_name']+" left a feedback for you: ")
    print(' '.join(args))
    updater.start_polling()

updater = Updater(token="653252548:AAGMGOpwXgNxd9QkjY34XCa5oXBtTNNSdw8")
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('back', back2mainlist))
dispatcher.add_handler(CommandHandler('movie_list', movie_list))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('feedback', feedback, pass_args=True))
dispatcher.add_handler(MessageHandler(Filters.text, movie_name))

updater.start_polling()
updater.idle()
