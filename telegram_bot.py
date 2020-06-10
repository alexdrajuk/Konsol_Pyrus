import lib
import telebot

from settings import TELEGRAM_BOT_TOKEN

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=['registration'])
def register_user(message):
    bot.send_message(message.chat.id, 'Укажите email который использовался при регистрации в Pyrus')
    bot.register_next_step_handler(message, process_registration)


def process_registration(message):
    user = lib.fetch_user_info(message.text.lower())
    if not user:
        bot.send_message(message.chat.id, f'Пользователь с email {message.text} не найден')
        return
    if dict(user).get('chat_id') == str(message.chat.id):
        bot.send_message(message.chat.id, f'Пользователь с email {message.text} уже зарегистрирован')
        return

    query_ok = lib.register_chat_id(message.text.lower(), message.chat.id)
    if query_ok:
        bot.send_message(message.chat.id, 'Ура! Вы зарегистрированы!\nГотовьтесь получать штрафы')


if __name__ == '__main__':
    bot.polling()
