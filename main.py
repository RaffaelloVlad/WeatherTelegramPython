import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests
from apikey import *


# Установка уровня логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=f'{TelebotAPIKey}')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

output_file = 'E://BotPyWeather//WeatherTelegramPython//.git//sourse//output.txt'

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    # image_path = "C://Users//vlads//Desktop//BotPyWeather//20230616_193653.jpg"
    # with open(image_path, 'rb') as photo:
    #     await message.bot.send_photo(chat_id=message.chat.id, photo=photo, caption="Доброго часу, Вас вітає Бог.\nБудь ласка введіть місто в якому ви хочете дізнатися погоду:")
    await message.reply("Доброго часу, Вас вітає Бог.\nБудь ласка введіть місто в якому ви хочете дізнатися погоду:")



def kelToCel(fah):
    cel = fah - 273.15
    return round(cel)

def map_weather_type(weather_type):
    weather_mapping = {
        'clear sky': 'Чисте небо',
        'few clouds': 'Небагато хмар',
        'overcast clouds': 'хмарно затягнуте небо',
        'scattered clouds': 'Розсіяні хмари',
        'broken clouds': 'Розірвані хмари',
        'shower rain': 'Злива',
        'rain': 'Дощ',
        'light rain': 'невеликий дощ',
        'moderate rain': 'помірний дощ',
        'heavy intensity rain': 'сильний дощ',
        'very heavy rain': 'дуже сильний дощ',
        'extreme rain': 'сильний дощ',
        'freezing rain': 'крижаний дощ',
        'light intensity shower rain': 'дощ легкої інтенсивності',
        'heavy intensity shower rain': 'сильний зливовий дощ',
        'ragged shower rain': 'рваний душовий дощ',
        'snow': 'Сніг',
        'light snow': 'невеликий сніг',
        'heavy snow': 'сильний сніг',
        'sleet': 'мокрий сніг',
        'light shower sleet': 'легкий дощ зі снігом',
        'shower sleet': 'злава мокрий сніг',
        'light rain and snow': 'невеликий дощ зі снігом',
        'rain and snow': 'дощ і сніг',
        'light shower snow': 'дрібний сніг',
        'shower snow': 'снігопад',
        'heavy shower snow': 'сильний снігопад',
        'thunderstorm': 'Гроза',
        'thunderstorm with light rain': 'гроза з невеликим дощем',
        'thunderstorm with rain': 'гроза з дощем',
        'thunderstorm with heavy rain': 'гроза з сильним дощем',
        'light thunderstorm': 'легка гроза',
        'heavy thunderstorm': 'сильна гроза',
        'ragged thunderstorm': 'обірвана гроза',
        'thunderstorm with light drizzle': 'гроза з легким дощем',
        'thunderstorm with drizzle': 'гроза з дощем',
        'thunderstorm with heavy drizzle': 'гроза з сильним дощем',
        'mist': 'Туман',
        'smoke': 'дим',
        'haze': 'серпанок',
        'sand/dust whirls': 'завихрення піску/пилу',
        'fog': 'туман',
        'sand': 'пісок',
        'dust': 'пил',
        'volcanic ash': 'вулканічний попіл',
        'squalls': 'шквали',
        'tornado': 'торнадо',
        'light intensity drizzle': 'інтенсивність світла мряка',
        'drizzle': 'мряка',
        'heavy intensity drizzle': 'сильний дощ',
        'light intensity drizzle rain': 'мрячний дощ слабкої інтенсивності',
        'drizzle rain': 'мрячить дощ',
        'heavy intensity drizzle rain': 'сильна мряка',
        'shower rain and drizzle': 'мряка і дрібний дощ',
        'heavy shower rain and drizzle': 'сильний зливовий дощ та мряка',
        'shower drizzle': 'дощова мряка',
    }
    return weather_mapping.get(weather_type, 'Неизвестно')

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_text(message: types.Message):
    input_message = message.text.lower()  #сообщения от пользователя
    
    weatherInfo = {}
    url = f'http://api.openweathermap.org/data/2.5/find?q={input_message}&type=like&APPID={OpenweatherAPIKey}'
    res = requests.get(url)
    data = res.json()
    
    # user_id = message.from_user.id
    # user_first_name = message.from_user.first_name
    # user_last_name = message.from_user.last_name
    # user_username = message.from_user.username

    if data['count'] == 0:
        # with open(output_file, 'a') as file:
            # file.write(f"FAILD_MESSAGE: User ID: {user_id}, First Name: {user_first_name}, Last Name: {user_last_name}, Username: {user_username},text: {input_message}\n")
        await message.reply("Місто не знайдено. Будь ласка, введіть правильну назву міста.")
        return

    weatherInfo['Temperature'] = kelToCel(data['list'][0]['main']['temp'])
    weatherInfo['weather type'] = data['list'][0]['weather'][0]['description']

    translation_UA = map_weather_type(weatherInfo['weather type'])

    result_string = f"Температура: {weatherInfo['Temperature']} °C\nТип погоды: {translation_UA}"
    #result_string = f"Вы ввели: {input_message}"#test


    # with open(output_file, 'a') as file:
    #     file.write(f"User ID: {user_id}, First Name: {user_first_name}, Last Name: {user_last_name}, Username: {user_username},text: {input_message}\n")

    await message.reply(result_string)


# Запуск бота
if __name__ == '__main__':
    try:
        from aiogram import executor

        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        logging.exception(e)
        
