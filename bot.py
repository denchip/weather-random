#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a simple echo bot using decorators and webhook with flask
# It echoes any incoming text messages and does not use the polling method.

import random
import cherrypy
import telebot
import logging
import time
import config.config as config


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

# WebhookServer, process webhook calls
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            return 'HelloWorld'

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


@bot.message_handler(func=lambda message: True, content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, 'Я пока не могу общаться, используй команды')


# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

time.sleep(0.1)

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

print('WEBHOOK_URL_BASE+WEBHOOK_URL_PATH')

# Start cherrypy server
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})


cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
