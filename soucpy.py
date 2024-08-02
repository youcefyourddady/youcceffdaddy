import os
import telebot
import requests
import time

# ملف حفظ المستخدمين المسموح لهم
AUTHORIZED_USERS_FILE = 'authorized_users.txt'

# قائمة المستخدمين المسموح لهم
AUTHORIZED_USER_IDS = set()

# ايدي حسابات الادمن
ADMIN_USER_IDS = [6905993209]

# توكن بوت
bot = telebot.TeleBot('7076972322:AAE541bvGio9T-K2FS2K8lH59LM-HwKsvl8')

# تحميل قائمة المستخدمين المسموح لهم من الملف
def load_authorized_users():
    if os.path.exists(AUTHORIZED_USERS_FILE):
        with open(AUTHORIZED_USERS_FILE, 'r') as file:
            return set(map(int, file.read().splitlines()))
    return set()

# حفظ قائمة المستخدمين المسموح لهم إلى الملف
def save_authorized_users():
    with open(AUTHORIZED_USERS_FILE, 'w') as file:
        file.write('\n'.join(map(str, AUTHORIZED_USER_IDS)))

# تحميل المستخدمين عند بدء تشغيل البوت
AUTHORIZED_USER_IDS = load_authorized_users()

@bot.message_handler(func=lambda message: message.from_user.id in AUTHORIZED_USER_IDS, content_types=['text'])
def handle_message(message):
    if message.text.startswith('/start'):
        bot.send_message(message.chat.id, 'Enter your phone number:')
        bot.register_next_step_handler(message, get_phone_number)
    elif message.text.startswith('/reset'):
        reset_bot(message)
    elif message.text.startswith('/adduser') and message.from_user.id in ADMIN_USER_IDS:
        bot.send_message(message.chat.id, 'Enter the user ID to add:')
        bot.register_next_step_handler(message, add_user)
    elif message.text.startswith('/removeuser') and message.from_user.id in ADMIN_USER_IDS:
        bot.send_message(message.chat.id, 'Enter the user ID to remove:')
        bot.register_next_step_handler(message, remove_user)
    else:
        bot.send_message(message.chat.id, 'Invalid command. Please start with /start or /reset')

def reset_bot(message):
    bot.send_message(message.chat.id, 'Bot has been reset.')
    # Add any code here to clean up or reset the bot's state

def add_user(message):
    try:
        new_user_id = int(message.text)
        if new_user_id not in AUTHORIZED_USER_IDS:
            AUTHORIZED_USER_IDS.add(new_user_id)
            save_authorized_users()  # حفظ التحديثات إلى الملف
            bot.send_message(message.chat.id, f'User {new_user_id} has been added.')
        else:
            bot.send_message(message.chat.id, f'User {new_user_id} is already in the list.')
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid user ID. Please enter a numeric user ID.')

def remove_user(message):
    try:
        user_id_to_remove = int(message.text)
        if user_id_to_remove in AUTHORIZED_USER_IDS:
            AUTHORIZED_USER_IDS.remove(user_id_to_remove)
            save_authorized_users()  # حفظ التحديثات إلى الملف
            bot.send_message(message.chat.id, f'User {user_id_to_remove} has been removed.')
        else:
            bot.send_message(message.chat.id, f'User {user_id_to_remove} is not in the list.')
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid user ID. Please enter a numeric user ID.')

def get_phone_number(message):
    num = message.text
    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'ibiza.ooredoo.dz',
            'Connection': 'Keep-Alive',
            'User-Agent': 'okhttp/4.9.3',
        }

        data = {
            'client_id': 'ibiza-app',
            'grant_type': 'password',
            'mobile-number': num,
            'language': 'AR',
        }

        response = requests.post('https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token', headers=headers, data=data)

        if 'ROOGY' in response.text:
            bot.send_message(message.chat.id, 'OTP code sent. Enter OTP:')
            bot.register_next_step_handler(message, get_otp, num)
            return
        else:
            attempt += 1
            if attempt < max_attempts:
                bot.send_message(message.chat.id, 'Error, please try again later. Attempt {}/{}'.format(attempt, max_attempts))
            else:
                bot.send_message(message.chat.id, 'Failed to verify phone number after {} attempts.'.format(max_attempts))

def get_otp(message, num):
    otp = message.text
    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'ibiza.ooredoo.dz',
            'Connection': 'Keep-Alive',
            'User-Agent': 'okhttp/4.9.3',
        }

        data = {
            'client_id': 'ibiza-app',
            'otp': otp,
            'grant_type': 'password',
            'mobile-number': num,
            'language': 'AR',
        }

        response = requests.post('https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token', headers=headers, data=data)

        access_token = response.json().get('access_token')
        if access_token:
            url = 'https://ibiza.ooredoo.dz/api/v1/mobile-bff/users/mgm/info/apply'

            headers = {
                'Authorization': f'Bearer {access_token}',
                'language': 'AR',
                'request-id': 'ef69f4c6-2ead-4b93-95df-106ef37feefd',
                'flavour-type': 'gms',
                'Content-Type': 'application/json'
            }

            payload = {
                "mgmValue": "ABC"
            }

            counter = 0
            while counter < 12:
                response = requests.post(url, headers=headers, json=payload)

                if 'EU1002' in response.text:
                    bot.send_message(message.chat.id, 'تم ارسال الانترنيت')
                else:
                    bot.send_message(message.chat.id, 'تحقق من الانترنيت عندك الان وعد لاحقا ....')

                counter += 1
                time.sleep(0)

            return
        else:
            attempt += 1
            if attempt < max_attempts:
                bot.send_message(message.chat.id, 'Error verifying OTP. Attempt {}/{}'.format(attempt, max_attempts))
            else:
                bot.send_message(message.chat.id, 'Failed to verify OTP after {} attempts.'.format(max_attempts))

@bot.message_handler(func=lambda message: message.from_user.id not in AUTHORIZED_USER_IDS, content_types=['text'])
def handle_unauthorized(message):
    bot.send_message(message.chat.id, 'انت غير مشترك بالبوت ياخي العزيز، يلزمك تشنرك')

bot.polling(none_stop=True)
