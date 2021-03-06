import datetime
from urllib.parse import unquote

import requests
import sentry_sdk
from dotenv import load_dotenv
from flask import Flask
from flask import request, redirect
from flask_talisman import Talisman
from requests.structures import CaseInsensitiveDict
from sentry_sdk.integrations.flask import FlaskIntegration

import pages
from pymongo_utils import *
from utils_server import *

load_dotenv()

CREDENTIALS = os.getenv('CREDENTIALS')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
CLIENT_ID = os.getenv('CLIENT_ID')
SENTRY_DSN_SERVER = os.getenv('SENTRY_DSN_SERVER')

BOT_TOKEN = os.getenv('BOT_TOKEN')
TRELLO_KEY = os.getenv('TRELLO_KEY')
REDIRECT_URI = os.getenv('REDIRECT_URI')
REDIRECT_URI_LOCALHOST = os.getenv('REDIRECT_URI_LOCALHOST')
IP = os.getenv('IP')
PORT = os.getenv('PORT')
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

sentry_sdk.init(
    dsn=SENTRY_DSN_SERVER,
    integrations=[FlaskIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)


app = Flask(__name__)

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)


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
    # print(j)
    refresh_token = "no_token"
    access_token = "no_token"
    if "access_token" in j:
        access_token = j["access_token"]
        # print(access_token)
    if "refresh_token" in j:
        refresh_token = j["refresh_token"]
        # print(refresh_token)
    return access_token, refresh_token


def notify_success_google_auth(chat_id, success):
    keyboard_login_trello = get_logging_trello_keyboard()
    hideBoard = telebot.types.ReplyKeyboardRemove()
    if success:
        bot.send_message(chat_id,
                         '?????????????????????? ?????????? Google ?????????????????? ??????????????.\n\n?????????????? ?????????? Trello '
                         '?????????????? ???? ???????????? ????????, ???????????????????? ???????????? ??????-??????????'
                         ' ?? ???????????????? ???????? ?????????????? ?????? ?? ???????????????? ?????????? ????????????.\n '
                         '????????????:\n\n/token 132fv6asd7da849ff',
                         reply_markup=keyboard_login_trello)
    else:
        msg = "????????????, ???? ?????? ????????????????????????????. ???????? ???????????? ???????????? ?????????????????????? ????????????, " \
              + "?????????????????? ???????????? ???????????????????? CalendarTrello ???? ????????????" \
                " https://myaccount.google.com/u/0/permissions ?? ???????????????????? ?????? ??????:\n/start"
        bot.send_message(chat_id, msg, reply_markup=hideBoard)


@app.errorhandler(404)
def page_not_found(e):
    return pages.error_page, 404


@app.route("/", methods=['GET'])
def index():
    return pages.index


@app.route("/login", methods=['GET'])
def login():
    # print('got request for ' + request.url)
    request_ip = request.environ['REMOTE_ADDR']
    chat_id = request.args.get('user')
    # send info to db
    j = {"chat_id": chat_id,
         "ip": request_ip,
         "time": datetime.datetime.now()}
    set_creds_db_data(chat_id, j)
    # get auth link and encode
    url = request.url.split("&auth_link=", 1)[1]
    url = unquote(url)
    # web_page = pages.first_page.replace("{url1}", url).replace("{url2}", url)
    return redirect(url)


@app.route("/redirect", methods=['GET'])
def redirect_mq():
    # print('redirecting')
    request_ip = request.environ['REMOTE_ADDR']
    chat_id = get_creds_db_data({"ip": request_ip}, 'chat_id')
    code = request.args.get('code')
    access_token, refresh_token = send_token_request(code)
    if access_token == 'no_token' or refresh_token == 'no_token':
        notify_success_google_auth(chat_id, False)
        return redirect("https://myaccount.google.com/u/0/permissions")
    notify_success_google_auth(chat_id, True)
    j = {"creds": {'access_token': access_token,
                   'refresh_token': refresh_token,
                   "client_id": CLIENT_ID,
                   "client_secret": CLIENT_SECRET}
         }
    set_creds_db_data(chat_id, j)
    # return pages.redirect_new_page, 200
    return redirect("https://t.me/CalendarTrello_Bot")


@app.route('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0


@app.route('/privacy_policy')
def policy():
    return pages.privacy_policy


@app.route('/terms')
def terms():
    return pages.terms


if __name__ == "__main__":
    app.debug = True
    app.run(
        ssl_context=('/etc/letsencrypt/live/fatsolko.xyz/cert.pem', '/etc/letsencrypt/live/fatsolko.xyz/privkey.pem'),
        host=IP, port=PORT)
