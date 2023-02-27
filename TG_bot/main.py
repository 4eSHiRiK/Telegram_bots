import asyncio
import sqlite3

import requests
from aiogram.dispatcher.filters.state import StatesGroup, State
from bs4 import BeautifulSoup
from lxml import html
import config
import keyboard
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import logging

storage = MemoryStorage()
bot = Bot(token=config.bot_key, parse_mode=types.ParseMode.HTML)

dp = Dispatcher(bot, storage=storage)

# logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%levelname-8s [%(asctime)s] %(message)s',
#                     filename='log.txt', level=logging.INFO)

#_____________________________________DATABASE

connect = sqlite3.connect('TG_Bot.db')
cursor = connect.cursor()

cursor.execute(''' CREATE TABLE IF NOT EXISTS user_list_id (id INTEGER PRIMARY KEY AUTOINCREMENT, col_1 TEXT) ''')
connect.commit()




#---------------------------FSM

class Meinfo(StatesGroup):
    Q1 = State()
    Q2 = State()



@dp.message_handler(Command('me'), state=None)
async def enter_me_info(message: types.Message):
    if message.chat.id == config.admin:
        await message.answer('*Start settings*\n'
                             '1) Enter your link',parse_mode='Markdown')
        await Meinfo.Q1.set() #Ждем пока не получим ответ

@dp.message_handler(state=Meinfo.Q1)
async def answer_for_q1(message, state: FSMContext):
    answer = message.text
    await state.update_data(answer1= answer)

    await message.answer('Thanks, Link is saved\n'
                         '2) Enter some description')
    await Meinfo.Q2.set()

@dp.message_handler(state=Meinfo.Q2)
async def answer_for_q2(message, state: FSMContext):
    answer = message.text
    await state.update_data(answer2= answer)

    await message.answer('Thanks, Description is saved')

    data = await state.get_data()
    answer1= data.get('answer1')
    answer2 = data.get('answer2')

    with open('link.txt', 'w', encoding='UTF-8') as joined_file:
        joined_file.write(str(answer1))

    with open('text.txt', 'w', encoding='UTF-8') as text_file:
        text_file.write(str(answer2))


    await message.answer(f"Your link is {answer1},description - {answer2}")

    await state.finish()

#___________________________________Start button
@dp.message_handler(commands='start', commands_prefix='!/', state=None)
async def welcome(message):
    # joined_file = open('user_data.txt','r')
    # joined_users = set()
    # for line in joined_file:
    #     joined_users.add(line.strip())
    # if not str(message.chat.id) in joined_users:
    #     joined_file = open('user_data.txt', 'a')
    #     joined_file.write('\n'+str(message.chat.id))
    #     joined_users.add(message.chat.id)
    cursor.execute(''' SELECT col_1 FROM user_list_id''')
    res = cursor.fetchall()
    print(res)
    if list(str(message.chat.id)) not in res:
        cursor.execute(''' INSERT INTO user_list_id (col_1) VALUES (?)''' , (message.chat.id, ))
        connect.commit()


    await bot.send_message(message.chat.id, f"Hello! *{message.from_user.first_name},*"
                                            f' Bot is work', reply_markup=keyboard.start,parse_mode='Markdown')



#---------------------------InlineButtons for stats
@dp.callback_query_handler(text_contains=['join'])
async def join(call):
    if call.message.chat.id == config.admin:
        users = sum(1 for line in open('user_data.txt'))
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                               text=f"This is bot's stats {users} join to bot",
                               parse_mode='Markdown')
    else:
        await bot.send_message(chat_id=call.message.chat_id, text=f"You are not admin",
                               parse_mode='Markdown')

@dp.callback_query_handler(text_contains='cancel')
async def cancel(call):
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=f"You are in head menu. Choose some button",parse_mode='Markdown')

#______________________________InlineButtons for show id
@dp.callback_query_handler(text_contains=['show'])
async def show(call):
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'This is your id {call.message.chat.id}', parse_mode='Markdown')

@dp.callback_query_handler(text_contains=['back'])
async def back(call):
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'You cancel your choise',parse_mode='Markdown')

#_____________________________InlineButtons for Database
@dp.callback_query_handler(text_contains=['database'])
async def database_1(call):
    cursor.execute(''' SELECT * FROM user_list_id''')
    look_db = cursor.fetchall()
    print(look_db)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'This is id database {look_db}', parse_mode='Markdown')

@dp.callback_query_handler(text_contains=['back'])
async def back(call):
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'You cancel your choise', parse_mode='Markdown')


#___________________________InlineButtons for job
@dp.callback_query_handler(text_contains=['bio'])
async def bio(call):
    url = 'https://rabota.by/vacancies/mikrobiolog'
    req = requests.get(url,
                       headers={
                           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
                       })

    soup = BeautifulSoup(req.text, 'lxml')
    search = soup.find_all('a', class_='serp-item__title')
    for elem in search:
        microb = elem['href']
        name = elem.text
        await bot.send_message(call.message.chat.id, f'{name} : {microb}', parse_mode='Markdown')

    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'This is all vacations of Microbiologist',parse_mode='Markdown')


@dp.callback_query_handler(text_contains=['pydev'])
async def pydev(call):
    url = 'https://rabota.by/search/vacancy?text=Python+junior&from=suggest_post&salary=&area=1002&ored_clusters=true&enable_snippets=true'
    req = requests.get(url,
                       headers={
                           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
                       })

    soup = BeautifulSoup(req.text, 'lxml')
    search = soup.find_all('a', class_='serp-item__title')
    for elem in search:
        pydev = elem['href']
        name = elem.text
        await bot.send_message(call.message.chat.id,f'{name} : {pydev}',parse_mode='Markdown')

    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'This is all vacations of Python Dev: \n',
                                parse_mode='Markdown')




#---------------------------------link

@dp.message_handler(commands=['links'], commands_prefix='!/')
async def mailling(message):
    if message.chat.id == config.admin:
        await bot.send_message(message.chat.id, f"Start mailling. Bot will notify at the end",
                               parse_mode='Markdown')

        recieve_user = 0
        block_user = 0
        with open('user_data.txt','r') as file:
            joined_users = set()
            for line in file:
                joined_users.add(line.strip())
            for user in joined_users:
                try:
                    await bot.send_photo(user, open('Безымянный.png','rb'),
                                     message.text[message.text.find(' '):] if ' ' in message.text else 'Take photo')
                    recieve_user += 1
                except:
                    block_user += 1
                await asyncio.sleep(0.4)
            await bot.send_message(message.chat.id, f'Mailling end.\n'
                                                    f'recieve users {recieve_user}\n'
                                                    f'block users {block_user}',parse_mode='Markdown')





#___________________________________information button
@dp.message_handler(content_types=['text'])
async def get_message(message):
    if message.text == 'Information':
        await bot.send_message(message.chat.id, text=f'Hi! I am Python/Django dev\nI do this bot for learning Python')

#___________________________________stats button
    elif message.text == 'Stats':
        # joined_file_s = open('user_data.txt','r')
        # await bot.send_message(message.chat.id, text=f"{joined_file_s.readline()}")
        await bot.send_message(message.chat.id, text=f"Do you wanna see the stats?",
                               reply_markup=keyboard.stats, parse_mode='Markdown')

#____________________________________show_user_button
    elif message.text == 'Show user':
        await bot.send_message(message.chat.id, text=f'Do you wanna see your id?',reply_markup=keyboard.show_user,
                               parse_mode='Markdown')

#______________________________________send_photo button
    elif message.text == 'Send photo':
        await bot.send_photo(message.chat.id, open('cheshir.png','rb'))


#_______________________________________Job_info_button
    elif message.text == 'Job Info':
        await bot.send_message(message.chat.id, text=f'Choose job',reply_markup=keyboard.job_info,
                               parse_mode='Markdown')

#__________________________________________Database Button
    elif message.text == 'Database':
        await bot.send_message(message.chat.id, text=f'DB interface',reply_markup=keyboard.dabase,
                               parse_mode='Markdown')

#___________________________________information button

    elif message.text == 'Weather':
        page = requests.get('https://www.gismeteo.by/', headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'})

        tree = html.fromstring(page.content)
        city = tree.xpath('//a[@class="city-link link"]//text()')[0]
        time = tree.xpath('//div[@class="current-time"]//text()')[0]
        descr = tree.xpath('//div[@class="weather-description"]//text()')[0]
        degrees = ''.join(tree.xpath('//div[@class="temperature"]//text()')[:2])
        await bot.send_message(message.chat.id, text=f'In {city} now {time}\n{degrees} {descr}')


#--------------------------- developer_button
    elif message.text == 'Developer':
        with open('link.txt','r', encoding='UTF-8') as link:
            link = link.read()

        with open('text.txt','r',encoding='UTF-8') as text:
            text = text.read()

        await bot.send_message(message.chat.id, f"This developer {link} created this bot. He's {text}",
                               parse_mode='Markdown')

if __name__ == '__main__':
    print('Bot started')
    executor.start_polling(dp, skip_updates=True)
