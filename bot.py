#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a simple echo bot using decorators and webhook with flask
# It echoes any incoming text messages and does not use the polling method.

import random
import flask
import telebot
import logging
import time
import config.config as config
#from models import db, User
from flask_sqlalchemy import SQLAlchemy

API_TOKEN = config.token

WEBHOOK_HOST = config.server_adress
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = config.ssl_cert_path  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = config.ssl_cert_pkey  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)

app = flask.Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % config.POSTGRES

db = SQLAlchemy(app)

class BaseModel(db.Model):
    """Base data model for all objects"""
    __abstract__ = True

    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        """Define a base way to print models"""
        return '%s(%s)' % (self.__class__.__name__, {
            column: value
            for column, value in self._to_dict().items()
        })

    def json(self):
        """
                Define a base way to jsonify models, dealing with datetime objects
        """
        return {
            column: value if not isinstance(value, datetime.date) else value.strftime('%Y-%m-%d')
            for column, value in self._to_dict().items()
        }


class Station(BaseModel, db.Model):
    """Model for the stations table"""
    __tablename__ = 'stations'

    id = db.Column(db.Integer, primary_key = True)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    spotify_id = db.Column(db.Integer)

db.init_app(app)


# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)

@bot.message_handler(commands=['choice'])
def choice(message):
    try:
        list = message.text.split(' ')[1:]
        bot.send_message(message.chat.id, list[random.randint(0, len(list)-1)])
    except:
        bot.send_message(message.chat.id, 'Ошибка ввода')

@bot.message_handler(commands=['choiceN'])
def choice(message):
    try:
        N = int(message.text.split(' ')[1])
        list = message.text.split(' ')[2:]
        if len(list) < N:
            raise 'Exception'
        random.shuffle(list)
        bot.send_message(message.chat.id, str(list[:N]))
    except:
        bot.send_message(message.chat.id, 'Ошибка ввода')

@bot.message_handler(commands=['gennum'])
def choice(message):
    try:
        a = int(message.text.split(' ')[1])
        b = int(message.text.split(' ')[2])
        bot.send_message(message.chat.id, str(random.randint(a, b)))
    except:
        bot.send_message(message.chat.id, 'Ошибка ввода')

def is_exists_user(id):
    user = User.query.filter_by(id=id).first()
    return user

@bot.message_handler(commands=['register'])
def repeat_all_messages(message):
    print(message)
    if message.chat.type == 'group':
        group_id = message.chat.id
        if is_exists_user(message.from_user.id):
            bot.send_message(message.chat.id, 'Ты уже регистрировался')
        else:
            user = User()
            user.id = message.from_user.id
            user.username = message.from_user.username
            user.spotify_id = 111
            db.session.add(user)
            db.session.commit()
            bot.send_message(message.chat.id, 'Регистрация прошла успешно')

#    bot.send_message(message.chat.id, 'Я пока не могу общаться, используй команды')

@bot.channel_post_handler(func=lambda message: True, content_types=["text"])
def channel_post(message):
    print(message)

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

time.sleep(0.1)

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Start flask server
app.run(host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
        debug=True)
