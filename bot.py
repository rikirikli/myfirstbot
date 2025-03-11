import telebot
from bot_logic import gen_pass, gen_emodji, flip_coin  # Импортируем функции из bot_logic
from config import token
from model import get_class
import requests
import random

# Замени 'TOKEN' на токен твоего бота
bot = telebot.TeleBot(token)

styles = {
    "кэжуал": "casual.jpg"
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой Telegram бот. Напиши команду /hello, /bye, /pass, /emodji, /coin, /joke, /help, /style, /game")

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

@bot.message_handler(commands=['joke'])
def send_joke(message):
    response = requests.get('https://official-joke-api.appspot.com/jokes/random')
    if response.status_code == 200:
        joke = response.json()
        bot.reply_to(message, f"{joke['setup']} ... {joke['punchline']}")
    else:
        bot.reply_to(message, "Не удалось получить шутку, попробуйте позже.")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "/start - приветствие\n"
        "/hello - задать вопрос\n"
        "/bye - попрощаться\n"
        "/pass - сгенерировать пароль\n"
        "/emodji - получить эмоджи\n"
        "/coin - подбросить монету\n"
        "/joke - получить случайную шутку\n"
        "/game - поиграть в игру по стилям одежды\n"
    )
    bot.reply_to(message, help_text)

def get_recommendations(style):
    if style == "спорт":
        return "Рекомендации по спортивному стилю:\n- Для тренировок выбирайте функциональные материалы, которые отводят влагу (например, полиэстер или комбинации с эластаном). \n- Рассмотрите легкие, световозвращающие куртки для занятий на улице в пасмурные дни.\n-  Выбирайте кроссовки с хорошей амортизацией и поддержкой, подходящие для вашего типа активности (бег, фитнес, повседневные прогулки).  \n- Аксессуары: рюкзаки и спортивные часы."
    elif style == "классика":
        return "Рекомендации по классическому стилю:\n- Инвестируйте в качественные основные вещи, такие как пиджак, классические брюки и универсальные рубашки. Такие вещи должны быть из натуральных тканей (шерсть, хлопок, лен).\n- Изучите сочетания цветов и узоров (например, классическая клетка или полоска), чтобы разнообразить наряды, оставаясь при этом в рамках классического стиля.\n- Обратите внимание на классические модели обуви, такие как оксфорды или дерби, выполненные из натуральной кожи. \n- Используйте галстуки, бабочки, карманы на пиджаке и запонки для добавления изящных деталей к вашему образу."
    else:
        return "Неизвестный стиль."

@bot.message_handler(commands=['style'])
def send_style_recommendations(message):
    try:
        style = message.text.split()[1]  # Получаем стиль из команды
        recommendations = get_recommendations(style.lower())  # Приводим стиль к нижнему регистру
        bot.reply_to(message, recommendations)
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите стиль (например, /style спорт или /style классика).")

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

@bot.message_handler(commands=['game'])
def start(message):
    bot.reply_to(message, "Привет! Давай играть в угадай стиль одежды! Введи /guess, чтобы начать.")

# Обработчик для начала угадывания стиля
user_data = {}

@bot.message_handler(commands=['guess'])
def guess(message):
    style, image_path = random.choice(list(styles.items()))
    bot.send_photo(chat_id=message.chat.id, photo=open(image_path, 'rb'))
    bot.reply_to(message, "Какой стиль одежды на изображении? Отвечай без ошибок и без знака: ?")
    user_data[message.from_user.id] = style  # Сохраняем правильный ответ для пользователя

@bot.message_handler(func=lambda message: True)
def handle_answer(message):
    correct_answer = user_data.get(message.from_user.id)  # Получаем правильный ответ
    if correct_answer:
        if message.text.lower() == correct_answer.lower():
            bot.reply_to(message, "Правильно! Молодец!")
            bot.reply_to(message, "Хотите попробовать угадать другую картинку /guess или вернуться в меню /help?")
        else:
            bot.reply_to(message, f"Неправильно. Правильный ответ: {correct_answer}. Введи /guess, чтобы попробовать снова.")
    else:
        bot.reply_to(message, "Сначала введи /guess, чтобы начать игру!")



# Запускаем бота
bot.polling()
