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
import argparse

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def get_api_key():
  with open("api_key.txt", "r") as file:
    api = file.read().strip()
  return api

def load_jokes(load_file):
   global questions
   questions = []
   global answers 
   answers = []  
   with open(load_file, 'r') as csvfile:
      #Skip header row
      for x in list(csv.reader(csvfile))[1:]:    
         questions.append(x[0])
         answers.append(x[1])             

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
   """Provide a new joke by first displaying the question part and a button to display the answer"""
   selected_joke = np.random.choice(len(questions))
   keyboard = [[InlineKeyboardButton("Tell me!", callback_data="q"+str(selected_joke))]]
   reply_markup = InlineKeyboardMarkup(keyboard)
   update.message.reply_text("Qn: " + questions[selected_joke], reply_markup=reply_markup)

def AnsButton(bot, update):
   """Show the answer part of joke and display 'Hahaha, funny', 'Meh' and 'Next joke pls!' buttons"""
   query = update.callback_query
   selected_joke = int(query.data[1:])
   keyboard = [[InlineKeyboardButton("Next joke pls!", callback_data="a")]]
   text = "Qn: " + questions[selected_joke] + "\nAns: " + answers[selected_joke]
   reply_markup = InlineKeyboardMarkup(keyboard)
   bot.edit_message_text(text, chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=reply_markup)

def QnButton(bot, update):
   """Provide a new joke by first displaying the question part and a button to display the answer"""
   query = update.callback_query
   selected_joke = np.random.choice(len(questions)) 
   keyboard = [[InlineKeyboardButton("Tell me!", callback_data="q"+str(selected_joke))]]
   text = "Qn: " + questions[selected_joke]
   reply_markup = InlineKeyboardMarkup(keyboard)
   bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
   update.effective_chat.send_message(text, reply_markup=reply_markup)

def dont_understand_msg(bot, update):
    """Handle invalid user message"""
    update.message.reply_text("Sorry, I don't understand what you just said.\nEnter /joke to hear a joke.")

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def dont_understand_cmd(bot, update):
    """Handle invalid user command"""
    invalid_cmd = update.message.text.split()[0]
    update.message.reply_text("Sorry, " + invalid_cmd + " is an invalid command.\nEnter /joke to hear a joke.")

def main():
   parser = argparse.ArgumentParser(description='Starts a Telegram bots that tell question and answer jokes')
   parser.add_argument('--load', metavar='jokes.csv', action='store', help='Loads new jokes file')
   args = parser.parse_args()

   load_file = args.load if args.load else "jokes.csv"
   load_jokes(load_file)
   logger.info("Loaded jokes from " + load_file)

   """Start the bot."""
   logger.info("Bot started")

   # Create the EventHandler and pass it your bot's token.
   updater = Updater(get_api_key())

   # Get the dispatcher to register handlers
   dp = updater.dispatcher

   # on different commands - answer in Telegram
   dp.add_handler(CommandHandler("start", start))
   dp.add_handler(CallbackQueryHandler(AnsButton, pattern="q[0-9]+"))
   dp.add_handler(CallbackQueryHandler(QnButton))
   dp.add_handler(CommandHandler("help", help))
   dp.add_handler(CommandHandler("joke", joke))
   dp.add_handler(MessageHandler(Filters.text, dont_understand_msg))
   dp.add_handler(MessageHandler(Filters.command, dont_understand_cmd))

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
