# Limpei Bot
A Telegram bot that tells question and answer jokes. 
It is written in Python and utilized the python-telegram-bot library 
from https://github.com/python-telegram-bot/python-telegram-bot 
and jokes dataset from https://www.kaggle.com/jiriroz/qa-jokes.

## Instructions
Enter `python limpei_bot.py --load jokes.csv` for first startup to load jokes from jokes.csv.   
For subsequent startups, just run `python limpei_bot.py` on the server.   
To reset the learnt weights of all jokes before starting up, enter `python limpei_bot.py --reset`.   
To terminate the process, enter Ctrl+C.

## Interacting with the bot
1. Enter /joke to start
2. The question part of the joke will be displayed with a button for user to press to see the answer part.
3. After clicking the answer part of the joke, the answer will appear and a button to display the next joke will also appear. There are also buttons to upvote("Haha, funny") or downvote("Meh") a joke.
