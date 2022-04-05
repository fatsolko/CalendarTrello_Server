from flask import Flask
from flask import request
from requests.structures import CaseInsensitiveDict
import requests
import sys
from utils_server import *
from pages import *
from pymongo_utils import *
from urllib.parse import unquote


print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['D:\\Programming\\Python\\CalendarTrello_Server', 'D:/Programming/Python/CalendarTrello_Server'])


app = Flask(__name__)


f = open(r'D:\Programming\Python\CalendarTrello_Server\credentials.json')
credentials = json.load(f)["web"]
client_id = credentials["client_id"]
client_secret = credentials["client_secret"]
f.close()

f = open(r'D:\Programming\Python\CalendarTrello_Server\settings.json')
settings = json.load(f)
bot_token = settings["bot_token"]
redirect_url = settings["redirect_url_localhost"] #TODO settings["redirect_url"]
ip = settings["ip"]
port = settings["port"]
bot_link = settings["bot_link"]
f.close()

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

bot = telebot.TeleBot(bot_token)


def send_token_request(code):
    url = "https://oauth2.googleapis.com/token"
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    data = "code={}&client_id={}&client_secret={}&redirect_uri={}&grant_type=authorization_code" \
        .format(code, client_id, client_secret, redirect_url)
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
        bot.send_message(chat_id, 'Авторизация через Google произошла успешно.\n\nВойдите через Trello '
                                  'аккаунт по ссылке ниже, скопируйте оттуда код-токен'
                                  ' и напишите боту вставив код с командой через пробел.\n '
                                  'Пример:\n\n/token 132fv6asd7da849ff',
                         reply_markup=keyboard_login_trello)
    else:
        msg = "Похоже, вы уже логинились. Если хотите перелогиниться в этот аккаунт, " \
              + "запретите доступ приложению CalendarTrello по ссылке https://myaccount.google.com/u/0/permissions и " \
              + "попробуйте еще раз: /start"
        bot.send_message(chat_id, msg, reply_markup=hideBoard)


@app.errorhandler(404)
def page_not_found(e):
    return error_page, 404


@app.route("/", methods=['GET'])
def index():
    return first_page


@app.route("/login", methods=['GET'])
def login_mq():
    print('got request for ' + request.url)
    request_ip = request.environ['REMOTE_ADDR']
    chat_id = request.args.get('user')
    # send info to db
    j = {"chat_id": chat_id,
         "ip": request_ip}
    set_creds_data(request_ip, j)
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
    chat_id = get_creds_dbdata({"ip": request_ip}, 'chat_id')
    code = request.args.get('code')
    access_token, refresh_token = send_token_request(code)
    print(access_token)
    print(refresh_token)
    if access_token == 'no_token' or refresh_token == 'no_token':
        notify_success_google_auth(chat_id, False)
        return error_page
    notify_success_google_auth(chat_id, True)
    j = {
        'token': access_token,
        'refresh_token': refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "scopes": SCOPES
    }
    set_creds_data(request_ip, j)
    return redirect_new_page, 200


if __name__ == "__main__":
    app.run(debug=True)

