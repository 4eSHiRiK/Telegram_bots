import requests
from lxml import html
import config
import keyboard
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()
bot = Bot(token=config.botkey, parse_mode=types.ParseMode.HTML)

dp = Dispatcher(bot,storage=storage)

#--------Start_button--------------
@dp.message_handler(commands='start', commands_prefix='!/', state=None)
async def welcome(message):
    start = types.ReplyKeyboardMarkup(resize_keyboard=True)
    joined_users = set()
    if not str(message.chat.id) in joined_users:
        joined_file = open('user_data.txt', 'a')
        joined_file.write('\n'+ str(message.chat.id))
        joined_users.add(message.chat.id)

    await bot.send_message(message.chat.id, f"Hello! *{message.from_user.first_name}*,"
                                            f"Bot is working", reply_markup=start, parse_mode='Markdown')

#----------Info_button----------------
@dp.message_handler(content_types=['text'])
async def get_message(message):
    if message.text == 'Info':
        start = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start.add(keyboard.books)
        await bot.send_message(message.chat.id, f"Click on book to get information about Python",
                           reply_markup=start,parse_mode='Markdown')

#---------books_button----------------
    elif message.text == 'Books':
        start=types.ReplyKeyboardMarkup(resize_keyboard=True)
        back = keyboard.back
        start.add(back)
        page = requests.get('https://realpython.com/best-python-books/', headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'})

        tree = html.fromstring(page.content)
        first_book = tree.xpath('//*[@id="python-crash-course"]/h3//text()')[0]
        second_book = tree.xpath('//*[@id="head-first-python-2nd-edition"]/h3//text()')[0]
        third_book = tree.xpath('//*[@id="invent-your-own-computer-games-with-python-4th-edition"]/h3//text()')[0]
        await bot.send_message(message.chat.id, text=f"There is a list of names helpful books for learning Python:"
                                                     f"\n1.{first_book}\n2.{second_book}\n3.{third_book}", reply_markup=start)
    elif message.text == 'Back':
        start = types.ReplyKeyboardMarkup(resize_keyboard=True)
        info = keyboard.info
        start.add(info)
        await bot.send_message(message.chat.id, text=f'You was returned to main page',
                               reply_markup=start, parse_mode='Markdown')

if __name__ == '__main__':
    print('Bot started')
    executor.start_polling(dp, skip_updates=True)
