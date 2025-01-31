import telebot
from bot_logic import gen_pass, gen_emodji, flip_coin  # Импортируем функции из bot_logic
from config import token
from model import get_class

# Замени 'TOKEN' на токен твоего бота
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой Telegram бот. Напиши команду /hello, /bye, /pass, /emodji или /coin  ")

@bot.message_handler(commands=['hello'])
def send_hello(message):
    bot.reply_to(message, "Привет! Как дела?")

@bot.message_handler(commands=['bye'])
def send_bye(message):
    bot.reply_to(message, "Пока! Удачи!")

@bot.message_handler(commands=['pass'])
def send_password(message):
    password = gen_pass(10)  # Устанавливаем длину пароля, например, 10 символов
    bot.reply_to(message, f"Вот твой сгенерированный пароль: {password}")

@bot.message_handler(commands=['emodji'])
def send_emodji(message):
    emodji = gen_emodji()
    bot.reply_to(message, f"Вот эмоджи': {emodji}")

@bot.message_handler(commands=['coin'])
def send_coin(message):
    coin = flip_coin()
    bot.reply_to(message, f"Монетка выпала так: {coin}")



@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    # Проверяем, есть ли фотографии
    if not message.photo:
        return bot.send_message(message.chat.id, "Вы забыли загрузить картинку :(")

    # Получаем файл и сохраняем его
    file_info = bot.get_file(message.photo[-1].file_id)
    file_name = file_info.file_path.split('/')[-1]
    
    # Загружаем файл и сохраняем
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)


        result = get_class(model_path='keras_model.h5',labels_path='labels.txt', image_path=file_name)
        bot.send_message(message.chat.id, result)

# Запускаем бота
bot.polling()
