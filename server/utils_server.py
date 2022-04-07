import os
import pyshorteners
import json
import telebot
from dotenv import load_dotenv

load_dotenv()

TRELLO_KEY = os.getenv('TRELLO_KEY')


def get_logging_trello_keyboard():
    keyboard_login_trello = telebot.types.InlineKeyboardMarkup()
    auth_url_update_trello = 'https://trello.com/1/authorize?' \
                             f'key={TRELLO_KEY}&' \
                             'expiration=never&' \
                             'name=CalendarTrello&' \
                             'scope=read,write&' \
                             'response_type=token'

    short_trello = pyshorteners.Shortener()
    short_url_trello = short_trello.tinyurl.short(auth_url_update_trello)
    url_button_trello = telebot.types.InlineKeyboardButton(text="Страница авторизации Trello", url=short_url_trello)
    keyboard_login_trello.row(url_button_trello)
    return keyboard_login_trello


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""



