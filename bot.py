import telebot
import random
import config

bot = telebot.TeleBot(config.token)

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


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, 'Я пока не могу общаться, используй команды')

if __name__ == '__main__':
    bot.polling(none_stop=True)
