from flask import Flask
from flask import request
from requests.structures import CaseInsensitiveDict
import requests
from utils_server import *
from pages import *
from pymongo_utils import *
from urllib.parse import unquote
from flask_talisman import Talisman
from dotenv import load_dotenv
load_dotenv()

CREDENTIALS = os.getenv('CREDENTIALS')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
CLIENT_ID = os.getenv('CLIENT_ID')

BOT_TOKEN = os.getenv('BOT_TOKEN')
TRELLO_KEY = os.getenv('TRELLO_KEY')
REDIRECT_URI = os.getenv('REDIRECT_URI')
REDIRECT_URI_LOCALHOST = os.getenv('REDIRECT_URI_LOCALHOST')
IP = os.getenv('IP')
PORT = os.getenv('PORT')
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

app = Flask(__name__)
Talisman(app, content_security_policy=None)

bot = telebot.TeleBot(BOT_TOKEN)


def send_token_request(code):
    url = "https://oauth2.googleapis.com/token"
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    data = f"code={code}" \
           f"&client_id={CLIENT_ID}" \
           f"&client_secret={CLIENT_SECRET}" \
           f"&redirect_uri={REDIRECT_URI}" \
           f"&grant_type=authorization_code"
    response = requests.post(url, headers=headers, data=data)
    j = response.json()
    print(j)
    refresh_token = "no_token"
    access_token = "no_token"
    if "access_token" in j:
        access_token = j["access_token"]
        print(access_token)
    if "refresh_token" in j:
        refresh_token = j["refresh_token"]
        print(refresh_token)
    return access_token, refresh_token


def notify_success_google_auth(chat_id, success):
    keyboard_login_trello = get_logging_trello_keyboard()
    hideBoard = telebot.types.ReplyKeyboardRemove()
    if success:
        bot.send_message(chat_id,
                         'Авторизация через Google произошла успешно.\n\nВойдите через Trello '
                         'аккаунт по ссылке ниже, скопируйте оттуда код-токен'
                         ' и напишите боту вставив код с командой через пробел.\n '
                         'Пример:\n\n/token 132fv6asd7da849ff',
                         reply_markup=keyboard_login_trello)
    else:
        msg = "Похоже, вы уже логинились. Если хотите перелогиниться в этот аккаунт, " \
              + "запретите доступ приложению CalendarTrello по ссылке" \
                " https://myaccount.google.com/u/0/permissions и попробуйте еще раз: /start"
        bot.send_message(chat_id, msg, reply_markup=hideBoard)


@app.errorhandler(404)
def page_not_found(e):
    return error_page, 404


@app.route("/", methods=['GET'])
def index():
    print("op")
    return first_page


@app.route("/login", methods=['GET'])
def login_mq():
    print('got request for ' + request.url)
    request_ip = request.environ['REMOTE_ADDR']
    chat_id = request.args.get('user')
    # send info to db
    j = {"chat_id": chat_id,
         "ip": request_ip}
    set_creds_db_data(request_ip, j)
    # get auth link and encode
    url = request.url.split("&auth_link=", 1)[1]
    url = unquote(url)
    web_page = first_page.replace("{url1}", url).replace("{url2}", url)
    print('login done')
    return web_page


@app.route("/redirect", methods=['GET'])
def redirect_mq():
    print('redirecting')
    request_ip = request.environ['REMOTE_ADDR']
    chat_id = get_creds_db_data({"ip": request_ip}, 'chat_id')
    code = request.args.get('code')
    access_token, refresh_token = send_token_request(code)
    if access_token == 'no_token' or refresh_token == 'no_token':
        notify_success_google_auth(chat_id, False)
        return error_page
    notify_success_google_auth(chat_id, True)
    j = {"creds": {'access_token': access_token,
                    'refresh_token': refresh_token,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET}
         }
    set_creds_db_data(request_ip, j)
    return redirect_new_page, 200


if __name__ == "__main__":
    app.debug = True
    app.run(ssl_context=('/etc/letsencrypt/live/fatsolko.xyz/fullchain.pem', '/etc/letsencrypt/live/fatsolko.xyz/privkey.pem'), host=IP, port=PORT)
