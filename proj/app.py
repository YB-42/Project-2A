import requests
from flask import Flask, render_template
import json


app = Flask(__name__)

API_KEY = 'kbrOdBHB6pAkYDfKWHr9LOHhqctcFGmX'
lat = '55.669986'
lon = '37.773143'

location_url = f"http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={API_KEY}&q={lat},{lon}"
location_response = requests.get(location_url)

if location_response.status_code == 200:
    location_data = location_response.json()
    LOCATION_KEY = location_data['Key']
else:
    print(f"Ошибка при получении ключа местоположения: {location_response.status_code}")
    LOCATION_KEY = None  # Установите в None, если не удалось получить ключ


def check_bad_weather(temperature, wind_speed, precipitation_probability):
    """
    Функция для оценки погодных условий.

    :param temperature: Температура в градусах Цельсия
    :param wind_speed: Скорость ветра в км/ч
    :param precipitation_probability: Вероятность осадков в процентах
    :return: Строка "Плохие погодные условия" или "Хорошие погодные условия"
    """
    if temperature < 0 or temperature > 35:
        return "Плохие погодные условия"
    if wind_speed > 50:
        return "Плохие погодные условия"
    if precipitation_probability > 70:
        return "Плохие погодные условия"

    return "Хорошие погодные условия"


@app.route('/')
def home():
    return "Добро пожаловать в приложение погоды!"


@app.route('/weather')
def get_weather():
    if LOCATION_KEY is None:
        return "Не удалось получить ключ местоположения", 500

    url = f"http://dataservice.accuweather.com/currentconditions/v1/{LOCATION_KEY}?apikey={API_KEY}&language=ru-ru"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:  # Проверяем, что данные не пустые
            weather_info = {
                'temperature': data[0]['Temperature']['Metric']['Value'],
                'humidity': data[0].get('RelativeHumidity', 'Нет данных'),
                'wind_speed': data[0].get('Wind', {}).get('Speed', {}).get('Metric', {}).get('Value', 'Нет данных'),
                'precipitation_probability': data[0].get('PrecipitationProbability', 'Нет данных')
            }

            # Преобразуем значения в нужный формат
            temperature = float(weather_info['temperature'])
            wind_speed = float(weather_info['wind_speed']) if weather_info['wind_speed'] != 'Нет данных' else 0
            precipitation_probability = float(weather_info['precipitation_probability']) if weather_info[
                                                                                                'precipitation_probability'] != 'Нет данных' else 0

            # Проверяем погодные условия
            weather_condition = check_bad_weather(temperature, wind_speed, precipitation_probability)

            # Возвращаем данные в HTML-шаблон
            return render_template('weather.html', weather_info=weather_info, weather_condition=weather_condition)
        else:
            return "Нет данных о погоде", 404
    else:
        return "Не удалось получить данные о погоде", response.status_code


if __name__ == '__main__':
    app.run(debug=True)