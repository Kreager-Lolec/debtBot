# -*- coding: utf-8 -*-
import random

import Constant_File as Keys
from telebot import *
from ConnectDB import *
import re
from flask import Flask, request
import os

print('Бот Стартує!')

CreateTable()
# ShowData()
# ShowChats()
# DeleteData()

TOKEN = Keys.API_KEY
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привіт пані та панове, я бот, який буде керувати вашими боргами. Для початку перевірте чи є "
                          "у "
                          "вас взагалі кошти (І чи не віддали ви свій под бившим і не хочете повертати гроші), щоб я "
                          "міг хоч щось порахувати")


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


@bot.message_handler(commands=['showdata'])
def showdata(message):
    bot.reply_to(message, ShowData(message))


@bot.message_handler(commands=['setdebt'])
def setdebt(message):
    userName = message.from_user.username
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("✅ Так")
    item2 = types.KeyboardButton("⛔ Ні")
    item3 = types.KeyboardButton("🛑 Відмінити операцію?")
    markup.row(item1, item2)
    markup.row(item3)
    msg = bot.reply_to(message, 'Усі люди скидались?', reply_markup=markup)
    bot.register_next_step_handler(msg, responsesum, userName)


@bot.message_handler(commands=['removedebt'])
def removedebt(message):
    if CheckUser(message.from_user.id, message.chat.id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item3 = types.KeyboardButton("🛑 Відмінити операцію?")
        markup.row(item3)
        userName = message.from_user.username
        msg = bot.reply_to(message, 'Кому ви хочете видалити борг? (Введіть нікнейм з допомогою @) ', reply_markup=markup)
        bot.register_next_step_handler(msg, responseRemoveDebt, userName)
    else:
        bot.reply_to(message, f'Для початку увійдіть в гільдію: команда /entertheparty')


def responseRemoveDebt(message, userName):
    if message.from_user.username == userName:
        if message.text == "🛑 Відмінити операцію?":
            bot.reply_to(message, 'Як знаєте.', reply_markup=types.ReplyKeyboardRemove())
        else:
            PersonUserName = message.text
            PersonUserName = str(PersonUserName).replace("@", '')
            PersonUserName = str(PersonUserName).replace(" ", '')
            if not userName == PersonUserName:
                if checkIfPersonHaveDebtFromPayer(PersonUserName, message.chat.id, userName):
                    PersonId = getUserIdByUserName(PersonUserName)
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = types.KeyboardButton("💰 Повну суму")
                    item2 = types.KeyboardButton("💵 Конкретну")
                    item3 = types.KeyboardButton("🛑 Відмінити операцію?")
                    markup.row(item1, item2)
                    markup.row(item3)
                    msg = bot.reply_to(message, 'Видалити весь борг чи конкретну суму?', reply_markup=markup)
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
        if message.text == "💰 Повну суму":
            if CheckIfZeroDebt(PersonId, message.chat.id, userName):
                msg = bot.reply_to(message, 'Ви і так витрясли все з нього!', reply_markup=types.ReplyKeyboardRemove())
            else:
                RemoveDebt(PersonId, message.chat.id, userName)
                msg = bot.reply_to(message, 'Борг успішно видалено', reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "💵 Конкретну":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item3 = types.KeyboardButton("🛑 Відмінити операцію?")
            markup.row(item3)
            msg = bot.reply_to(message, 'Введіть суму, яку хочете списати з боргу.', reply_markup=markup)
            bot.register_next_step_handler(msg, removeExactDebt, userName, PersonId)
        elif message.text == "🛑 Відмінити операцію?":
            bot.reply_to(message, 'Як знаєте.', reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.register_next_step_handler(message, choiceDelete, userName, PersonId)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на видалення має @' + userName)
        bot.register_next_step_handler(msg, choiceDelete, userName, PersonId)


def removeExactDebt(message, userName, PersonId):
    if message.from_user.username == userName:
        if message.text == "🛑 Відмінити операцію?":
            bot.reply_to(message, 'Як знаєте.', reply_markup=types.ReplyKeyboardRemove())
        else:
            if checkValidationString(message.text)[0]:
                debtValue = float(checkValidationString(message.text)[1])
                if CheckIfZeroDebt(PersonId, message.chat.id, userName):
                    msg = bot.reply_to(message, 'Ви і так витрясли все з нього!',
                                       reply_markup=types.ReplyKeyboardRemove())
                elif CheckMinusDebt(PersonId, message.chat.id, debtValue, userName):
                    msg = bot.reply_to(message,
                                       'Воу-воу, ви хочете видалити більше, чим вам винні. Введіть суму ще раз, яку хочете списати з боргу.')
                    bot.register_next_step_handler(msg, removeExactDebt, userName, PersonId)
                else:
                    RemoveExactDebt(PersonId, message.chat.id, debtValue, userName)
                    msg = bot.reply_to(message, 'Борг успішно відняно.', reply_markup=types.ReplyKeyboardRemove())
            else:
                msg = bot.reply_to(message,
                                   'Значення повинно містити лише цифри (без пробілів) (У разі додавання (числа до мільйона) ще знак "+"), введіть значення боргу ще раз')
                bot.register_next_step_handler(msg, removeExactDebt, userName, PersonId)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на видалення має @' + userName + " Просимо його ввести суму, яку потрібно списати з боргу.")
        bot.register_next_step_handler(msg, removeExactDebt, userName, PersonId)


@bot.message_handler(commands=['addcards'])
def addcards(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item3 = types.KeyboardButton("🛑 Відмінити операцію?")
    markup.row(item3)
    userName = message.from_user.username
    msg = bot.reply_to(message, 'Впишіть ваші реквізити', reply_markup=markup)
    bot.register_next_step_handler(msg, addcardtodb, userName)


@bot.message_handler(commands=['deletecards'])
def deletecards(message):
    userName = message.from_user.username
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("✅ Так")
    item2 = types.KeyboardButton("⛔ Ні")
    item3 = types.KeyboardButton("🛑 Відмінити операцію?")
    markup.row(item1, item2)
    markup.row(item3)
    msg = bot.reply_to(message, 'Видалити ваші реквізити?', reply_markup=markup)
    bot.register_next_step_handler(msg, deletecard, userName)


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
            bot.reply_to(message, f'Гарного дня вам!', reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "🛑 Відмінити операцію?":
            bot.reply_to(message, 'Як знаєте.', reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.register_next_step_handler(message, deletecard, userName)
    else:
        msg = bot.reply_to(message, "@" + userName + " має індульгенцію видаляти свою картку.")
        bot.register_next_step_handler(msg, deletecard, userName)


def addcardtodb(message, userName):
    if message.from_user.username == userName:
        if message.text == "🛑 Відмінити операцію?":
            bot.reply_to(message, 'Як знаєте.', reply_markup=types.ReplyKeyboardRemove())
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
                        item3 = types.KeyboardButton("🛑 Відмінити операцію?")
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
            item3 = types.KeyboardButton("🛑 Відмінити операцію?")
            markup.row(item3)
            msg = bot.reply_to(message, 'Впишіть ваші реквізити', reply_markup=markup)
            bot.register_next_step_handler(msg, addcardtodb, userName)
            print(msg.text)
        elif message.text == "⛔ Ні":
            bot.reply_to(message, f'\t\t\tРеквізити додано' + '\n' + ShowData(message),
                         reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "🛑 Відмінити операцію?":
            bot.reply_to(message, 'Як знаєте.', reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.register_next_step_handler(message, responsecard, userName)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на відповідь має лише @' + userName)
        bot.register_next_step_handler(msg, responsecard, userName)


def responsesum(message, userName):
    if message.from_user.username == userName:
        if message.text == "✅ Так":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item3 = types.KeyboardButton("🛑 Відмінити операцію?")
            markup.row(item3)
            msg = bot.reply_to(message, 'Впишіть суму', reply_markup=markup)
            bot.register_next_step_handler(msg, add_sum, userName)
            print(msg.text)
        elif message.text == "⛔ Ні":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("✅ Так")
            item2 = types.KeyboardButton("⛔ Ні")
            item3 = types.KeyboardButton("🛑 Відмінити операцію?")
            markup.row(item1, item2)
            markup.row(item3)
            msg = bot.reply_to(message, 'Скидались не всі, але більше чим одна людина?', reply_markup=markup)
            bot.register_next_step_handler(msg, response_sum_exact, userName)
        elif message.text == "🛑 Відмінити операцію?":
            bot.reply_to(message, 'Як знаєте.', reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.register_next_step_handler(message, responsesum, userName)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на відповідь має лише @' + userName)
        bot.register_next_step_handler(msg, responsesum, userName)


@bot.message_handler(content_types=['text'])
def response(message):
    text = message.text
    if text == '@mihail_panchuk':
        msg = bot.reply_to(message,'@mihail_panchuk, привіт, це Сашко, я хочу за тобою бігати')
    elif text == '@so_nyaaa':
        # msg = bot.reply_to(message, '@so_nyaaa, @mihail_panchuk хоче твої сісечкі')
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
        msg = bot.send_photo(chat_id=message.chat.id, photo=open('Kreager Hi.jpg', 'rb'))
    elif text == 'Ненавиджу нігерів':
        bot.send_message(message.chat.id, 'Чо так?')
    elif text == '@mihailik_panchuk':
        bot.send_message(message.chat.id, 'Поки ти тільки здаєш теорію, я вже катаю твою малишку, з якою в тебе хімія.')
    elif str(text).lower() == 'бот, завалюй інтро курятника':
        bot.send_video(chat_id=message.chat.id, video=open('ІнтроКурятника.mp4', 'rb'), supports_streaming=True)


def simplifyExpession(expession):
        equation = str(expession)
        if equation.find('+'):
            equation = equation.split('+')
            print(equation)
            while len(equation) > 1:
                tempsum = Subeq(equation[0], equation[len(equation) - 1])
                equation.remove(equation[0])
                equation.remove(equation[len(equation) - 1])
                equation.append(tempsum)
                print(equation)
        print(equation)
        return equation[0]


def Subeq(leftnum,rightnum):
    sum = float(leftnum) + float(rightnum)
    print("Sum: " + str(sum))
    return str(sum)


def checkValidationString(message):
        substring = "+"
        fullstring = str(message)
        fullstring = fullstring.strip(" ")
        if " " in fullstring:
            match = None
        else:
            if fullstring.find("+") > 0:
                regex = re.compile("\d{0,6}[+]\d{0,6}")
                match = regex.match(fullstring)
                try:
                    fullstring = simplifyExpession(fullstring)
                except:
                    match = None
            else:
                regex = re.compile('\\d')
                match = regex.match(fullstring)
        if match is None:
            return False, fullstring
        return True, fullstring


def add_sum(message, userName):
    if message.from_user.username == userName:
        if message.text == "🛑 Відмінити операцію?":
            bot.reply_to(message, 'Як знаєте.', reply_markup=types.ReplyKeyboardRemove())
        else:
            list = checkValidationString(message.text)
            if not list[0]:
                msg = bot.reply_to(message,
                                   'Сума повинна містити лише цифри (У разі додавання (числа до мільйона) ще знак "+"), введіть суму ще раз')
                bot.register_next_step_handler(msg, add_sum, userName)
            else:
                if not CheckLoneLinnes(message.from_user.id, message.chat.id):
                    AddDebtForAll(message.from_user.id, message.chat.id, float(list[1]))
                    msg = bot.reply_to(message, f'Суму добавлено' + '\n' + '\n' + ShowData(message))
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = types.KeyboardButton("✅ Так")
                    item2 = types.KeyboardButton("⛔ Ні")
                    item3 = types.KeyboardButton("🛑 Відмінити операцію?")
                    markup.row(item1, item2)
                    markup.row(item3)
                    msg = bot.reply_to(message, 'Скидались не всі, але більше чим одна людина?', reply_markup=markup)
                    bot.register_next_step_handler(msg, response_sum_exact, userName)
                elif CheckLoneLinnes(message.from_user.id,
                                     message.chat.id) == "Ти скидаєшся сам з собою, знайди собі друзів":
                    bot.reply_to(message, 'Ти скидаєшся сам з собою, знайди собі друзів', reply_markup=types.ReplyKeyboardRemove())
                elif CheckLoneLinnes(message.from_user.id,
                                     message.chat.id) == "Для початку увійдіть в гільдію: команда /entertheparty":
                    bot.reply_to(message, f'Для початку увійдіть в гільдію: команда /entertheparty',
                                 reply_markup=types.ReplyKeyboardRemove())
    else:
        msg = bot.reply_to(message, 'Індульгенцію на ввід суми має лише @' + userName + ". Просимо його зробите це.")
        bot.register_next_step_handler(msg, add_sum, userName)


def response_sum_exact(message, userName):
    if message.from_user.username == userName:
        if message.text == "✅ Так":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item3 = types.KeyboardButton("🛑 Відмінити операцію?")
            markup.row(item3)
            msg = bot.reply_to(message, 'Впишіть людей, які скидались через знак "/"',
                               reply_markup=types.ReplyKeyboardRemove())
            msg_content = str(msg.text).replace(" ", "/")
            # print(msg_content)
            # listperson = str(msg_content).split("/")
            bot.register_next_step_handler(msg, handle_list_person, userName)
        elif message.text == "⛔ Ні":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("✅ Так")
            item2 = types.KeyboardButton("⛔ Ні")
            item3 = types.KeyboardButton("🛑 Відмінити операцію?")
            markup.row(item1, item2)
            markup.row(item3)
            msg = bot.reply_to(message, 'Ви оплачували людям окремі товари?', reply_markup=markup)
            bot.register_next_step_handler(msg, response_sum_one, userName)
        elif message.text == "🛑 Відмінити операцію?":
            bot.reply_to(message, 'Як знаєте.', reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.register_next_step_handler(message, response_sum_exact, userName)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на відповідь має лише @' + userName)
        bot.register_next_step_handler(msg, response_sum_exact, userName)


def handle_list_person(message, userName):
    if message.from_user.username == userName:
        if message.text == "🛑 Відмінити операцію?":
            bot.reply_to(message, 'Як знаєте.', reply_markup=types.ReplyKeyboardRemove())
        else:
            # msg = bot.reply_to(message, 'Впишіть відповідні суми для кожної людини через пробіл або знак "/"',
            #                    reply_markup=types.ReplyKeyboardRemove())
            msg_content = str(message.text).replace(" ", "/")
            msg_content = msg_content.replace("@", "")
            listperson = str(msg_content).split("/")
            list = checkIfPersonsExist(listperson, message)
            if list[0]:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item3 = types.KeyboardButton("🛑 Відмінити операцію?")
                markup.row(item3)
                msg = bot.reply_to(message, 'Впишіть суму, на яку ці люди скинулись',
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
        if message.text == "🛑 Відмінити операцію?":
            bot.reply_to(message, 'Як знаєте.', reply_markup=types.ReplyKeyboardRemove())
        else:
            list = checkValidationString(message.text)
            if not list[0]:
                msg = bot.reply_to(message,
                                   'Сума повинна містити лише цифри (У разі додавання (числа до мільйона) ще знак "+"), введіть суму ще раз')
                bot.register_next_step_handler(msg, handle_list_sum, userName)
            else:
                i = 0
                if len(listperson) == 1 and message.from_user.id == getUserIdByUserName(listperson[0]):
                    msg = bot.reply_to(message,
                                           'Нахріна ти сам собі борг додаєш? У даному випадку тобі винні гроші. Спробуй ще раз')
                    bot.register_next_step_handler(msg, handle_list_person_for_one, userName)
                else:
                    AddDebtForGroupNotAll(message.from_user.id, message.chat.id, list[1], listperson)
                    msg = bot.reply_to(message, f'Суму добавлено' + '\n' + '\n' + ShowData(message))
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = types.KeyboardButton("✅ Так")
                    item2 = types.KeyboardButton("⛔ Ні")
                    item3 = types.KeyboardButton("🛑 Відмінити операцію?")
                    markup.row(item1, item2)
                    markup.row(item3)
                    msg = bot.reply_to(message, 'Людина брала окремий товар?', reply_markup=markup)
                    bot.register_next_step_handler(msg, response_sum_one, userName)
    else:
        msg = bot.reply_to(message,
                           'Індульгенцію на відповідь має лише @' + userName + ". Впишіть суму, на яку скидались люди")
        bot.register_next_step_handler(msg, handle_list_sum, userName)


def response_sum_one(message, userName):
    if message.from_user.username == userName:
        if message.text == "✅ Так":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item3 = types.KeyboardButton("🛑 Відмінити операцію?")
            markup.row(item3)
            msg = bot.reply_to(message, 'Впишіть людей, які скидались через знак "/"',
                               reply_markup=types.ReplyKeyboardRemove())
            msg_content = str(msg.text).replace(" ", "/")
            # print(msg_content)
            # listperson = str(msg_content).split("/")
            bot.register_next_step_handler(msg, handle_list_person_for_one, userName)
        elif message.text == "⛔ Ні":
            msg = bot.reply_to(message, 'Хорошо дня вам!', reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "🛑 Відмінити операцію?":
            bot.reply_to(message, 'Як знаєте.', reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.register_next_step_handler(message, response_sum_one, userName)
    else:
        msg = bot.reply_to(message, 'Індульгенцію на відповідь має лише @' + userName)
        bot.register_next_step_handler(msg, response_sum_one, userName)


def handle_list_person_for_one(message, userName):
    if message.from_user.username == userName:
        if message.text == "🛑 Відмінити операцію?":
            bot.reply_to(message, 'Як знаєте.', reply_markup=types.ReplyKeyboardRemove())
        else:
            # msg = bot.reply_to(message, 'Впишіть відповідні суми для кожної людини з допомогою знаку "/"',
            #                    reply_markup=types.ReplyKeyboardRemove())
            msg_content = str(message.text).replace(" ", "/")
            msg_content = msg_content.replace("@", "")
            listperson = str(msg_content).split("/")
            list = checkIfPersonsExist(listperson, message)
            if list[0]:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item3 = types.KeyboardButton("🛑 Відмінити операцію?")
                markup.row(item3)
                msg = bot.reply_to(message, 'Впишіть відповідні суми для кожної людини з допомогою знаку "/"',
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
        if message.text == "🛑 Відмінити операцію?":
            bot.reply_to(message, 'Як знаєте.', reply_markup=types.ReplyKeyboardRemove())
        else:
            listsum = str(message.text).strip(" ")
            listsum = str(listsum).split("/")
            print(listsum)
            for row in listsum:
                list = checkValidationString(row)
                if not list[0]:
                    continueController = False
                    msg = bot.reply_to(message,
                                       'Сума повинна містити лише цифри (У разі додавання (числа до мільйона) ще знак "+"), введіть суму ще раз')
                    bot.register_next_step_handler(msg, handle_list_person_for_one, userName)
                    break
                else:
                    continueController = True
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
                            AddDebtForOne(message.from_user.id, message.chat.id, listsum[i],
                                          getUserIdByUserName(listperson[i]))
                        i = i + 1
                    if continueController:
                        msg = bot.reply_to(message, f'Суму добавлено' + '\n' + '\n' + ShowData(message))
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        item1 = types.KeyboardButton("✅ Так")
                        item2 = types.KeyboardButton("⛔ Ні")
                        item3 = types.KeyboardButton("🛑 Відмінити операцію?")
                        markup.row(item1, item2)
                        markup.row(item3)
                        msg = bot.reply_to(message, 'Можливо потрібно вписати ще когось?', reply_markup=markup)
                        bot.register_next_step_handler(msg, response_sum_one, userName)
                else:
                    msg = bot.reply_to(message,
                                       'Кількість людей та відповідних сум повинна бути однаковою, спробуйте ще раз. Впишіть людей, які скидались через знак "/".')
                    bot.register_next_step_handler(msg, handle_list_sum_for_one, listperson, userName)
    else:
        msg = bot.reply_to(message,
                           'Індульгенцію на відповідь має лише @' + userName + ". Впишіть суму, на яку скидались люди")
        bot.register_next_step_handler(msg, handle_list_sum_for_one, listperson, userName)


# def stop(message, userName):
#     if message.from_user.username == userName:
#         msg = bot.reply_to(message, '' ,reply_markup = types.ReplyKeyboardRemove())
#     else:
#         msg = bot.reply_to(message,
#                            'Індульгенцію на скасування операції має лише @' + userName)
#         bot.register_next_step_handler(msg, stop, userName)

# def add_division(message, userName):
#     bot.reply_to(message, f'Іди нахрін')


# def response(message: Message):
#     text = message.text
#     reply = Res.response(text, message)
#     bot.reply_to(message, reply)
#     bot.register_next_step_handler(message, response)


# def initializeMoney(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     item1 = types.KeyboardButton("Увійти в паті")
#     item2 = types.KeyboardButton("Показати список Masters")
#     markup.add(item1)
#     markup.add(item2)
#     bot.reply_to(message, 'Виберіть,що вам потрібно!', reply_markup=markup)


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://protected-lowlands-25243.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

# bot.infinity_polling()
