from ConnectDB import *


def response(input_text, message):
    user_message = str(input_text).lower()
    if user_message in ('боржники', 'credit', 'жопа',):
        return "Барик Лох, сторчить нам 1000 гривень кожному"
    # elif user_message in ('увійти в паті',):
        # user_id = message.from_user.id
        # chat_id = message.chat.id
        # user_first_name = str(message.from_user.first_name)
        # user_last_name = str(message.from_user.last_name)
        # if CheckUser(user_id, chat_id, user_first_name + ' ' + user_last_name):
        #     result_message = 'Ви вже в паті'
        # else:
        #     FullName = user_first_name + ' ' + user_last_name
        #     InsertData(chat_id, user_id, FullName)
        #     result_message = 'Ви успішно додані до бази даних' + ' Ваше айді: ' + str(user_id) + ' Айді чату: ' + str(chat_id) + \
        #            ' Вас звати: ' + user_first_name + ' ' + user_last_name
        # return result_message
    elif user_message in ('так'):
        return "ok"
    elif user_message in ('ні'):
        return "ok"
    elif user_message in ('показати список masters',):
        return ShowData(message)
    else:
        return ""
