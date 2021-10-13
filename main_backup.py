# coding=UTF-8
#!/usr/bin/env python

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram import filters
from pyrogram.errors import FloodWait
import configparser
import random
import pyexcel
from requests import get
from datetime import datetime, timedelta, timezone
import os
import time
import psycopg2
import traceback
import xml.etree.ElementTree as ET
from cryptozor import Cryptozor


config = configparser.ConfigParser()
config.read('./token.ini')
api_id = config.get("pyrogram", "api_id")
api_hash = config.get("pyrogram", "api_hash")
bot = Client(
    "my_account",
    api_id = api_id,
    api_hash= api_hash
)

#DATABASE_URL = os.environ['DATABASE_URL']
#connection = psycopg2.connect(DATABASE_URL)
connection = psycopg2.connect('postgres://peshtfmscffdxn:580b0c06eea61ed8bbf114ef8c7d964b67ad65009d4194bb4197cd636abb06e6@ec2-54-170-123-247.eu-west-1.compute.amazonaws.com:5432/dfo4gp6u86j4u')

state_full_start = filters.create(func=lambda _, __, message: message.text == '@@')

state_start = filters.create(func=lambda _, __, message: check_status(message.from_user.id) == 0)

state_city = filters.create(func=lambda _, __, message: check_status(message.from_user.id) == 1)

state_product = filters.create(func=lambda _, __, message: check_status(message.from_user.id) == 2)

state_area = filters.create(func=lambda _, __, message: check_status(message.from_user.id) == 3)

state_method = filters.create(func=lambda _, __, message: check_status(message.from_user.id) == 4)

state_payment = filters.create(func=lambda _, __, message: check_status(message.from_user.id) == 5)

state_help = filters.create(func=lambda _, __, message: message.text == '?')

state_history = filters.create(func=lambda _, __, message: message.text == '*')

state_trans = filters.create(func=lambda _, __, message: message.text == '/')

def is_int(number):
    try:
        int(number)
        return True
    except:
        return False


def check_status(chat_id):
    cursor = connection.cursor()
    cursor.execute("SELECT state FROM clients WHERE chat_id = (%s)", [chat_id])
    status = cursor.fetchall()
    if len(status) > 0:
        return status[0][0]
    return False


@bot.on_message(state_full_start)
def full_start(client, message):
    try:
        bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
)
        data = pyexcel.get_array(file_name="./cities.xlsx")
        cities = [f"🏠 <b>{item[0]}</b>\n[ Для выбора отправьте 👉 {item[1]} ]" for item in data]
        random.shuffle(cities)
        cities = '\n➖➖➖➖\n'.join(cities)
        message.reply_text(text= f"""
<b>Вас приветствует магазин - off24 .biz  
В СВЯЗИ С ПРОБЛЕМАМИ С ПОСТАВКАМИ, НАМ ПОДНЯЛИ ЦЕНУ НА РЕАГЕНТ В 2 РАЗА!!! МЫ ВЫНУЖДЕНЫ ПОДНИМАТЬ ЦЕНУ!! ПРИ ПЕРВОЙ ВОЗМОЖНОСТИ ЦЕНЫ СНИЗИМ!! СПАСИБО ЧТО ВЫ С НАМИ!!! 
Наши контакты:</b>
Telegram: <a href = 'http://t.me/offkate'>@KateOff</a> 
Сайт автопродаж - https://off24bizwqmqbbbs .biz
 
Удачных покупок!
➖➖➖➖➖➖➖➖➖➖
Привет, <b>{message.from_user.username}</b>
Ваш баланс: 💰0 руб.
➖➖➖➖➖➖➖➖➖➖
Для пополнения баланса отправьте 👉/pay или ! 
Для просмотра баланса отправьте 👉/balance или = 
Для просмотра истории операций по счету отправьте 👉 /history или * 
➖➖➖➖➖➖➖➖➖➖
Если у Вас завис платеж или не пополнился баланс отправьте 👉/exticket или _ 
Чтобы посмотреть список заявок на покупки или пополнения через SIM или банковскую карту отправьте 👉/trans или / 
➖➖➖➖➖➖➖➖➖➖
Для получения помощи отправьте 👉 /help или ? 
Для просмотра последнего заказа отправьте 👉 /lastorder или # 
➖➖➖➖➖➖➖➖➖➖
<b>Выберите город:</b>
➖➖➖➖➖➖➖➖➖➖
{''.join(cities)}
""", parse_mode='HTML', disable_web_page_preview= True)
        cursor = connection.cursor()
        if is_int(check_status(message.from_user.id)):
            cursor.execute("UPDATE clients SET state = (1) WHERE chat_id = (%s)", [message.from_user.id])
            connection.commit()
        else:
            cursor.execute("INSERT INTO clients VALUES(%s, 1)", [message.from_user.id])
            connection.commit()
        message.stop_propagation()
    except FloodWait as e:
        print(e)
        time.sleep(e.x)
    except Exception as e:
        print(e)
        time.sleep(1)

@bot.on_message(filters.regex('@') | filters.command(['start']))
def alternative_start(client, message):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT captcha FROM clients WHERE chat_id = (%s)", [message.from_user.id])
        captcha_time = cursor.fetchall()
        offset = timezone(timedelta(hours=7))
        if len(captcha_time) > 0:
            if datetime.strptime(captcha_time[0][0], '%m/%d/%y %H:%M:%S').replace(tzinfo=None) < datetime.now(offset).replace(tzinfo=None):
                bot.send_chat_action(
                    chat_id=message.chat.id,
                    action="upload_photo"
                )
                captcha = random.choice(os.listdir('./captcha'))
                cursor.execute("UPDATE clients SET state = (0) WHERE chat_id = (%s)", [message.from_user.id])
                cursor.execute("UPDATE clients SET image = (%s) WHERE chat_id = (%s)", [captcha.replace('.jpg', ''), message.from_user.id])
                connection.commit()
                print('test6')
                with open('./captcha/'+captcha, 'rb') as file:
                    print(file)
                    bot.send_photo(chat_id = message.from_user.id, photo= file, caption= f'''
Введите код с картинки 👆
➖➖➖➖➖➖➖➖➖
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''')
                print('test5')
                message.stop_propagation()
            else:
                bot.send_chat_action(
                    chat_id=message.chat.id,
                    action="typing"
                )
                data = pyexcel.get_array(file_name="./cities.xlsx")
                cities = [f"🏠 <b>{item[0]}</b>\n[ Для выбора отправьте 👉 {item[1]} ]" for item in data]
                random.shuffle(cities)
                cities = '\n➖➖➖➖➖\n'.join(cities)
                message.reply_text(text= f"""
Привет, <b>{message.from_user.username}</b>
Ваш баланс:💰 0 руб
➖➖➖➖➖
Для просмотра полного сообщения (с контактами магазина и командами бота) отправьте 👉 @@
➖➖➖➖➖
<b>Выберите город:</b>
➖➖➖➖➖
{''.join(cities)}""", parse_mode='HTML')
                cursor = connection.cursor()
                cursor.execute("UPDATE clients SET state = (1) WHERE chat_id = (%s)", [message.from_user.id])
                connection.commit()
        else:
            captcha = random.choice(os.listdir('./captcha'))
            cursor.execute("INSERT INTO clients(chat_id, state, captcha, image) VALUES(%s, %s, %s, %s)", 
            [message.from_user.id, 0, datetime.strftime(datetime.now(offset) - timedelta(minutes = 30), "%m/%d/%y %H:%M:%S"), captcha.replace('.jpg', '')])
            connection.commit()
            bot.send_photo(chat_id = message.from_user.id, photo= open('./captcha/'+ captcha, 'rb'), caption= f'''
Введите код с картинки 👆
➖➖➖➖➖➖➖➖➖
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''')
        
    except FloodWait as e:
        time.sleep(e.x)
    except Exception as e:
        print(e)
        time.sleep(1)

@bot.on_message(state_start)
def captcha_check(client, message):
    try:
        bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT captcha FROM clients WHERE chat_id = (%s)", [message.from_user.id])
        captcha_time = cursor.fetchall()
        offset = timezone(timedelta(hours=7))
        if len(captcha_time) > 0:
            if datetime.strptime(captcha_time[0][0], '%m/%d/%y %H:%M:%S').replace(tzinfo=None) < datetime.now(offset).replace(tzinfo=None):
                cursor.execute("SELECT image FROM clients WHERE chat_id = (%s)", [message.from_user.id])
                answer = cursor.fetchall()[0][0]
                if message.text == answer:
                    data = pyexcel.get_array(file_name="./cities.xlsx")
                    cities = [f"🏠 <b>{item[0]}</b>\n[ Для выбора отправьте 👉 {item[1]} ]" for item in data]
                    random.shuffle(cities)
                    cities = '\n➖➖➖➖➖\n'.join(cities)
                    message.reply_text(text= f"""
Привет, <b>{message.from_user.username}</b>
Ваш баланс:💰 0 руб
➖➖➖➖➖
Для просмотра полного сообщения (с контактами магазина и командами бота) отправьте 👉 @@
➖➖➖➖➖
<b>Выберите город:</b>
➖➖➖➖➖
{''.join(cities)}""", parse_mode='HTML')
                    cursor = connection.cursor()
                    cursor.execute("UPDATE clients SET state = (1) WHERE chat_id = (%s)", [message.from_user.id])
                    cursor.execute("UPDATE clients SET captcha = (%s) WHERE chat_id = (%s)", 
                        [datetime.strftime(datetime.now(offset) + timedelta(minutes = 30), "%m/%d/%y %H:%M:%S"), message.from_user.id])
                    connection.commit()
                else:
                    bot.send_message(chat_id = message.chat.id, text= '''Неправильный код проверки. Попробуйте еще раз
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''')
        else:
            print('test')
            captcha = random.choice(os.listdir('./captcha'))
            cursor.execute("INSERT INTO clients(chat_id, state, captcha, image) VALUES(%s, %s, %s, %s)", 
            [message.from_user.id, 0, datetime.strftime(datetime.now(offset) - timedelta(minutes = 30), "%m/%d/%y %H:%M:%S"), captcha.replace('.jpg', '')])
            connection.commit()
            bot.send_photo(chat_id = message.from_user.id, photo= open('./captcha/'+ captcha, 'rb'), caption= f'''
Введите код с картинки 👆
➖➖➖➖➖➖➖➖➖
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''')
        message.stop_propagation()
    except FloodWait as e:
        time.sleep(e.x)
    except:
        time.sleep(1)
    message.stop_propagation()

@bot.on_message(state_city, group=1)
def product_choice(client, message):
    try:
        bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )
        cities = pyexcel.get_array(file_name="./cities.xlsx")
        cities_numbers = [str(item[1]) for item in cities]
        if message.text in cities_numbers:
            cursor = connection.cursor()
            cursor.execute("UPDATE clients SET city = (%s) WHERE chat_id = (%s)", [message.text, message.from_user.id])
            connection.commit()
            city_number = cities_numbers[cities_numbers.index(message.text)]
            city = [item[0] for item in cities if str(item[1]) == str(city_number)][0]
            products = pyexcel.get_array(file_name=f"./products/{city_number}.xlsx")
            products = [f"\n🎁 <b>{item[0]}</b>\n💰 Цена: <b>{item[1]} руб.</b>\n[ Для покупки отправьте 👉 {item[2]} ]\n" for item in products]
            random.shuffle(products)
            answer = '➖➖➖➖➖➖➖➖➖'.join(products)
            message.reply_text(text = f'''🏠 Город: <b>{city}</b> 
➖➖➖➖➖➖➖➖➖
Выберите товар: 
➖➖➖➖➖➖➖➖➖{answer}
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''', parse_mode='HTML')
            if is_int(check_status(message.from_user.id)):
                cursor.execute("UPDATE clients SET state = (2) WHERE chat_id = (%s)", [message.from_user.id])
                connection.commit()
            else:
                cursor.execute("INSERT INTO clients VALUES(%s, 1)", [message.from_user.id])
                connection.commit()
        else:
            message.reply_text(text = f'''
Выберите город строго из списка
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''')
        message.stop_propagation()
    except FloodWait as e:
        time.sleep(e.x)
    except:
        time.sleep(1)
    message.stop_propagation()

@bot.on_message(state_product, group=1)
def area_choice(client, message):
    try:
        bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT city FROM clients WHERE chat_id = (%s)", [message.from_user.id])
        city_number = cursor.fetchall()[0][0]
        cities = pyexcel.get_array(file_name="./cities.xlsx")
        city = [item[0] for item in cities if str(item[1]) == str(city_number)][0]
        products = pyexcel.get_array(file_name=f"./products/{city_number}.xlsx")
        items = [str(item[2]) for item in products]
        if message.text in items:
            cursor.execute("UPDATE clients SET product = (%s) WHERE chat_id = (%s)", [message.text, message.from_user.id])
            connection.commit()
            areas = pyexcel.get_array(file_name=f"./areas/{city_number}/{message.text}.xlsx")
            areas = [f"\n🏃 район <b>{item[0]}</b>\n[ Для выбора отправьте 👉 {item[1]} ]\n" for item in areas]
            random.shuffle(areas)
            answer = '➖➖➖➖➖'.join(areas)
            name = [item[0] for item in products if str(item[2]) == message.text][0]
            amount = [item[1] for item in products if str(item[2]) == message.text][0]
            message.reply_text(text = f'''
🏠 Город: <b>{city}</b>
🎁 Товар: <b>{name}</b>
💰 Цена: <b>{amount} руб.</b>
➖➖➖➖➖➖
Выберите район: 
➖➖➖➖➖➖{answer}
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''', parse_mode='HTML')
            if is_int(check_status(message.from_user.id)):
                cursor.execute("UPDATE clients SET state = (3) WHERE chat_id = (%s)", [message.from_user.id])
                connection.commit()
            else:
                cursor.execute("INSERT INTO clients VALUES(%s, 1)", [message.from_user.id])
                connection.commit()
        else:
            message.reply_text(text = f'''
Выберите продукт строго из списка
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''')
        message.stop_propagation()
    except FloodWait as e:
        time.sleep(e.x)
    except:
        time.sleep(1)
    message.stop_propagation()

@bot.on_message(state_area, group=1)
def method_choice(client, message):
    try:
        bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )
        cursor = connection.cursor()
        cursor.execute("SELECT city FROM clients WHERE chat_id = (%s)", [message.from_user.id])
        city_number = cursor.fetchall()[0][0]
        cities = pyexcel.get_array(file_name="./cities.xlsx")
        city = [item[0] for item in cities if str(item[1]) == str(city_number)][0]
        products = pyexcel.get_array(file_name=f"./products/{city_number}.xlsx")
        cursor.execute("SELECT product FROM clients WHERE chat_id = (%s)", [message.from_user.id])
        product_number = cursor.fetchall()[0][0]
        name = [item[0] for item in products if str(item[2]) == str(product_number)][0]
        amount = [item[1] for item in products if str(item[2]) == str(product_number)][0]
        areas = pyexcel.get_array(file_name=f"./areas/{city_number}/{product_number}.xlsx")
        area_numbers = [str(item[1]) for item in areas]
        if message.text in area_numbers:
            cursor.execute("UPDATE clients SET area = (%s) WHERE chat_id = (%s)", [message.text, message.from_user.id])
            connection.commit()
            area = [item[0] for item in areas if str(item[1]) == message.text][0]
            methods_numbers = pyexcel.get_array(file_name=f"./payments.xlsx")
            methods = [f"\n<b>{item[0]}</b>\n[ Для выбора отправьте 👉 {item[1]} ]\n" for item in methods_numbers]
            random.shuffle(methods)
            answer = '➖➖➖➖➖'.join(methods)
            message.reply_text(text = f'''
🏠 Город: <b>{city}</b>
🏃 Район: <b>{area}</b>
🎁 Название: <b>{name}</b>
💰 Стоимость: <b>{amount} руб.</b>
➖➖➖➖➖➖➖
Выберите метод оплаты:
➖➖➖➖➖➖➖{answer}
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''', parse_mode='HTML')
            if is_int(check_status(message.from_user.id)):
                cursor.execute("UPDATE clients SET state = (4) WHERE chat_id = (%s)", [message.from_user.id])
                connection.commit()
            else:
                cursor.execute("INSERT INTO clients VALUES(%s, 1)", [message.from_user.id])
                connection.commit()
        else:
            message.reply_text(text = f'''
Выберите район строго из списка
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''')
        message.stop_propagation()
    except FloodWait as e:
        time.sleep(e.x)
    except:
        time.sleep(1)
    message.stop_propagation()

@bot.on_message(state_method)
def pay_choice(clientm, message):
    try:
        bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT city FROM clients WHERE chat_id = (%s)", [message.from_user.id])
        city_number = cursor.fetchall()[0][0]
        cities = pyexcel.get_array(file_name="./cities.xlsx")
        city = [item[0] for item in cities if str(item[1]) == str(city_number)][0]
        products = pyexcel.get_array(file_name=f"./products/{city_number}.xlsx")
        cursor.execute("SELECT product FROM clients WHERE chat_id = (%s)", [message.from_user.id])
        product_number = cursor.fetchall()[0][0]
        name = [item[0] for item in products if str(item[2]) == str(product_number)][0]
        amount = [item[1] for item in products if str(item[2]) == str(product_number)][0]
        areas = pyexcel.get_array(file_name=f"./areas/{city_number}/{product_number}.xlsx")
        cursor.execute("SELECT area FROM clients WHERE chat_id = (%s)", [message.from_user.id])
        area_number = cursor.fetchall()[0][0]
        area = [item[0] for item in areas if str(item[1]) == str(area_number)][0]
        methods = pyexcel.get_array(file_name=f"./payments.xlsx")
        methods_numbers = [str(item[1]) for item in methods]
        if message.text in methods_numbers:
            if message.text == '1':
                connection.commit()
                method = 'Bitcoin'
                btc_address = pyexcel.get_array(file_name=f"./payments.xlsx")[0][2]
                btc_amount = get(f'https://blockchain.info/tobtc?currency=RUB&value={amount}').json()
                bot.send_message(chat_id= message.chat.id, text= f'''
🏠 Город: <b>{city}</b>
🏃 Район: <b>{area}</b>
🎁 Название: <b>{name}</b>
💰 Стоимость: <b>{amount} руб.</b>
💱 Метод оплаты: <b>{method}</b>
➖➖➖➖➖➖➖➖➖
Для приобретения выбранного товара, оплатите:
➖➖➖➖➖➖➖➖➖
💸 <b>{btc_amount} BTC</b>
на Bitcoin кошелек:
<b>{btc_address}</b>
➖➖➖➖➖➖➖➖➖
👉 <a href="https://bitaps.com/api/qrcode/png/bitcoin%{btc_address}%3Famount%3D{btc_amount}" >QR код для более удобной оплаты (если нужен)</a>
➖➖➖➖➖➖➖➖➖
#⃣ <b>Заказ №{random.randint(51367, 99999)}</b>, запомните его.
➖➖➖➖➖➖➖➖➖
Комментарий к платежу
💬 <b>{random.randint(11111111, 99999999)}</b>
➖➖➖➖➖➖➖➖➖
По номеру заказа и комментарию вы сможете узнать статус заказа (получить адрес) в любой момент и с любого устройства на 👉 <a href= "https://off24.biz/check">нашем сайт</a>.
➖➖➖➖➖➖➖➖➖
Комментарий служит исключительно для идентификации Вашего заказа. Отправлять BTC с комментарием не нужно, достаточно просто на указанный кошелек перевести точную сумму, дождаться 1 подтверждение в системе Bitcoin, после чего Вы получите свой адрес. Оплачивать необходимо одним переводом. Сумма перевода и кошелек должны быть точными, как указано в реквизитах выше, иначе Ваша оплата не засчитается. Будьте внимательны, так как при ошибочном платеже получить адрес или возврат средств будет невозможно!
➖➖➖➖➖➖➖➖➖
После оплаты отправьте любую цифру и если на Вашем платеже есть 1 подтверждение - Вы получите адрес. Так же, получить адрес можно и на нашем сайте, на странице 👉 <a href= "https://off24.biz/check">проверка заказа</a>. Создать свой кошелек Bitcoin можно 👉 <a href= "https://blockchain.info/ru/wallet/new">здесь</a> или 👉 <a href= "https://bitcoin.org/ru/choose-your-wallet">здесь</a>.
➖➖➖➖➖➖➖➖➖
Купить Bitcoin можно через обменники, например 👉 <a href= "http://www.bestchange.ru/qiwi-to-bitcoin.html">здесь</a>.
➖➖➖➖➖➖➖➖➖
Для того, чтобы посмотреть последний Ваш заказ нажмите 👉 /lastorder
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''', parse_mode = 'HTML')
                if is_int(check_status(message.from_user.id)):
                    cursor.execute("UPDATE clients SET state = (5) WHERE chat_id = (%s)", [message.from_user.id])
                    cursor.execute("UPDATE clients SET method = (1) WHERE chat_id = (%s)", [message.from_user.id])
                    connection.commit()

            elif message.text == '7':
                connection.commit()
                method = 'Litecoin'
                ltc_address = pyexcel.get_array(file_name=f"./payments.xlsx")[4][2]
                cryptozor = Cryptozor('rub', 'ltc')
                ltc_amount = cryptozor.convert(amount)
                bot.send_message(chat_id= message.chat.id, text= f'''
🏠 Город: <b>{city}</b>
🏃 Район: <b>{area}</b>
🎁 Название: <b>{name}</b>
💰 Стоимость: <b>{amount} руб.</b>
💱 Метод оплаты: <b>{method}</b>
➖➖➖➖➖➖➖➖➖
Для приобретения выбранного товара, оплатите:
➖➖➖➖➖➖➖➖➖
💸 <b>{ltc_amount} LTC</b>
на Litecoin кошелек:
<b>{ltc_address}</b>
➖➖➖➖➖➖➖➖➖
👉 <a href="https://bitaps.com/api/qrcode/png/litcoin%{ltc_address}%3Famount%3D{ltc_amount}" >QR код для более удобной оплаты (если нужен)</a>
➖➖➖➖➖➖➖➖➖
#⃣ <b>Заказ №{random.randint(51367, 99999)}</b>, запомните его.
➖➖➖➖➖➖➖➖➖
Комментарий к платежу
💬 <b>{random.randint(11111111, 99999999)}</b>
➖➖➖➖➖➖➖➖➖
По номеру заказа и комментарию вы сможете узнать статус заказа (получить адрес) в любой момент и с любого устройства на 👉 <a href= "https://off24.biz/check">нашем сайт</a>.
➖➖➖➖➖➖➖➖➖
Комментарий служит исключительно для идентификации Вашего заказа. Отправлять LTC с комментарием не нужно, достаточно просто на указанный кошелек перевести точную сумму, дождаться 1 подтверждение в системе Litecoin, после чего Вы получите свой адрес. Оплачивать необходимо одним переводом. Сумма перевода и кошелек должны быть точными, как указано в реквизитах выше, иначе Ваша оплата не засчитается. Будьте внимательны, так как при ошибочном платеже получить адрес или возврат средств будет невозможно!
➖➖➖➖➖➖➖➖➖
После оплаты отправьте любую цифру и если на Вашем платеже есть 1 подтверждение - Вы получите адрес. Так же, получить адрес можно и на нашем сайте, на странице 👉 <a href= "https://off24.biz/check">проверка заказа</a>. Создать свой кошелек Litecoin можно 👉 <a href= "https://litecoin.info/">здесь</a>.
➖➖➖➖➖➖➖➖➖
Купить Litecoin можно через обменники, например 👉 <a href= "http://www.bestchange.ru/qiwi-to-litecoin.html">здесь</a>.
➖➖➖➖➖➖➖➖➖
Для того, чтобы посмотреть последний Ваш заказ нажмите 👉 /lastorder
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''', parse_mode = 'HTML')
                if is_int(check_status(message.from_user.id)):
                    cursor.execute("UPDATE clients SET state = (5) WHERE chat_id = (%s)", [message.from_user.id])
                    cursor.execute("UPDATE clients SET method = (7) WHERE chat_id = (%s)", [message.from_user.id])
                    connection.commit()
            elif message.text == '11':
                method = 'Банковская карта'
                cards = pyexcel.get_array(file_name=f"./payments.xlsx")
                cards = [cards[2][2], cards[2][3], cards[2][4]]
                card = random.choice(cards)
                bot.send_message(chat_id= message.chat.id, text= f'''
    🏠 Город: <b>{city}</b>
🏃 Район: <b>{area}</b>
🎁 Название: <b>{name}</b>
💰 Стоимость: <b>{amount + 234} руб.</b>
💱 Метод оплаты: <b>{method}</b>
➖➖➖➖➖➖➖➖➖
Для приобретения выбранного товара, оплатите:
➖➖➖➖➖➖➖➖➖
💰 <b>{amount + 234} руб.</b>
Номер банковской карты для оплаты:
👉 <b>{card}</b>
➖➖➖
<b>Оплатите ТОЧНУЮ СУММУ на номер банковской карты! Обычно это занимает 30-60 секунд.</b>
➖➖➖
<b>Отправьте любую цифру, только после реальной оплаты. Если после этого система не увидит Вашу оплату в течении 3х минут, ваш заказ будет отменен и Вы не получите ни товар, ни деньги на баланс.</b>
➖➖➖
Оплата принимается только на <b>НОМЕР БАНКОВСКОЙ КАРТЫ</b>. Пополнить банковскую карту можно любым удобным способом, например: со своего QIWI-кошелька, терминала, банковской карты (card2card), Yandex.Деньги, Payeer, WebMoney и другие платежные системы.
➖➖➖
Переводите обязательно <b>ТОЧНУЮ</b> сумму, которую Вам выдал бот! Пожалуйста, учитывайте сумму комиссии к платежу!
➖➖➖
<b>Любая цифра отправляется в самый последний момент, когда Вы произвели оплату и уверены в точной сумме. При точном выполнении всех правил - Вы получите товар.</b>
➖➖➖
Вопросы по зависшим платежам принимаются в течении суток с момента оплаты. Если Вы не получили товар, но реально перевели деньги на выданные Вам реквизиты - свяжитесь со службой поддержки обменника отправив /exticket, обязательно укажите номер заявки и детали вашего платежа вместе с точной суммой оплаты. Скриншоты чеков обязательны! По истечении суток запросы по зависшим платежам не принимаются!
➖➖➖
Заявки обрабатываются через сторонний обменник, если Вы создали обращение по зависшему платежу и Вашу проблему не решили - обратитесь к Администрации магазина.
➖➖➖
❗️ После оплаты отправьте любую цифру
➖➖➖
#⃣ <b>Заказ №{random.randint(51367, 99999)}</b>, запомните его.
➖➖➖
Комментарий для проверки
💬 <b>{random.randint(11111111, 99999999)}</b>
➖➖➖
❗️ Внимание! Оплачивать с комментарием не нужно. Номер заказа и комментарий служит исключительно для проверки платежа на странице проверки заказа.
По номеру заказа и комментарию вы сможете узнать статус заказа (получить адрес) в любой момент и с любого устройства на 👉 <a href= "https://csabk24.biz/check">нашем сайт</a>.
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''', parse_mode = 'HTML', disable_web_page_preview= True)
                if is_int(check_status(message.from_user.id)):
                    cursor.execute("UPDATE clients SET state = (5) WHERE chat_id = (%s)", [message.from_user.id])
                    cursor.execute("UPDATE clients SET method = (11) WHERE chat_id = (%s)", [message.from_user.id])
                    connection.commit()

            elif message.text == '8':
                method = 'EXMO код'
                root = ET.fromstring(get('http://www.cbr.ru/scripts/XML_daily.asp?').text)
                for child in root.findall('Valute'):
                    rank = child.find('CharCode').text
                    if rank == 'USD':
                        usd_curse = float(str(child.find('Value').text).replace(',','.'))
                    if rank == 'EUR':
                        eur_curse = float(str(child.find('Value').text).replace(',','.'))
                bot.send_message(chat_id= message.chat.id, text= f'''
🏠 Город: <b>{city}</b>
🏃 Район: <b>{area}</b>
🎁 Название: <b>{name}</b>
💰 Стоимость: <b>{amount} руб.</b>
💱 Метод оплаты: <b>EXMO код</b>
➖➖➖➖➖➖➖➖➖
Для приобретения выбранного товара, оплатите:
➖➖➖➖➖➖➖➖➖
👉 <b>{amount} рублей</b>
или
👉 <b>{str(float('{:.1f}'.format(amount / usd_curse)))} USD</b>
или
👉<b>{str(float('{:.1f}'.format(amount / eur_curse)))} EUR</b>
➖➖➖➖➖➖➖➖➖➖
с помощью 👉 EXMO кода и 👉 СРАЗУ отправьте его в ответном сообщении
➖➖➖➖➖➖➖➖➖➖
Внимание! Если EXMO код будет на сумму меньше, чем сумма товара, вы не получите адрес и деньги не будут возвращены. Если EXMO код будет на сумму больше стоимости товара, то вы получите адрес, но не получите сдачу. Будьте внимательны при расчете комиссий обменников - сумма кода должна точь в точь совпадать с суммой товара (учтите комисии обменников). Будьте внимательны!
➖➖➖➖➖➖➖➖➖➖
Если Вы используете EXMO USD (долларовый) или EXMO EUR (евровый) код, то при активации система автоматически перерасчитает Ваш код в рубли по официальному курсу.
➖➖➖➖➖➖➖➖➖➖
#⃣ <b>Заказ №{random.randint(51367, 99999)}</b>, запомните его.
➖➖➖➖➖➖➖➖➖➖
По номеру заказа и коду вы сможете узнать статус заказа (получить адрес) в любой момент и с любого устройства на 👉 <a href= "https://csabk24.biz/check">нашем сайте</a>.
➖➖➖➖➖➖➖➖➖➖
Купить EXMO-код можно через обменники, например 👉 https://www.bestchange.ru/qiwi-to-exmo-rub.html
➖➖➖➖➖➖➖➖➖➖
Для того, чтобы посмотреть последний Ваш заказ нажмите 👉 /lastorder

Чтобы вернуться в меню и начать сначала нажмите 👉 /start или @''', parse_mode = 'HTML', disable_web_page_preview= True)
                if is_int(check_status(message.from_user.id)):
                    cursor.execute("UPDATE clients SET state = (5) WHERE chat_id = (%s)", [message.from_user.id])
                    cursor.execute("UPDATE clients SET method = (8) WHERE chat_id = (%s)", [message.from_user.id])
                    connection.commit()

            elif message.text == '10':
                method = 'SIM'
                phone = pyexcel.get_array(file_name=f"./payments.xlsx")[3][2]
                message.reply_text(text= f'''
🏠 Город: <b>{city}</b>
🏃 Район: <b>{area}</b>
🎁 Название: <b>{name}</b>
💱 Метод оплаты: <b>SIM</b>
➖➖➖➖➖➖➖➖➖➖
Для приобретения выбранного товара, оплатите:
➖➖➖➖➖➖➖➖➖➖
💰 <b>{amount + 234} руб.</b>
Телефон для оплаты:
👉 <b>{phone}</b>
➖➖➖➖➖➖➖➖➖➖
<b>Оплатите ТОЧНУЮ СУММУ на баланс мобильного телефона! Обычно это занимает 30-60 секунд.</b>
➖➖➖➖➖➖➖➖➖➖
<b>Отправьте любую цифру, только после реальной оплаты.</b> Если после этого система не увидит Вашу оплату в течении 3х минут, ваш заказ будет отменен и Вы не получите ни товар, ни деньги на баланс.
➖➖➖➖➖➖➖➖➖➖
Оплата принимается только на <b>НОМЕР МОБИЛЬНОГО ТЕЛЕФОНА</b>. Пополнять выданный номер можно любым способом, например через терминал, офис мобильного оператора, банковской картой, QIWI и так далее. Не переводите деньги на QIWI или любую другую платежную систему вы их теряете БЕЗ ВОЗМОЖНОСТИ ВОЗВРАТА!
➖➖➖➖➖➖➖➖➖➖
Переводите обязательно <b>ТОЧНУЮ</b> сумму, которую Вам выдал бот! Многие терминалы берут комиссию и с них сложно оплатить точную сумму, старайтесь этого избегать.
➖➖➖➖➖➖➖➖➖➖
<b>Любая цифра отправляется в самый последний момент, когда Вы произвели оплату и уверены в точной сумме. При точном выполнении всех правил - Вы получите товар.</b>
➖➖➖➖➖➖➖➖➖➖
Вопросы по зависшим платежам принимаются в течении суток с момента оплаты. Если Вы не получили товар, но реально перевели деньги на выданные Вам реквизиты - свяжитесь со службой поддержки обменника отправив /exticket, обязательно укажите номер заявки и детали вашего платежа вместе с точной суммой оплаты. Скриншоты чеков обязательны! По истечении суток запросы по зависшим платежам не принимаются!
➖➖➖➖➖➖➖➖➖➖
Заявки обрабатываются через сторонний обменник, если Вы создали обращение по зависшему платежу и Вашу проблему не решили - обратитесь к Администрации магазина.
➖➖➖➖➖➖➖➖➖➖
❗️ После оплаты отправьте любую цифру
➖➖➖➖➖➖➖➖➖➖
#⃣ <b>Заказ №{random.randint(51367, 99999)}</b>, запомните его.
➖➖➖➖➖➖➖➖➖➖
Комментарий для проверки
💬  <b>{random.randint(11111111, 99999999)}</b>
➖➖➖➖➖➖➖➖➖➖
❗️ Внимание! Оплачивать с комментарием не нужно. Номер заказа и комментарий служит исключительно для проверки платежа на странице проверки заказа.
По номеру заказа и комментарию вы сможете узнать статус заказа (получить адрес) в любой момент и с любого устройства на 👉 <a href= "https://csabk24.biz/check">нашем сайте</a>.
Чтобы вернуться в меню и начать сначала нажмите 👉 /start или @''', parse_mode = 'HTML', disable_web_page_preview= True)
                if is_int(check_status(message.from_user.id)):
                    cursor.execute("UPDATE clients SET state = (5) WHERE chat_id = (%s)", [message.from_user.id])
                    cursor.execute("UPDATE clients SET method = (10) WHERE chat_id = (%s)", [message.from_user.id])
                    connection.commit()

        else:
            message.reply_text(text = f'''
Выберите метод оплаты строго из списка
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''')        
        
        message.stop_propagation()
    except FloodWait as e:
        time.sleep(e.x)
    except:
        time.sleep(1)
    message.stop_propagation()

@bot.on_message(state_payment, group=1)
def wait_choice(clientm, message):
    try:
        bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )
        cursor = connection.cursor()
        cursor.execute("SELECT method FROM clients WHERE chat_id = (%s)", [message.from_user.id])
        method = str(cursor.fetchall()[0][0])
        if method == '1':
            message.reply_text(text= f'''
Если вы оплатили заказ и видите это сообщение, скорее всего транзакция имеет 0 подтверждений. Для проверки платежа необходимо как минимум 1 подтверждение в сети Bitcoin. Дождитесь подтверждения и попробуйте проверить заказ позже.
Отправьте любую цифру чтобы проверить платеж еще раз.
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''')
        elif method == '7':
            message.reply_text(text= f'''
Если вы оплатили заказ и видите это сообщение, скорее всего транзакция имеет 0 подтверждений. Для проверки платежа необходимо как минимум 1 подтверждение в сети Bitcoin. Дождитесь подтверждения и попробуйте проверить заказ позже.
Отправьте любую цифру чтобы проверить платеж еще раз.
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''')
        elif method == '8':
            message.reply_text(text= f'''
Данный EXMO код уже был активирован. Свяжитесь с администрацией.
Отправьте любую цифру чтобы проверить платеж еще раз.
Чтобы вернуться в меню и начать сначала нажмите 👉 /start или @''')
        elif method == '11':
            message.reply_text(text= f'''
Заявка принята. Ожидает оплаты
Отправьте любую цифру чтобы проверить платеж еще раз.
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''')
        elif method == '10':
            message.reply_text(text= f'''
Заказ отмечен как оплаченый. Отправьте любую цифру, чтобы узнать статус платежа
Чтобы вернуться в меню и начать сначала отправьте 👉 /start или @''')
        message.stop_propagation()
    except FloodWait as e:
        time.sleep(e.x)
    except:
        time.sleep(1)
    message.stop_propagation()

# commands
@bot.on_message(filters.command('pay') | filters.regex('!'))
def pay_handler(client, message):
    try:
        bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )
        message.reply_text(text= 'В данный момент пополнить баланс без выбора товара невозможно.')
        cursor = connection.cursor()
        cursor.execute('UPDATE clients SET state = (0) WHERE chat_id = (%s)', [message.from_user.id])
        connection.commit()
        message.stop_propagation()
    except FloodWait as e:
        time.sleep(e.x)
    except:
        time.sleep(1)
    message.stop_propagation()

@bot.on_message(filters.command('balance') | filters.regex('='))
def balance_handler(client, message):
    try:
        bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )
        message.reply_text(text= '''   
Ваш баланс:
💰0 руб.
➖➖➖➖➖➖➖➖➖➖
Для пополнения баланса нажмите 👉/pay
Для просмотра баланса нажмите 👉/balance
Для просмотра истории операций по счету 👉/history''')
        cursor = connection.cursor()
        cursor.execute('UPDATE clients SET state = (0) WHERE chat_id = (%s)', [message.from_user.id])
        connection.commit()
        message.stop_propagation()
    except FloodWait as e:
        time.sleep(e.x)
    except:
        time.sleep(1)
    message.stop_propagation()

@bot.on_message(filters.command('exticket') | filters.regex('_'))
def exticket_handler(client, message):
    try:
        bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )
        message.reply_text(text= 'Вы еще не делали пополнений чтобы создавать обращения.')
        cursor = connection.cursor()
        cursor.execute('UPDATE clients SET state = (0) WHERE chat_id = (%s)', [message.from_user.id])
        connection.commit()
        message.stop_propagation()
    except FloodWait as e:
        time.sleep(e.x)
    except:
        time.sleep(1)
    message.stop_propagation()

@bot.on_message(filters.command('history') | state_history)
def history_handler(client, message):
    try:
        bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )
        message.reply_text(text= 'Транзакции не найдены')
        cursor = connection.cursor()
        cursor.execute('UPDATE clients SET state = (0) WHERE chat_id = (%s)', [message.from_user.id])
        connection.commit()
        message.stop_propagation()
    except FloodWait as e:
        time.sleep(e.x)
    except:
        time.sleep(1)
    message.stop_propagation()

@bot.on_message(filters.command('trans') | state_trans)
def trans_handler(client, message):
    try:
        bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )
        message.reply_text(text= 'Функция просмотра выших заявок временно недоступна')
        cursor = connection.cursor()
        cursor.execute('UPDATE clients SET state = (0) WHERE chat_id = (%s)', [message.from_user.id])
        connection.commit()
        message.stop_propagation()
    except FloodWait as e:
        time.sleep(e.x)
    except:
        time.sleep(1)
    message.stop_propagation()

@bot.on_message(filters.command('lastorder') | filters.regex('#'))
def lastorder_handler(client, message):
    try:
        bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )
        message.reply_text(text= '''Функция просмотра последнего заказа временно недоступна
Отправьте 👉 /start или @ для того, чтобы вернуться к выбору города.''')
        cursor = connection.cursor()
        cursor.execute('UPDATE clients SET state = (0) WHERE chat_id = (%s)', [message.from_user.id])
        connection.commit()
        message.stop_propagation()
    except FloodWait as e:
        time.sleep(e.x)
    except:
        time.sleep(1)
    message.stop_propagation()


@bot.on_message(filters.command('help') | state_help)
def help_handler(client, message):
    try:
        bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )
        message.reply_text(text='''
➖➖➖➖➖➖➖➖➖➖
Добро пожаловать в наш магазин.
Уважаемый клиент, будьте внимательны при оплате и выборе товара.
Перед покупкой товара, бот предложит Вам город, товар и удобный для Вас район, после чего, выдаст реквизиты для оплаты.
Внимательно перед покупкой проверяйте товар и выбранный район. Обязательно записывайте реквизиты для оплаты (номер кошелька и комментарий).

При оплате, Вам необходимо обязательно указать  комментарий, который выдал Вам бот, иначе оплата не будет засчитана в автоматическом режиме и Вы не получите адрес.
Всегда записывайте номер заказа и комментарий, с помощью них, вы сможете узнать статус заказа (получить адрес) в любой момент и с любого устройства. 
Сохраняйте чек до тех пор, пока не получили адрес. Присутствует возможность производить несколько платежей с одним комментарием. Платежи суммируются и в случае, если сумма полная - Вы получаете свой адрес.
Будьте внимательны, кошелек, комментарий и сумма должны быть точными. Если возникли какие-либо проблемы - обращайтесь к оператору.

После внесения оплаты, нажмите кнопку проверки платежа и если Ваша оплата будет найдена - Вы получите адрес в автоматическом режиме.
Так же для Вашего удобства реализована возможность просмотра Вашего последнего заказа, для этого необходимо нажать /lastorder
А для того, чтобы вернуться на стартовую страницу к выбору городов, просто нажмите /start или напишите любое сообщение.

Приятных покупок!
➖➖➖➖➖➖➖➖➖➖''')
        cursor = connection.cursor()
        cursor.execute('UPDATE clients SET state = (0) WHERE chat_id = (%s)', [message.from_user.id])
        connection.commit()
        message.stop_propagation()
    except FloodWait as e:
        time.sleep(e.x)
    except:
        time.sleep(1)
    message.stop_propagation()

if __name__ == "__main__":
    while 1:
        try:
            bot.run()
        except: 
            print(traceback.format_exc())
            time.sleep(15)