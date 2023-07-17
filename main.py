import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests
from apikey import *
from dictionaries import *
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta

# Установка уровня логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=f'{TelebotAPIKey}')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

output_file = 'E://BotPyWeather//WeatherTelegramPython//output.txt'

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    # image_path = "C://Users//vlads//Desktop//BotPyWeather//20230616_193653.jpg"
    # with open(image_path, 'rb') as photo:
    #     await message.bot.send_photo(chat_id=message.chat.id, photo=photo, caption="Доброго часу, Вас вітає Бог.\nБудь ласка введіть місто в якому ви хочете дізнатися погоду:")
    await message.reply("Good afternoon, God is in you.\nPlease сhoose a language:", reply_markup=types.InlineKeyboardMarkup(
                            inline_keyboard=[
                                [types.InlineKeyboardButton(text="English", callback_data="lang_en")],
                                [types.InlineKeyboardButton(text="Українська", callback_data="lang_ua")],
                                [types.InlineKeyboardButton(text="Deutsche", callback_data="lang_de")],
                                [types.InlineKeyboardButton(text="російська", callback_data="lang_ru")]
                            ]
                        ))


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("lang_"))
async def handle_language(callback_query: types.CallbackQuery, state: FSMContext):
    language = callback_query.data.replace("lang_", "")
    await state.update_data(language=language)
    await state.finish()
    reply_text = dictionaries[language]['SayWriteCity']
    select_text = dictionaries[language]['SelectLanguage']
    await callback_query.answer(f"{select_text} {language.upper()}")
    await callback_query.message.reply(reply_text)
    await state.update_data(language=language)


def kelToCel(fah):
    cel = fah - 273.15
    return round(cel)

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_text(message: types.Message, state: FSMContext):
    
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    state_data = await state.get_data()
    language = state_data.get('language')
    if not language:    # Если значение language не установлено
        await message.reply("Language not selected. Please select a language.", reply_markup=types.InlineKeyboardMarkup(
                                inline_keyboard=[
                                    [types.InlineKeyboardButton(text="English", callback_data="lang_en")],
                                    [types.InlineKeyboardButton(text="Українська", callback_data="lang_ua")],
                                    [types.InlineKeyboardButton(text="Deutsche", callback_data="lang_de")],
                                    [types.InlineKeyboardButton(text="російська", callback_data="lang_ru")]
                                ]
                            ))
        return

    input_message = message.text.lower()  #сообщения от пользователя

    await state.update_data(input_message=input_message)

    weatherInfo = {}
    url = f'http://api.openweathermap.org/data/2.5/find?q={input_message}&type=like&APPID={OpenweatherAPIKey}'
    res = requests.get(url)
    data = res.json()
    
    user_id = message.from_user.id
    user_first_name = message.from_user.first_name
    user_last_name = message.from_user.last_name
    user_username = message.from_user.username

    if data['count'] == 0:
        with open(output_file, 'a', encoding="utf-8") as file:
            file.write(f"[{formatted_datetime}] FAILD_MESSAGE: User ID: {user_id}, First Name: {user_first_name}, Last Name: {user_last_name}, Username: {user_username},text: {input_message}\n")
        await message.reply("Місто не знайдено. Будь ласка, введіть правильну назву міста.")
        return

    weatherInfo['Temperature'] = kelToCel(data['list'][0]['main']['temp'])
    weatherInfo['weather type'] = data['list'][0]['weather'][0]['description']


    weather_type = dictionaries[language][weatherInfo['weather type']]
    weather_type_name = dictionaries[language]['WeatherTypeName']
    Temperature = dictionaries[language]['Temperature']

    result_string = f"{Temperature} {weatherInfo['Temperature']} °C\n{weather_type_name} {weather_type}"
    #result_string = f"Вы ввели: {input_message}"#test
    WeatherFullDay = dictionaries[language]['WeatherFullDay']
    WeatherTomorrow = dictionaries[language]['WeatherTomorrow']
    WeatherFullWeek = dictionaries[language]['WeatherFullWeek']
    await state.update_data(WeatherFullWeek=WeatherFullWeek,WeatherFullDay=WeatherFullDay,WeatherTomorrow=WeatherTomorrow,Temperature=Temperature,weather_type_name=weather_type_name)
    

    reply_markup = types.InlineKeyboardMarkup(row_width=2)
    reply_markup.add(
        types.InlineKeyboardButton(text=f"{WeatherFullDay}", callback_data="weather_full_day"),
        types.InlineKeyboardButton(text=f"{WeatherTomorrow}", callback_data="weather_full_day_tomorrow"),
        types.InlineKeyboardButton(text=f"{WeatherFullWeek}", callback_data="weather_full_week")
    )

    with open(output_file, 'a', encoding="utf-8") as file:
        file.write(f"[{formatted_datetime}] User ID: {user_id}, First Name: {user_first_name}, Last Name: {user_last_name}, Username: {user_username}, Text: {input_message}\n")

    await message.reply(result_string, reply_markup=reply_markup)

@dp.callback_query_handler(lambda query: query.data == "weather_full_day")
async def handle_weather_full_day(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message  # Получаем объект сообщения из callback_query
    state_data = await state.get_data()
    language = state_data.get('language')
    input_message = state_data.get('input_message')
    Temperature = state_data.get('Temperature')
    WeatherTypeName = state_data.get('weather_type_name')
    WeatherFullDay = dictionaries[language]['WeatherFullDay']


    url = f'http://api.openweathermap.org/data/2.5/forecast?q={input_message}&APPID={OpenweatherAPIKey}'

    res = requests.get(url)
    data = res.json()



    forecast_list = data['list']
    weather_message = f"{WeatherFullDay}: \n\n"

    for forecast in forecast_list:
        date = forecast['dt_txt']  # Дата и время прогноза

        forecast_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()
        current_date = datetime.now().date()


        if forecast_date == current_date:
            temperature = kelToCel(forecast['main']['temp'])  # Температура
            weather_type = dictionaries[language][forecast['weather'][0]['description']]

            weather_message += f"{dictionaries[language]['date and time']} {date}\n"
            weather_message += f"{Temperature} {temperature} °C\n"
            weather_message += f"{WeatherTypeName} {weather_type}\n\n"

    # Отправляем сообщение с прогнозом погоды
    await message.answer(weather_message)
    await callback_query.answer()  # Ответить на запрос

@dp.callback_query_handler(lambda query: query.data == "weather_full_day_tomorrow")
async def handle_weather_full_day(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message  # Получаем объект сообщения из callback_query
    state_data = await state.get_data()
    language = state_data.get('language')
    input_message = state_data.get('input_message')
    Temperature = state_data.get('Temperature')
    WeatherTypeName = state_data.get('weather_type_name')
    WeatherTomorrow = state_data.get('WeatherTomorrow')

    url = f'http://api.openweathermap.org/data/2.5/forecast?q={input_message}&APPID={OpenweatherAPIKey}'

    res = requests.get(url)
    data = res.json()

    forecast_list = data['list']
    weather_message = f"{WeatherTomorrow}: \n\n"

    current_date = datetime.now().date()
    next_day = current_date + timedelta(days=1)

    for forecast in forecast_list:
        date = forecast['dt_txt']  # Дата и время прогноза

        forecast_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()

        if forecast_date == next_day:
            temperature = kelToCel(forecast['main']['temp'])  # Температура
            weather_type = dictionaries[language][forecast['weather'][0]['description']]

            weather_message += f"{dictionaries[language]['date and time']} {date}\n"
            weather_message += f"{Temperature} {temperature} °C\n"
            weather_message += f"{WeatherTypeName} {weather_type}\n\n"

    # Отправляем сообщение с прогнозом погоды
    await message.answer(weather_message)
    await callback_query.answer()  # Ответить на запрос

@dp.callback_query_handler(lambda query: query.data == "weather_full_week")
async def handle_weather_full_week(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message  # Получаем объект сообщения из callback_query
    state_data = await state.get_data()
    language = state_data.get('language')
    input_message = state_data.get('input_message')
    Temperature = state_data.get('Temperature')
    WeatherTypeName = state_data.get('weather_type_name')
    WeatherFullWeek = state_data.get('WeatherFullWeek')
    

    url = f'http://api.openweathermap.org/data/2.5/forecast?q={input_message}&cnt=40&APPID={OpenweatherAPIKey}'

    res = requests.get(url)
    data = res.json()

    forecast_list = data['list']
    weather_message = f"{WeatherFullWeek}\n\n"

    current_date = datetime.now().date()
    end_date = current_date + timedelta(days=7)

    for forecast in forecast_list:
        date = forecast['dt_txt']  # Дата и время прогноза
        forecast_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()

        if current_date <= forecast_date <= end_date:
            temperature = kelToCel(forecast['main']['temp'])  # Температура
            weather_type = dictionaries[language][forecast['weather'][0]['description']]

            weather_message += f"{dictionaries[language]['date and time']} {date}\n"
            weather_message += f"{Temperature} {temperature} °C\n"
            weather_message += f"{WeatherTypeName} {weather_type}\n\n"

    # Отправляем сообщение с прогнозом погоды на неделю
    await message.answer(weather_message)
    await callback_query.answer()  # Ответить на запрос

# Запуск бота
if __name__ == '__main__':
    try:
        from aiogram import executor

        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        logging.exception(e)
        
