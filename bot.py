import telebot
import random

token = "465922976:AAGN6DmGRkxXZ6330eJrbuhvNvGmnTGZhUo"

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['choice'])
def choice(message):
    list = message.text.split(' ')[1:]
    print(list)
    bot.send_message(message.chat.id, 'pipka')

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): # Название функции не играет никакой роли, в принципе
    bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    bot.polling(none_stop=True)
