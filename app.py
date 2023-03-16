# -*- coding: utf-8 -*-
import random
import Constant_File as Keys
from telebot import *
from telebot.types import *
from ConnectDB import *
import re
from apscheduler.schedulers.background import BackgroundScheduler
from math import *


TOKEN = Keys.API_KEY
bot = telebot.TeleBot(TOKEN)
scheduler = BackgroundScheduler()


def send_celebration():
    # bot.send_message(256266717, 'Я тут пінгую вас')
    ShowChats()
    # bot.send_video(chat_id=-792145823, video=open('ІнтроКурятника.mp4', 'rb'), supports_streaming=True)
    # bot.send_video(chat_id=-792145823, video=open('IMG_3768.MOV', 'rb'), supports_streaming=True)
    # bot.send_audio(chat_id=-792145823, audio=open('audio_2022-08-20_23-49-24.MP3', 'rb'))


scheduler.add_job(send_celebration, 'interval', minutes=29, seconds=59)
scheduler.start()
# server = Flask(__name__)


@bot.message_handler(commands=['start'])
def start(message):
    welcome = getWelcomeAccoringToHours()
    print(welcome)
    bot.reply_to(message, welcome + " пані та панове, я бот, який буде керувати вашими боргами. Для початку перевірте чи є "
                          "у "
                          "вас взагалі кошти (І чи не віддали ви свій под бившим і не хочете повертати гроші), щоб я "
                          "міг хоч щось порахувати")


def getCurrentHour():
    utchour = datetime.now()
    print("Utc hour" + str(datetime.now()))
    if utchour.hour == 21:
        current_hour = 23
    elif utchour.hour == 22:
        current_hour = 24
    elif utchour.hour == 23:
        current_hour = 1
    elif utchour.hour == 24:
        current_hour = 2
    else:
        current_hour = utchour.hour + 2
    print(current_hour)
    return current_hour


def getWelcomeAccoringToHours():
    currentHour = getCurrentHour()
    if (currentHour >= 4) and (currentHour < 12):
        return "Доброго ранку"
    elif (currentHour >= 12) and (currentHour < 19):
        return "Добрий день"
    elif (currentHour >= 19) and (currentHour < 24):
        return "Доброго вечора"
    elif (currentHour >= 0) and (currentHour < 4):
        return "Доброї ночі"
    else:
        return "Мої Вітання"


def getFarewellAccoringToHours():
    currentHour = getCurrentHour()
    if (currentHour >= 4) and (currentHour < 12):
        return "Хорошого ранку!"
    elif (currentHour >= 12) and (currentHour < 19):
        return "Хорошого дня!"
    elif (currentHour >= 19) and (currentHour < 24):
        return "Хорошого вечора!"
    elif (currentHour >= 0) and (currentHour < 4):
        return "Хорошої ночі!"
    else:
        return "До зустрічі!"


# @bot.message_handler(commands=['getinfo'])
# def getinfo(message):
#     user_first_name = str(message.from_user.first_name)
#     user_last_name = str(message.from_user.last_name)
#     bot.reply_to(message, f'Hello {user_first_name} {user_last_name}')


# @bot.message_handler(commands=['button'])
# def button_message(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     item1 = types.KeyboardButton("Увійти в паті")
#     item2 = types.KeyboardButton("Показати список Masters")
#     markup.add(item1)
#     markup.add(item2)
#     msg = bot.reply_to(message, 'Виберіть,що вам потрібно', reply_markup=markup)
#     bot.register_next_step_handler(msg, response)


@bot.message_handler(commands=['entertheparty'])
def enter(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_first_name = str(message.from_user.first_name)
    user_last_name = str(message.from_user.last_name)
    user_name = str(message.from_user.username)
    if user_first_name == 'None' and user_last_name == 'None':
        FullName = user_name
    elif user_first_name == 'None':
        FullName = user_last_name
    elif user_last_name == 'None':
        FullName = user_first_name
    else:
        FullName = user_first_name + ' ' + user_last_name
    if user_name == 'None':
        result_message = "Для початку створіть собі Username та повторіть спробу: /entertheparty"
    elif CheckUser(user_id, chat_id):
        result_message = 'Ви вже в паті'
    else:
        InsertData(chat_id, user_id, FullName, user_name)
        result_message = 'Ви успішно додані до бази даних: ' + '\n' + 'Ваш Нікнейм: ' + user_name + '\n' + \
                         'Вас звати: ' + FullName
    bot.reply_to(message, result_message)


@bot.message_handler(commands=['enterthecharity'])
def setdebt(message):
    userName = message.from_user.username
    if userName in GetListPersonCharity():
         bot.reply_to(message, 'Ви уже берете участь в зборі!')
    elif userName == "None":
        bot.reply_to(message, 'Спочатку додайте свій нікнейм в телеграмі.')
    else:
        joinCharity(userName)
        bot.reply_to(message, 'Вітаю, ви долучились до збору!')


@bot.message_handler(commands=['leavethecharity'])
def setdebt(message):
    userName = message.from_user.username
    if userName in GetListPersonCharity():
        leaveCharity(userName)
        bot.reply_to(message, 'Ви покинули збір!' + "\n\n" + getFarewellAccoringToHours())
    elif userName == "None":
        bot.reply_to(message, 'Спочатку додайте свій нікнейм в телеграмі.')
    else:
        bot.reply_to(message, 'Ви не долучались до збору!')


@bot.message_handler(commands=['leavethecharity'])
def setdebt(message):
    if message.from_user.id == 256266717:
        userName = message.from_user.username
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item3 = types.KeyboardButton("🛑 Відмінити операцію!")
        markup.row(item3)
        msg = bot.reply_to(message, 'Надішліть мат, який хочете добавити', reply_markup=markup)
        bot.register_next_step_handler(msg, addmat, userName)


@bot.message_handler(commands=['showdata'])
def showdata(message):
    bot.reply_to(message, ShowData(message))


@bot.message_handler(commands=['addmat'])
def setdebt(message):
    if message.from_user.id == 256266717:
        userName = message.from_user.username
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item3 = types.KeyboardButton("🛑 Відмінити операцію!")
        markup.row(item3)
        msg = bot.reply_to(message, 'Надішліть мат, який хочете добавити', reply_markup=markup)
        bot.register_next_step_handler(msg, addmat, userName)


@bot.message_handler(commands=['changelimit'])
def changelimit(message):
    if CheckUser(message.from_user.id, message.chat.id):
        if CheckIfChatHaveVoting(message.chat.id):
            bot.reply_to(message,
                         "На даний момент голосування уже проходить, знайти його можна у закріплених повідомленнях.")
        else:
            userName = message.from_user.username
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item3 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item3)
            msg = bot.reply_to(message, 'Вкажіть новий ліміт ( число )', reply_markup=markup)
            bot.register_next_step_handler(msg, vote, userName)
    else:
        bot.reply_to(message, f'Для початку увійдіть в гільдію: команда /entertheparty')


def vote(message, userName):
    list = checkValidationString(message.text)
    if userName == message.from_user.username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif list[0]:
            number = round(float(list[1]))
            if number == getDebtLimitValue(message.chat.id):
                msg = bot.reply_to(message,
                                   "Ви ввели значення ліміту, який і так встановлений, спробуйте інше число.")
                bot.register_next_step_handler(msg, vote, userName)
            else:
                CreateVoting(message.chat.id, number, userName)
                markup = types.InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(
                    f"За ( {str(getVotesYesByChatId(message.chat.id))} / {getCountOfActiveUsers(message.chat.id)} )",
                    callback_data="yes"))
                markup.add(InlineKeyboardButton(
                    f"Проти ( {str(getVotesNoByChatId(message.chat.id))} / {getCountOfActiveUsers(message.chat.id)} )",
                    callback_data="no"))
                msg = bot.reply_to(message, "ㅤ", reply_markup=types.ReplyKeyboardRemove())
                bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
                msg = bot.reply_to(message,
                                   f"Користувач @{userName} хоче встановити новий ліміт боргу: {number} грн при поточному - {getDebtLimitValue(message.chat.id)} грн. Прошу проголосувати. Рішення буде ухвалене або відхилене за наявності абсолютної більшості ( {str(floor(int(getCountOfActiveUsers(message.chat.id)) * 0.5) + 1)} )",
                                   reply_markup=markup)
                InsertMessageId(msg.chat.id, msg.message_id)
                bot.pin_chat_message(chat_id=msg.chat.id, message_id=msg.message_id, disable_notification=True)
        else:
            msg = bot.reply_to(message, "Вираз повинен містити лише цифри, арифметичні операції та дужки, спробуйте ще раз.")
            bot.register_next_step_handler(msg, vote, userName)
    else:
        msg = bot.reply_to(message, f"Зараз черга @{userName}.")
        bot.register_next_step_handler(msg, vote, userName)


@bot.callback_query_handler(func=lambda call: call.data.startswith("yes"))
def callback_query(call: types.CallbackQuery):
    try:
        markup = types.InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
            f"За ( {str(getVotesYesByChatId(call.message.chat.id))} / {getCountOfActiveUsers(call.message.chat.id)} )",
            callback_data="yes"))
        markup.add(InlineKeyboardButton(
            f"Проти ( {str(getVotesNoByChatId(call.message.chat.id))} / {getCountOfActiveUsers(call.message.chat.id)} )",
            callback_data="no"))
        bot.edit_message_text(
            text=f"Користувач @{getCreatorByChatId(call.message.chat.id)} хоче встановити новий ліміт боргу: {getPurposeByChatId(call.message.chat.id)} грн при поточному - {getDebtLimitValue(call.message.chat.id)} грн. Прошу проголосувати. Рішення буде ухвалене або відхилене за наявності абсолютної більшості ( {str(floor(int(getCountOfActiveUsers(call.message.chat.id)) * 0.5) + 1)} )",
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    except:
        print("Same text")
    if CheckUser(call.from_user.id, call.message.chat.id):
        if checkIfPersonVotes(call.from_user.id, call.message.chat.id):
            bot.reply_to(call.message,
                         f'@{call.from_user.username}, ви вже проголосували')
        else:
            addYesVote(call.from_user.id, call.message.chat.id)
            markup = types.InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(
                f"За ( {str(getVotesYesByChatId(call.message.chat.id))} / {getCountOfActiveUsers(call.message.chat.id)} )",
                callback_data="yes"))
            markup.add(InlineKeyboardButton(
                f"Проти ( {str(getVotesNoByChatId(call.message.chat.id))} / {getCountOfActiveUsers(call.message.chat.id)} )",
                callback_data="no"))
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=markup)
            if getVotesYesByChatId(call.message.chat.id) == floor(
                    int(getCountOfActiveUsers(call.message.chat.id)) * 0.5) + 1:
                msg = bot.send_message(call.message.chat.id,
                                       f"Рішення ухвалено. Голосів за: {getVotesYesByChatId(call.message.chat.id)} / Голосів проти: {getVotesNoByChatId(call.message.chat.id)}, тепер новий ліміт боргу буде становити {getPurposeByChatId(call.message.chat.id)} грн")
                setNewDebtLimitValue(call.message.chat.id, float(getPurposeByChatId(call.message.chat.id)))
                deleteVoting(msg.chat.id)
                bot.pin_chat_message(chat_id=msg.chat.id, message_id=msg.message_id, disable_notification=True)
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            elif getVotesYesByChatId(call.message.chat.id) + getVotesNoByChatId(
                    call.message.chat.id) == getCountOfActiveUsers(call.message.chat.id):
                msg = bot.send_message(call.message.chat.id,
                                       f"Рішення не ухвалено через рівну кількість голосів. Голосів за: {getVotesYesByChatId(call.message.chat.id)} / Голосів проти: {getVotesNoByChatId(call.message.chat.id)}, ліміт боргу залишатиметься {getDebtLimitValue(call.message.chat.id)} грн")
                deleteVoting(msg.chat.id)
                bot.pin_chat_message(chat_id=msg.chat.id, message_id=msg.message_id, disable_notification=True)
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    else:
        bot.send_message(call.message.chat.id, f'@{call.from_user.username} ,для початку увійдіть в гільдію: команда /entertheparty')


@bot.callback_query_handler(func=lambda call: call.data.startswith("no"))
def callback_query(call: types.CallbackQuery):
    try:
        markup = types.InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
            f"За ( {str(getVotesYesByChatId(call.message.chat.id))} / {getCountOfActiveUsers(call.message.chat.id)} )",
            callback_data="yes"))
        markup.add(InlineKeyboardButton(
            f"Проти ( {str(getVotesNoByChatId(call.message.chat.id))} / {getCountOfActiveUsers(call.message.chat.id)} )",
            callback_data="no"))
        bot.edit_message_text(
            text=f"Користувач @{getCreatorByChatId(call.message.chat.id)} хоче встановити новий ліміт боргу: {getPurposeByChatId(call.message.chat.id)} грн при поточному - {getDebtLimitValue(call.message.chat.id)} грн. Прошу проголосувати. Рішення буде ухвалене або відхилене за наявності абсолютної більшості ( {str(floor(int(getCountOfActiveUsers(call.message.chat.id)) * 0.5) + 1)} )",
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    except:
        print("Same text")
    if CheckUser(call.from_user.id, call.message.chat.id):
        if checkIfPersonVotes(call.from_user.id, call.message.chat.id):
            msg = bot.reply_to(call.message,
                               f'@{call.from_user.username}, ви вже проголосували')
        else:
            addNoVote(call.from_user.id, call.message.chat.id)
            markup = types.InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(
                f"За ( {str(getVotesYesByChatId(call.message.chat.id))} / {getCountOfActiveUsers(call.message.chat.id)} )",
                callback_data="yes"))
            markup.add(InlineKeyboardButton(
                f"Проти ( {str(getVotesNoByChatId(call.message.chat.id))} / {getCountOfActiveUsers(call.message.chat.id)} )",
                callback_data="no"))
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=markup)
            if getVotesNoByChatId(call.message.chat.id) == floor(
                    int(getCountOfActiveUsers(call.message.chat.id)) * 0.5) + 1:
                msg = bot.send_message(call.message.chat.id,
                                       f"Рішення не ухвалено. Голосів проти: {str(getVotesNoByChatId(call.message.chat.id))} / Голосів за: {str(getVotesYesByChatId(call.message.chat.id))}, ліміт боргу залишатиметься {getDebtLimitValue(call.message.chat.id)}  грн")
                deleteVoting(msg.chat.id)
                bot.pin_chat_message(chat_id=msg.chat.id, message_id=msg.message_id, disable_notification=True)
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            elif getVotesYesByChatId(call.message.chat.id) + getVotesNoByChatId(
                    call.message.chat.id) == getCountOfActiveUsers(call.message.chat.id):
                msg = bot.send_message(call.message.chat.id,
                                       f"Рішення не ухвалено через рівну кількість голосів. Голосів за: {getVotesYesByChatId(call.message.chat.id)} / Голосів проти: {getVotesNoByChatId(call.message.chat.id)}, ліміт боргу залишатиметься {getDebtLimitValue(call.message.chat.id)}  грн")
                deleteVoting(msg.chat.id)
                bot.pin_chat_message(chat_id=msg.chat.id, message_id=msg.message_id, disable_notification=True)
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    else:
        bot.send_message(call.message.chat.id, f'@{call.from_user.username} ,для початку увійдіть в гільдію: команда /entertheparty')


def addmat(message, userName):
    maxNumOfSymsForAnegdot = 255
    if userName == message.from_user.username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif len(str(message.text)) <= maxNumOfSymsForAnegdot:
            if checkIfExistsMat(str(message.text)):
                msg = bot.reply_to(message, "Мат уже існує, спробуйте надіслати новий!")
                bot.register_next_step_handler(msg, addmat, userName)
            else:
                addMatToDb(message)
                bot.reply_to(message, "Мат успішно доданий!", reply_markup=types.ReplyKeyboardRemove())
    else:
        msg = bot.reply_to(message, f"Зараз черга @{userName}.")
        bot.register_next_step_handler(msg, addmat, userName)


@bot.message_handler(commands=['removemat'])
def setdebt(message):
    if message.from_user.id == 256266717:
        userName = message.from_user.username
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item3 = types.KeyboardButton("🛑 Відмінити операцію!")
        markup.row(item3)
        msg = bot.reply_to(message, 'Надішліть мат, який хочете видалити', reply_markup=markup)
        bot.register_next_step_handler(msg, removeMat, userName)


def removeMat(message, userName):
    maxNumOfSymsForAnegdot = 255
    if userName == message.from_user.username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif len(str(message.text)) <= maxNumOfSymsForAnegdot:
            if not checkIfExistsMat(str(message.text)):
                msg = bot.reply_to(message, "Такого мата не існує, спробуйте надіслати ще раз!")
                bot.register_next_step_handler(msg, removeMat, userName)
            else:
                removeMatFromDb(message)
                bot.reply_to(message, "Мат успішно видалений!", reply_markup=types.ReplyKeyboardRemove())
    else:
        msg = bot.reply_to(message, f"Зараз черга @{userName}.")
        bot.register_next_step_handler(msg, removeMat, userName)





@bot.message_handler(commands=['setdebt'])
def setdebt(message):
    if CheckUser(message.from_user.id, message.chat.id):
        userName = message.from_user.username
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("✅ Так")
        item2 = types.KeyboardButton("⛔ Ні")
        item3 = types.KeyboardButton("🛑 Відмінити операцію")
        markup.row(item1, item2)
        markup.row(item3)
        msg = bot.reply_to(message, 'Усі люди скидались?', reply_markup=markup)
        bot.register_next_step_handler(msg, responsesum, userName)
    else:
        bot.reply_to(message, f'Для початку увійдіть в гільдію: команда /entertheparty')


@bot.message_handler(commands=['removedebt'])
def removedebt(message):
    if CheckUser(message.from_user.id, message.chat.id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item3 = types.KeyboardButton("🛑 Відмінити операцію")
        markup.row(item3)
        userName = message.from_user.username
        msg = bot.reply_to(message, 'Кому ви хочете видалити борг? (Введіть нікнейм з допомогою @) ', reply_markup=markup)
        bot.register_next_step_handler(msg, responseRemoveDebt, userName)
    else:
        bot.reply_to(message, f'Для початку увійдіть в гільдію: команда /entertheparty')


def responseRemoveDebt(message, userName):
    if message.from_user.username == userName:
        if message.text == "🛑 Відмінити операцію":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            PersonUserName = message.text
            PersonUserName = str(PersonUserName).replace("@", '')
            PersonUserName = str(PersonUserName).replace(" ", '')
            if not userName == PersonUserName:
                if checkIfPersonHaveDebtFromPayer(PersonUserName, message.chat.id, userName):
                    PersonId = getUserIdByUserName(PersonUserName)
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = types.KeyboardButton("💰 Усі кошти")
                    item2 = types.KeyboardButton("💵 Конкретну кількість")
                    item3 = types.KeyboardButton("🛑 Відмінити операцію")
                    markup.row(item1, item2)
                    markup.row(item3)
                    msg = bot.reply_to(message, 'Видалити весь борг чи конкретну кількість?', reply_markup=markup)
                    bot.register_next_step_handler(msg, choiceDelete, userName, PersonId)
                else:
                    msg = bot.reply_to(message,
                                       'Користувач, якому ви хочете видалити борг, не є у вашому патті, або він вам нічого не був винен. Спробуйте ще раз')
                    bot.register_next_step_handler(msg, responseRemoveDebt, userName)
            else:
                msg = bot.reply_to(message,
                                   'Видаляти самому собі борг - не найкраща ідея. Спробуйте ще раз')
                bot.register_next_step_handler(msg, responseRemoveDebt, userName)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на видалення має @' + userName)
        bot.register_next_step_handler(msg, responseRemoveDebt, userName)


def choiceDelete(message, userName, PersonId):
    if message.from_user.username == userName:
        if message.text == "💰 Усі кошти":
            if CheckIfZeroDebt(PersonId, message.chat.id, userName):
                msg = bot.reply_to(message, 'Ви і так витрясли все з нього!', reply_markup=types.ReplyKeyboardRemove())
            else:
                RemoveDebt(PersonId, message.chat.id, userName)
                msg = bot.reply_to(message, 'Борг успішно видалено' + '\n' + '\n' + ShowData(message), reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "💵 Конкретну кількість":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item3 = types.KeyboardButton("🛑 Відмінити операцію")
            markup.row(item3)
            msg = bot.reply_to(message, 'Введіть кількість коштів, яку хочете списати з боргу.', reply_markup=markup)
            bot.register_next_step_handler(msg, removeExactDebt, userName, PersonId)
        elif message.text == "🛑 Відмінити операцію":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.register_next_step_handler(message, choiceDelete, userName, PersonId)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на видалення має @' + userName)
        bot.register_next_step_handler(msg, choiceDelete, userName, PersonId)


def removeExactDebt(message, userName, PersonId):
    if message.from_user.username == userName:
        if message.text == "🛑 Відмінити операцію":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            list = checkValidationString(message.text)
            if list[0]:
                try:
                    debtValue = float(list[1])
                    if CheckIfZeroDebt(PersonId, message.chat.id, userName):
                        msg = bot.reply_to(message, 'Ви і так витрясли все з нього!',
                                           reply_markup=types.ReplyKeyboardRemove())
                    elif CheckMinusDebt(PersonId, message.chat.id, debtValue, userName):
                        msg = bot.reply_to(message,
                                           'Воу-воу, ви хочете видалити більше, чим вам винні. Введіть кількість коштів ще раз, яку хочете списати з боргу.')
                        bot.register_next_step_handler(msg, removeExactDebt, userName, PersonId)
                    else:
                        RemoveExactDebt(PersonId, message.chat.id, debtValue, userName)
                        msg = bot.reply_to(message, 'Борг успішно відняно.' + '\n' + '\n' + ShowData(message), reply_markup=types.ReplyKeyboardRemove())
                except:
                    msg = bot.reply_to(message,
                                       list[2])
                    bot.register_next_step_handler(msg, removeExactDebt, userName, PersonId)
            else:
                msg = bot.reply_to(message,
                                   list[2])
                bot.register_next_step_handler(msg, removeExactDebt, userName, PersonId)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на видалення має @' + userName + " Просимо його ввести кількість коштів, яку потрібно списати з боргу.")
        bot.register_next_step_handler(msg, removeExactDebt, userName, PersonId)


@bot.message_handler(commands=['addcards'])
def addcards(message):
    if CheckUser(message.from_user.id, message.chat.id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item3 = types.KeyboardButton("🛑 Відмінити операцію")
        markup.row(item3)
        userName = message.from_user.username
        msg = bot.reply_to(message, 'Впишіть ваші реквізити', reply_markup=markup)
        bot.register_next_step_handler(msg, addcardtodb, userName)
    else:
        bot.reply_to(message, f'Для початку увійдіть в гільдію: команда /entertheparty')


@bot.message_handler(commands=['deletecards'])
def deletecards(message):
    if CheckUser(message.from_user.id, message.chat.id):
        userName = message.from_user.username
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("✅ Так")
        item2 = types.KeyboardButton("⛔ Ні")
        item3 = types.KeyboardButton("🛑 Відмінити операцію")
        markup.row(item1, item2)
        markup.row(item3)
        msg = bot.reply_to(message, 'Видалити ваші реквізити?', reply_markup=markup)
        bot.register_next_step_handler(msg, deletecard, userName)
    else:
        bot.reply_to(message, f'Для початку увійдіть в гільдію: команда /entertheparty')


def deletecard(message, userName):
    if message.from_user.username == userName:
        if message.text == "✅ Так":
            if CheckUser(message.from_user.id, message.chat.id):
                if GetCard(str(message.from_user.id), str(message.chat.id)) == 'Не додано':
                    bot.reply_to(message, 'Ви ще не додавали реквізитів.', reply_markup=types.ReplyKeyboardRemove())
                else:
                    DeleteCards(message)
                    bot.reply_to(message, 'Реквізити успішно видалено.', reply_markup=types.ReplyKeyboardRemove())
            else:
                bot.reply_to(message, f'Для початку увійдіть в гільдію: команда /entertheparty',
                             reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "⛔ Ні":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "🛑 Відмінити операцію":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.register_next_step_handler(message, deletecard, userName)
    else:
        msg = bot.reply_to(message, "@" + userName + " має індульгенцію видаляти свою картку.")
        bot.register_next_step_handler(msg, deletecard, userName)


def addcardtodb(message, userName):
    if message.from_user.username == userName:
        if message.text == "🛑 Відмінити операцію":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            regex = re.compile('[a-zA-Zа-яА-Я].+[:]\\d{4}\\d{4}\\d{4}\\d{4}$')
            fullstring = str(message.text).replace(" ", "")
            match = regex.match(fullstring)
            print(match)
            if match is None:
                msg = bot.reply_to(message,
                                   'Не коректний запис. Приклад: Моно : 9898 8475 3984 4895 (Можна додати лише один '
                                   'реквізит за раз). Спробуйте ще раз')
                bot.register_next_step_handler(msg, addcardtodb, userName)
            else:
                if CheckUser(message.from_user.id, message.chat.id):
                    if CheckCardPersonsDoubleInfo(message.from_user.id, message.chat.id, message.text):
                        msg = bot.reply_to(message,
                                           f'\t\t\tДані реквізити вже існують у іншої людини, спробуйте додати іншу картку')
                        bot.register_next_step_handler(msg, addcardtodb, userName)
                    elif CheckCardDoubleInfo(message.from_user.id, message.chat.id, message.text):
                        msg = bot.reply_to(message, f'\t\t\tДані реквізити вже існують, спробуйте додати іншу картку')
                        bot.register_next_step_handler(msg, addcardtodb, userName)
                    else:
                        AddCard(message.chat.id, message.from_user.id, message.text)
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        item1 = types.KeyboardButton("✅ Так")
                        item2 = types.KeyboardButton("⛔ Ні")
                        item3 = types.KeyboardButton("🛑 Відмінити операцію")
                        markup.row(item1, item2)
                        markup.row(item3)
                        msg = bot.reply_to(message, 'Хочете додати ще одну картку?', reply_markup=markup)
                        bot.register_next_step_handler(msg, responsecard, userName)
                else:
                    bot.reply_to(message, f'Для початку увійдіть в гільдію: команда /entertheparty',
                                 reply_markup=types.ReplyKeyboardRemove())
    else:
        msg = bot.reply_to(message, 'Тільки @' + userName + " має право надіслати свої реквізити.")
        bot.register_next_step_handler(msg, addcardtodb, userName)


def responsecard(message, userName):
    if message.from_user.username == userName:
        if message.text == "✅ Так":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item3 = types.KeyboardButton("🛑 Відмінити операцію")
            markup.row(item3)
            msg = bot.reply_to(message, 'Впишіть ваші реквізити', reply_markup=markup)
            bot.register_next_step_handler(msg, addcardtodb, userName)
            print(msg.text)
        elif message.text == "⛔ Ні":
            bot.reply_to(message, f'\t\t\tРеквізити додано' + '\n' + ShowData(message),
                         reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "🛑 Відмінити операцію":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.register_next_step_handler(message, responsecard, userName)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на відповідь має лише @' + userName)
        bot.register_next_step_handler(msg, responsecard, userName)


def responsesum(message, userName):
    if message.from_user.username == userName:
        if message.text == "✅ Так":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item3 = types.KeyboardButton("🛑 Відмінити операцію")
            markup.row(item3)
            msg = bot.reply_to(message, 'Впишіть кількість коштів', reply_markup=markup)
            bot.register_next_step_handler(msg, add_sum, userName)
            print(msg.text)
        elif message.text == "⛔ Ні":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("✅ Так")
            item2 = types.KeyboardButton("⛔ Ні")
            item3 = types.KeyboardButton("🛑 Відмінити операцію")
            markup.row(item1, item2)
            markup.row(item3)
            msg = bot.reply_to(message, 'Частина людей з групи скидалась?', reply_markup=markup)
            bot.register_next_step_handler(msg, response_sum_exact, userName)
        elif message.text == "🛑 Відмінити операцію":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.register_next_step_handler(message, responsesum, userName)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на відповідь має лише @' + userName)
        bot.register_next_step_handler(msg, responsesum, userName)


@bot.message_handler(content_types=['text'])
def response(message):
    text = message.text
    for row in GetListPersonCharity():
        if message.from_user.username == row:
            for row in getAllMat():
                if row in text:
                    bot.reply_to(message, "Надсилайте сюди свою гривню ☺: https://send.monobank.ua/jar/3AP9zHTxHZ")
                    break
    if text == '@mihail_panchuk':
        msg = bot.reply_to(message,'@mihail_panchuk, привіт, це Сашко, я хочу за тобою бігати')
    elif text == '@so_nyaaa':
        # msg = bot.reply_to(message, '@so_nyaaa, @mihail_panchuk хоче твої сісечкі')
        bot.send_audio(chat_id=message.chat.id, audio=open('Пісня про Соню Купер.mp3', 'rb'))
        bot.send_audio(chat_id=message.chat.id, audio=open('Пісня про Соню Купер.mp3', 'rb'))
    elif text == '@alexagranv':
        # msg = bot.reply_to(message,'хіба ви не подружились з сонічкою?')
        # bot.send_audio(chat_id=message.chat.id, audio=open('audio_2022-07-16_15-53-51.mp3', 'rb'))
        bot.send_audio(chat_id=message.chat.id, audio=open('право Барановичу Максиму Володимировичу.MP3', 'rb'))
    elif text == '@yu_liaa88':
        bot.send_audio(chat_id=message.chat.id, audio=open('audio_2022-07-16_15-57-49.mp3', 'rb'))
        bot.reply_to(message,'@yu_liaa88, йобана корівка бля, як же хочеться тебе ' + '\n' +
                               'за рога потягнути, коли я буду драяти' + '\n' + 'твою солодку піхву, поки ти будеш муукати' + '\n' +
                               'муукати, тупорила корова з піздєц якими' + '\n' + 'великими цицьками)) 😜😜😜')
        bot.send_photo(chat_id=message.chat.id, photo=open('Yulia.jpg', 'rb'))
    elif text == '@ScamCreditBot якого хуя сука слив голосовуху?':
        msg = bot.reply_to(message,'Бо @so_nyaaa не змінилася ніхуя, і я рішив їй поднасрать')
    elif str(text).lower() == 'да':
        msg = bot.reply_to(message, 'Пізда')
    elif str(text).lower() == 'іди нахуй':
        msg = bot.reply_to(message,'Своїм помахуй')
    elif str(text) == 'Тоді бот призначить вам зустріч, так?':
        msg = bot.reply_to(message,'@Barik_superman @yu_liaa88 ,Завтра о 18:00 Злата Плаза, туалет, '
                                               'де Христос натягував 13-літну малишку')
    elif str(text).lower() == 'що таке колоденка і мототрек?':
        bot.send_photo(chat_id=message.chat.id, photo=open('Колоденка.jpg', 'rb'))
    elif str(text).lower() == 'хто буде єбатися з сонічкою?':
        listboba = ['@kreager','@Barik_superman','@mihailik_panchuk']
        bot.reply_to(message,random.choice(listboba))
    elif str(text).lower() == 'хто буде питати в любімої юлічкі про нмт?':
        listboba = ['@kreager','@Barik_superman','@mihailik_panchuk']
        bot.reply_to(message,random.choice(listboba))
    elif text == '@kreager':
        # bot.send_message(message.chat.id, "От'єбіться, він знаходиться на відпочинку в іншому культурному місті. А поки ви можете глянуту, як проходить цей відпочинок на наступному відео: ")
        # bot.send_video(chat_id=message.chat.id, video=open('bearsitsnexttoguy.mp4', 'rb'), supports_streaming=True)
        msg = bot.send_photo(chat_id=message.chat.id, photo=open('Kreager Hi.jpg', 'rb'))
    elif text == 'Ненавиджу нігерів':
        bot.send_message(message.chat.id, 'Чо так?')
    elif text == '@mihailik_panchuk':
        bot.send_message(message.chat.id, 'Поки ти тільки здаєш теорію, я вже катаю твою малишку, з якою в тебе хімія.')
    elif str(text).lower() == 'бот, завалюй інтро курятника':
        bot.send_video(chat_id=message.chat.id, video=open('ІнтроКурятника.mp4', 'rb'), supports_streaming=True)


def checkValidationString(message):
    fullstring = message
    ifValid = True
    warningmessage = "Непередбачувана помилка"
    if message == " ":
        ifValid = False
    else:
        try:
            fullstring = simplifyExpession(message)
            if float(fullstring) < 0:
                warningmessage = f"Вираз вийшов менше нуля: {str(fullstring)}, спробуйте знову, але з додатнім результатом." 
                ifValid = False
        except:
            warningmessage = f"Вираз ({str(fullstring)}) повинен містити лише цифри, арифметичні операції та дужки, спробуйте знову."
            ifValid = False
    return ifValid, fullstring, warningmessage


def simplifyExpession(fullstring):
    equation = str(fullstring)
    equation = equation.strip(" ").replace(",", ".").replace(" ", "")
    i = 0
    while "(" in equation and ")" in equation:
        subEquation = ExtractSubEquation(equation)[0]
        subList = ExtractSubEquation(equation)[1]
        if len(subList) > 2:
            result = prioritiescalculation(subEquation, subList)
            equation = equation.replace("(" + subEquation + ")", result)
            print(subEquation + " = " + result + "\nNow equation is " + equation + "\n----------------------------------")
        elif len(subList) <= 2:
            equation = equation.replace("(" + subEquation + ")", subEquation)
            print(
                subEquation + " = " + subEquation + "\nNow equation is " + equation + "\n----------------------------------")
        i += 1
    while "^" in equation or "*" in equation or "/" in equation or "+" in equation or "-" in equation:
        subeqarr = validateequation(equation)
        if len(subeqarr) >= 3:
            tsq = equation
            equation = prioritiescalculation(equation, subeqarr)
            print(
                tsq + " = " + equation + "\nNow equation is " + equation + "\n----------------------------------")
        elif len(subeqarr) == 2:
            break
        elif len(subeqarr) == 1:
            tsq = equation
            if equation.count("+") > 0:
                equation = equation.replace("+", "")
            equation = equation.replace("-0", "0")
            print(
                tsq + " = " + equation + "\nNow equation is " + equation + "\n----------------------------------")
        if len(subeqarr) <= 1:
            if float(equation) < 0:
                break
    return equation


def bracketindex(eq):
    leftbracket = -1
    rightbracket = -1
    i = 0
    while i < len(eq):
        if eq[i] == "(":
            leftbracket = i
        if eq[i] == ")":
            rightbracket = i
            break
        i += 1
    return leftbracket, rightbracket


def ExtractSubEquation(equation):
    bracketindexes = bracketindex(equation)
    leftbracket = bracketindexes[0]
    rightbracket = bracketindexes[1]
    print("Left bracket: " + str(leftbracket) + " Right bracket: " + str(rightbracket))
    subequation = equation[leftbracket:rightbracket].strip(")").strip("(")
    tsq = subequation
    subList = validateequation(tsq)
    return subequation,subList


def validateequation(eq):
    eq = str(eq).strip(" ").replace(" ", "")
    resulteq = eq[0]
    i = 1
    while i < len(eq):
        if eq[i] == "-" and eq[i-1] == "^":
            resulteq += eq[i]
        elif eq[i].isdigit() or eq[i] == "." and eq[i - 1].isdigit() or eq[i-1] == ".":
            resulteq += eq[i]
        elif eq[i].isdigit() and not eq[i - 1].isdigit():
            resulteq += " " + eq[i]
        elif not eq[i].isdigit():
            resulteq += " " + eq[i] + " "
        i += 1
    resulteq = resulteq.replace("  ", " ")
    resulteq = resulteq.strip(" ")
    listresult = resulteq.split(" ")
    # print("List result: ")
    # print(listresult)
    if len(listresult) == 2 and listresult[0] != "/" and listresult != "*":
        listresult[0] = listresult[0] + listresult[1]
        listresult.pop(1)
    i = 1
    while i < len(listresult):
        if listresult[i] == "^" and listresult[i + 1] == "-":
            listresult[i + 2] = "-" + listresult[i + 2]
            listresult.pop(i + 1)
            for item in listresult:
                print(item)
        elif listresult[i] == "^" and listresult[i + 1] == "+":
            listresult.pop(i + 1)
            for item in listresult:
                print(item)
        if listresult[i] == "*" and listresult[i + 1] == "-":
            listresult[i + 2] = "-" + listresult[i + 2]
            listresult.pop(i + 1)
            for item in listresult:
                print(item)
        if listresult[i] == "/" and listresult[i + 1] == "-":
            listresult[i + 2] = "-" + listresult[i + 2]
            listresult.pop(i + 1)
            for item in listresult:
                print(item)
        i += 1
    i = 1
    while i < len(listresult):
        if listresult[i] == "+" and listresult[i + 1] == "-":
            listresult.pop(i)
            for item in listresult:
                print(item)
        elif listresult[i] == "-" and listresult[i + 1] == "+":
            listresult.pop(i + 1)
            for item in listresult:
                print(item)
        if listresult[i] == "*" and listresult[i + 1] == "+":
            listresult.pop(i + 1)
            for item in listresult:
                print(item)
        if listresult[i] == "/" and listresult[i + 1] == "+":
            listresult.pop(i + 1)
            for item in listresult:
                print(item)
        i += 1
    print("Local arythmetic will be such: " + resulteq)
    return listresult


def calculationtwo(leftnumber, rightnumber, operation):
    result = 0
    print("Left number: " + leftnumber)
    print("Right number: " + rightnumber)
    lnum = float(leftnumber)
    rnum = float(rightnumber)
    if operation == "+":
        result = lnum + rnum
    elif operation == "-":
        result = lnum - rnum
    elif operation == "*":
        result = lnum * rnum
    elif operation == "/":
        result = lnum / rnum
    elif operation == "^":
        result = pow(lnum,rnum)
    else:
        print("Invalid operation. Sign " + operation)
    if "e" in str(result):
        result = round(result, 4)
    return result


def prioritiescalculation(mathStr,mathparts):
    print("Length mathparts: " + str(len(mathparts)))
    if "^" in mathStr:
        i = 1
        while i < len(mathparts):
            subeq = ""
            if mathparts[i] == "^":
                res = calculationtwo(mathparts[i - 1], mathparts[i + 1], mathparts[i])
                subeq += mathparts[i - 1]
                subeq += mathparts[i]
                subeq += mathparts[i + 1]
                subeq = subeq.replace("^+", "^")
                mathparts.pop(i - 1)
                mathparts.pop(i - 1)
                mathparts.pop(i - 1)
                print("Math parts: ")
                print(mathparts)
                mathparts.insert(i - 1, str(res))
                print("Sub equation: " + subeq)
                print("Current equation before replace: " + mathStr)
                mathStr = mathStr.replace(subeq, str(res))
                print("Current equation: " + mathStr)
            i += 1
    if "*" in mathStr or "/" in mathStr:
        i = 1
        while i < len(mathparts):
            subeq = ""
            if mathparts[i] == "*" or mathparts[i] == "/":
                res = calculationtwo(mathparts[i - 1], mathparts[i + 1], mathparts[i])
                subeq += mathparts[i - 1]
                subeq += mathparts[i]
                subeq += mathparts[i + 1]
                subeq = subeq.replace("*+", "*")
                subeq = subeq.replace("/+", "/")
                mathparts.pop(i - 1)
                mathparts.pop(i - 1)
                mathparts.pop(i - 1)
                mathparts.insert(i - 1, str(res))
                print("Math parts: ")
                print(mathparts)
                print("Sub equation: " + subeq)
                print("Current equation before replace: " + mathStr)
                mathStr = mathStr.replace(subeq, str(res))
                print("Current equation: " + mathStr)
            else:
                i += 1
    if "+" in mathStr or "-" in mathStr:
        i = 1
        while i < len(mathparts):
            subeq = ""
            if mathparts[i] == "+" or mathparts[i] == "-":
                res = calculationtwo(mathparts[i - 1], mathparts[i + 1], mathparts[i])
                subeq += mathparts[i - 1]
                subeq += mathparts[i]
                subeq += mathparts[i + 1]
                subeq = subeq.replace("+-", "-")
                subeq = subeq.replace("-+", "-")
                mathparts.pop(i - 1)
                mathparts.pop(i - 1)
                mathparts.pop(i - 1)
                mathparts.insert(i - 1, str(res))
                print("Math parts: ")
                print(mathparts)
                print("Sub equation: " + subeq)
                print("Current equation before replace: " + mathStr)
                mathStr = mathStr.replace(subeq, str(res))
                print("Current equation: " + mathStr)
            else:
                i += 1
    return mathStr


def add_sum(message, userName):
    if message.from_user.username == userName:
        if message.text == "🛑 Відмінити операцію":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            list = checkValidationString(message.text)
            if not list[0]:
                msg = bot.reply_to(message, list[2])
                bot.register_next_step_handler(msg, add_sum, userName)
            else:
                if not CheckLoneLinnes(message.chat.id):
                    continueController = True
                    try:
                        result = AddDebtForAll(message.from_user.id, message.chat.id, float(list[1]))
                        if "Перевищено ліміт боргу: " in result:
                            continueController = False
                            msg = bot.reply_to(message, result + "; Спробуйте ще раз")
                            bot.register_next_step_handler(msg, add_sum, userName)
                        else:
                            bot.reply_to(message, result)
                    except:
                        continueController = False
                        msg = bot.reply_to(message,
                                           "Вираз повинен містити лише цифри, арифметичні операції та дужки, спробуйте ще раз.")
                        bot.register_next_step_handler(msg, add_sum, userName)
                    if continueController:
                        msg = bot.reply_to(message, f'Кошти добавлено' + '\n' + '\n' + ShowData(message))
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        item1 = types.KeyboardButton("✅ Так")
                        item2 = types.KeyboardButton("⛔ Ні")
                        item3 = types.KeyboardButton("🛑 Відмінити операцію")
                        markup.row(item1, item2)
                        markup.row(item3)
                        msg = bot.reply_to(message, 'Частина людей з групи скидалась?',
                                           reply_markup=markup)
                        bot.register_next_step_handler(msg, response_sum_exact, userName)
                elif CheckLoneLinnes(message.chat.id) == "Ти скидаєшся сам з собою, знайди собі друзів":
                    bot.reply_to(message, 'Ти скидаєшся сам з собою, знайди собі друзів',
                                    reply_markup=types.ReplyKeyboardRemove())
                # elif CheckLoneLinnes(message.chat.id) == "Для початку увійдіть в гільдію: команда /entertheparty":
                #     bot.reply_to(message, f'Для початку увійдіть в гільдію: команда /entertheparty',
                #                  reply_markup=types.ReplyKeyboardRemove())
    else:
        msg = bot.reply_to(message, 'Індульгенцію на ввід кількості коштів має лише @' + userName + ". Просимо його зробите це.")
        bot.register_next_step_handler(msg, add_sum, userName)


def response_sum_exact(message, userName):
    if message.from_user.username == userName:
        if message.text == "✅ Так":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item3 = types.KeyboardButton("🛑 Відмінити операцію")
            markup.row(item3)
            msg = bot.reply_to(message, 'Впишіть людей, які скидались через знак "/"',
                               reply_markup=markup)
            msg_content = str(msg.text).replace(" ", "/")
            # print( )
            # listperson = str(msg_content).split("/")
            bot.register_next_step_handler(msg, handle_list_person, userName)
        elif message.text == "⛔ Ні":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("✅ Так")
            item2 = types.KeyboardButton("⛔ Ні")
            item3 = types.KeyboardButton("🛑 Відмінити операцію")
            markup.row(item1, item2)
            markup.row(item3)
            msg = bot.reply_to(message, 'Ви оплачували людям окремі (їх) товари?', reply_markup=markup)
            bot.register_next_step_handler(msg, response_sum_one, userName)
        elif message.text == "🛑 Відмінити операцію":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.register_next_step_handler(message, response_sum_exact, userName)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на відповідь має лише @' + userName)
        bot.register_next_step_handler(msg, response_sum_exact, userName)


def handle_list_person(message, userName):
    if message.from_user.username == userName:
        if message.text == "🛑 Відмінити операцію":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            # msg = bot.reply_to(message, 'Впишіть відповідну кількість коштів для кожної людини через пробіл або знак "|"',
            #                    reply_markup=types.ReplyKeyboardRemove())
            # msg_content = str(message.text).replace(" ", "/")
            msg_content = str(message.text).replace(" ", "")
            msg_content = msg_content.replace("@", "")
            listperson = str(msg_content).split("/")
            list = checkIfPersonsExist(listperson, message)
            if list[0]:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item3 = types.KeyboardButton("🛑 Відмінити операцію")
                markup.row(item3)
                msg = bot.reply_to(message, 'Впишіть кількість коштів, на яку ці люди скинулись',
                                   reply_markup=markup)
                bot.register_next_step_handler(msg, handle_list_sum, listperson, userName)
            else:
                msg = bot.reply_to(message,
                                   list[1] + ' не входять у патті або не існують, спробуйте ще раз')
                bot.register_next_step_handler(msg, handle_list_person, userName)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на відповідь має лише @' + userName + ". Впишіть людей, які скидались через знак '/'")
        bot.register_next_step_handler(msg, handle_list_person, userName)


def checkIfPersonsExist(listperson, message):
    notExist = ''
    countExistance = 0
    for row in listperson:
        if CheckUserByUserName(row, message.chat.id):
            countExistance = countExistance + 1
        else:
            notExist = notExist + " @" + row
    print(notExist)
    print(countExistance)
    if countExistance == len(listperson):
        return True, notExist
    else:
        return False, notExist


def handle_list_sum(message, listperson, userName):
    if message.from_user.username == userName:
        if message.text == "🛑 Відмінити операцію":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            try:
                list = checkValidationString(message.text)
                if not list[0]:
                    msg = bot.reply_to(message,
                                       list[2])
                    bot.register_next_step_handler(msg, handle_list_sum, userName)
                else:
                    continueController = True
                    i = 0
                    if len(listperson) == 1 and message.from_user.id == getUserIdByUserName(listperson[0]):
                        msg = bot.reply_to(message,
                                           'Нахріна ти сам собі борг додаєш? У даному випадку тобі винні гроші. Спробуй ще раз')
                        bot.register_next_step_handler(msg, handle_list_person_for_one, userName)
                    else:
                        try:
                            result = AddDebtForGroupNotAll(message.from_user.id, message.chat.id, list[1], listperson)
                            if "Перевищено ліміт боргу: " in result:
                                continueController = False
                                msg = bot.reply_to(message, result + "; Спробуйте ще раз")
                                bot.register_next_step_handler(msg, handle_list_sum, listperson, userName)
                            else:
                                bot.reply_to(message, result)
                        except:
                            continueController = False
                            msg = bot.reply_to(message,
                                               "Вираз повинен містити лише цифри, арифметичні операції та дужки, спробуйте ще раз.")
                            bot.register_next_step_handler(msg, handle_list_sum, listperson, userName)
                        if continueController:
                            msg = bot.reply_to(message, f'Кошти добавлено' + '\n' + '\n' + ShowData(message))
                            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                            item1 = types.KeyboardButton("✅ Так")
                            item2 = types.KeyboardButton("⛔ Ні")
                            item3 = types.KeyboardButton("🛑 Відмінити операцію")
                            markup.row(item1, item2)
                            markup.row(item3)
                            msg = bot.reply_to(message, 'Ви оплачували людям окремі (їх) товари?', reply_markup=markup)
                            bot.register_next_step_handler(msg, response_sum_one, userName)
            except:
                msg = bot.reply_to(message,
                                   "Вираз повинен містити лише цифри, арифметичні операції та дужки, спробуйте ще раз.")
                bot.register_next_step_handler(msg, handle_list_sum, listperson, userName)
    else:
        msg = bot.reply_to(message,
                           'Індульгенцію на відповідь має лише @' + userName + ". Впишіть кількість коштів, на яку скидались люди")
        bot.register_next_step_handler(msg, handle_list_sum, userName)


def response_sum_one(message, userName):
    if message.from_user.username == userName:
        if message.text == "✅ Так":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item3 = types.KeyboardButton("🛑 Відмінити операцію")
            markup.row(item3)
            msg = bot.reply_to(message, 'Впишіть людей, яким ви оплачували товар через знак "/"',
                               reply_markup=markup)
            msg_content = str(msg.text).replace(" ", "/")
            # print(msg_content)
            # listperson = str(msg_content).split("/")
            bot.register_next_step_handler(msg, handle_list_person_for_one, userName)
        elif message.text == "⛔ Ні":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "🛑 Відмінити операцію":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.register_next_step_handler(message, response_sum_one, userName)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на відповідь має лише @' + userName)
        bot.register_next_step_handler(msg, response_sum_one, userName)


def handle_list_person_for_one(message, userName):
    if message.from_user.username == userName:
        if message.text == "🛑 Відмінити операцію":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            # msg = bot.reply_to(message, 'Впишіть відповідну кількість коштів для кожної людини з допомогою знаку "|"',
            #                    reply_markup=types.ReplyKeyboardRemove())
            msg_content = str(message.text).replace(" ", "/")
            msg_content = msg_content.replace("@", "")
            listperson = str(msg_content).split("/")
            list = checkIfPersonsExist(listperson, message)
            if list[0]:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item3 = types.KeyboardButton("🛑 Відмінити операцію")
                markup.row(item3)
                msg = bot.reply_to(message, 'Впишіть відповідну кількість коштів для кожної людини з допомогою знаку "|"',
                                   reply_markup=markup)
                bot.register_next_step_handler(msg, handle_list_sum_for_one, listperson, userName)
            else:
                msg = bot.reply_to(message,
                                   list[1] + ' не входять у патті або не існують, спробуйте ще раз')
                bot.register_next_step_handler(msg, handle_list_person_for_one, userName)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на відповідь має лише @' + userName + ". Впишіть людей, які скидались через знак '/'")
        bot.register_next_step_handler(msg, handle_list_person_for_one, userName)


def handle_list_sum_for_one(message, listperson, userName):
    continueController = False
    if message.from_user.username == userName:
        if message.text == "🛑 Відмінити операцію":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            listsum = str(message.text).strip(" ")
            listsum = str(listsum).split("|")
            print(listsum)
            i = 0
            for row in listsum:
                list = checkValidationString(row)
                if not list[0]:
                    continueController = False
                    msg = bot.reply_to(message,
                                       list[2])
                    bot.register_next_step_handler(msg, handle_list_sum_for_one, listperson, userName)
                    break
                else:
                    listsum.pop(i)
                    listsum.insert(i, list[1])
                    continueController = True
                    i += 1
                    continue
            if continueController:
                if len(listperson) == len(listsum):
                    i = 0
                    while i < len(listperson):
                        if len(listperson) == 1 and message.from_user.id == getUserIdByUserName(listperson[i]):
                            continueController = False
                            msg = bot.reply_to(message,
                                               'Нахріна ти сам собі борг додаєш? У даному випадку тобі винні гроші. Спробуй ще раз')
                            bot.register_next_step_handler(msg, handle_list_person_for_one, userName)
                            break
                        else:
                            try:
                                result = AddDebtForOne(message.from_user.id, message.chat.id, listsum[i],
                                              getUserIdByUserName(listperson[i]))
                                if "Перевищено ліміт боргу: " in result:
                                    continueController = False
                                    msg = bot.reply_to(message, result + "; Спробуйте ще раз")
                                    bot.register_next_step_handler(msg, handle_list_sum_for_one, listperson, userName)
                                else:
                                    bot.reply_to(message, result)
                            except:
                                continueController = False
                                msg = bot.reply_to(message,
                                                   "Вираз повинен містити лише цифри, арифметичні операції та дужки, спробуйте ще раз.")
                                bot.register_next_step_handler(msg, handle_list_sum_for_one, listperson, userName)
                                break
                        i = i + 1
                    if continueController:
                        msg = bot.reply_to(message, f'Кошти добавлено' + '\n' + '\n' + ShowData(message))
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        item1 = types.KeyboardButton("✅ Так")
                        item2 = types.KeyboardButton("⛔ Ні")
                        item3 = types.KeyboardButton("🛑 Відмінити операцію")
                        markup.row(item1, item2)
                        markup.row(item3)
                        msg = bot.reply_to(message, 'Можливо ви оплачували ще комусь окремі (його/її/їх) товари?', reply_markup=markup)
                        bot.register_next_step_handler(msg, response_sum_one, userName)
                else:
                    msg = bot.reply_to(message,
                                       'Кількість людей та відповідна кількість коштів повинна бути однаковою, спробуйте ще раз. Впишіть людей, які скидались через знак "/".')
                    bot.register_next_step_handler(msg, handle_list_sum_for_one, listperson, userName)
    else:
        msg = bot.reply_to(message,
                           'Індульгенцію на відповідь має лише @' + userName + ". Впишіть кількість коштів, на яку скидались люди")
        bot.register_next_step_handler(msg, handle_list_sum_for_one, listperson, userName)


# @server.route('/' + TOKEN, methods=['POST'])
# def getMessage():
#     json_string = request.get_data().decode('utf-8')
#     update = telebot.types.Update.de_json(json_string)
#     bot.process_new_updates([update])
#     return "!", 200
#
#
# @server.route("/")
# def webhook():
#     bot.remove_webhook()
#     bot.set_webhook(url='https://debtbot.fly.dev/' + TOKEN)
#     return "!", 200


def main():
    print('Бот Стартує!!!')
    # DropTable()
    CreateTable()
    # ShowData()
    # ShowChats()
    try:
        bot.infinity_polling()
    except:
        print("Not today")


if __name__ == "__main__":
    main()
    # scheduler.add_job(send_celebration, 'interval', minutes=1)
    # scheduler.start()
    # server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))