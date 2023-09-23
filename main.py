from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
import requests
import os
from dotenv import load_dotenv

load_dotenv()

print('1')

api_token = os.getenv('API_TOKEN')

bot = Bot(token=api_token)

db_path = "./app_data/dbase.db"

storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

class CheckStockStates(StatesGroup):
    StockID = State()

class User:

    def __init__(self, telegram_id) -> None:
        self.telegram_id = telegram_id

    def checkUserRecord(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY)''')
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (self.telegram_id,))
        db_data = cursor.fetchone()
        if db_data is None:
            result = None
            conn.close()
        else:
            result = db_data[0]
            conn.close()    
        return result
    
    def createUserRecord(self):
        insterted_id = None
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY)''')
        cursor.execute('INSERT INTO users (telegram_id) VALUES (?)', (self.telegram_id,))
        conn.commit()
        insterted_id = cursor.lastrowid
        conn.close()
        return insterted_id 

def checkStockExistance(stock_id):
    url = f"https://iss.moex.com/iss/securities/{stock_id}.json"
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        exist = data.get("boards", {}).get("data", [])
        return bool(exist)
    else:
        return False
    
def getStockPrice(stock_id):
    url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{stock_id}.json?iss.only=securities&securities.columns=PREVPRICE,CURRENCYID"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        stock_price = data.get("securities", {}).get("data", [[]])[0][0]
        stock_currency = data.get("securities", {}).get("data", [[]])[0][1]

        if stock_currency == "SUR":
            stock_currency = "RUB"
        stock_info = str(stock_price) + " " + str(stock_currency)
        return stock_info
    else: 
        return False

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user = User(message.from_user.id)
    user_record = user.checkUserRecord()
    if user_record is None:
        user.createUserRecord() 
        await message.reply("Привет! Регистрация прошла успешно")
    else:
        await message.reply("Привет! Вы уже зарегистрированы")

@dp.message_handler(commands=['getStock'])
async def getStock_start(message: types.Message):
    await message.reply("Введите идентификатор ценной бумаги")
    await CheckStockStates.StockID.set()

@dp.message_handler(state=CheckStockStates.StockID)
async def getStock_exec(message: types.Message, state: FSMContext):
    stock_id = message.text.upper()
    if checkStockExistance(stock_id) == True:
        stock_price = getStockPrice(stock_id)
        if stock_price != False:
            await message.reply("Ценная бумага " + str(stock_id) + " найдена на Московской бирже. Стоимость: " + str(stock_price))
        else:
            await message.reply("Не удалось получить данные от Московской биржи")    
    else:
        await message.reply("Не удалось найти ценную бумагу")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)