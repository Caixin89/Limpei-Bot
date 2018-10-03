#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.

This program is dedicated to the public domain under the CC0 license.

This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import logging, os, csv, threading, time
import numpy as np


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
selected_joke = None

def get_api_key():
  with open("api_key.txt", "r") as file:
    api = file.read().strip()
  return api

def load_jokes():
   global questions
   questions = []
   global answers 
   answers = []   
   file_path = "jokes.csv"
   with open(file_path, 'r') as csvfile:
      #Skip header row
      for x in list(csv.reader(csvfile))[1:]:
         questions.append(x[1])
         answers.append(x[2])
   global weights
   if os.path.isfile("weights.csv"):
      with open("weights.csv", "r") as csvfile:
         weights = np.array([float(x) for x in csvfile.readlines()])
   else:
      weights = np.array([1.0] * len(questions))

def thread_save_weights(interval):
   while True:
      with open("weights.csv", "w") as csvfile:
         csvfile.write("\n".join([str(x) for x in weights]))
      time.sleep(interval)

def start_weight_saving_thread(interval):
   thread = threading.Thread(target=thread_save_weights, args=(interval,))
   thread.daemon = True # Daemonize thread
   thread.start()  # Start the execution              

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    update.message.reply_text("Hi " +  user.first_name + """.\n
Feeling down or bored?\n
Type /joke to hear a question and answer joke!""" )

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Type /joke to hear a question and answer joke')

def joke(bot, update):
   """Tells the joke"""
   global selected_joke
   selected_joke = np.random.choice(len(questions), p=weights / np.sum(weights))
   keyboard = [[InlineKeyboardButton("Tell me!", callback_data="qn")]]
   reply_markup = InlineKeyboardMarkup(keyboard)
   update.message.reply_text("Qn: " + questions[selected_joke], reply_markup=reply_markup)

def button(bot, update):
   """Handles button logic: Either tells the question or answer part of a joke"""
   global selected_joke
   query = update.callback_query
   if query.data == "qn" and selected_joke is not None:
      keyboard = [[InlineKeyboardButton("Hahaha, funny", callback_data="upvote"), InlineKeyboardButton("Meh", callback_data="downvote")],
      [InlineKeyboardButton("Next joke pls!", callback_data="ans")]]
      text = "Qn: " + questions[selected_joke] + "\nAns: " + answers[selected_joke]
      reply_markup = InlineKeyboardMarkup(keyboard)
      bot.edit_message_text(text, chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=reply_markup)
   elif query.data == "upvote" and selected_joke is not None:
      weights[selected_joke] = weights[selected_joke] + 1
      keyboard = [[InlineKeyboardButton("Next joke pls!", callback_data="ans")]]
      text = "Qn: " + questions[selected_joke] + "\nAns: " + answers[selected_joke]
      reply_markup = InlineKeyboardMarkup(keyboard)
      bot.edit_message_text(text, chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=reply_markup)
   elif query.data == "downvote" and selected_joke is not None:
      weights[selected_joke] = max(weights[selected_joke] - 1, 0)
      keyboard = [[InlineKeyboardButton("Next joke pls!", callback_data="ans")]]
      text = "Qn: " + questions[selected_joke] + "\nAns: " + answers[selected_joke]
      reply_markup = InlineKeyboardMarkup(keyboard)
      bot.edit_message_text(text, chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=reply_markup)
   elif query.data == "ans":
      selected_joke = np.random.choice(len(questions), p=weights / np.sum(weights))
      keyboard = [[InlineKeyboardButton("Tell me!", callback_data="qn")]]
      text = "Qn: " + questions[selected_joke]
      reply_markup = InlineKeyboardMarkup(keyboard)
      bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
      update.effective_chat.send_message(text, reply_markup=reply_markup)

def dont_understand(bot, update):
    """Echo the user message."""
    update.message.reply_text("Sorry, I dont understand what you just said.\nEnter /joke to hear a joke.")

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    """Start the bot."""
    logger.info("Bot started")
    #Load jokes
    load_jokes()
    logger.info("Jokes loaded")
    #Start saving weights every 5 minutes
    start_weight_saving_thread(5 * 60)
    logger.info("Start saving weights every 5 minutes")

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(get_api_key())

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("joke", joke))
    dp.add_handler(MessageHandler(Filters.text, dont_understand))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
