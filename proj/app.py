import requests
from flask import Flask, render_template, request

app = Flask(__name__)

API_KEY = 'mUYuUqUwyTGa5S7IKkRWBloPTzVpTCU0'

def get_location_key(city_name):
    location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city_name}"
    try:
        response = requests.get(location_url)
        response.raise_for_status()
        location_data = response.json()
        if location_data:
            return location_data[0]['Key']
    except requests.exceptions.HTTPError:
        return None
    except requests.exceptions.RequestException:
        return None

def check_bad_weather(temperature, wind_speed, precipitation_probability):
    if temperature < 0 or temperature > 35:
        return "Погода БЕ"
    if wind_speed > 50:
        return "Погода БЕ"
    if precipitation_probability > 70:
        return "Погода БЕ"
    return "Погода — кайфовая"

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/weather', methods=['POST'])
def get_weather():
    start_city = request.form['start']
    end_city = request.form['end']

    start_location_key = get_location_key(start_city)
    end_location_key = get_location_key(end_city)

    if not start_location_key:
        return render_template('form.html', error="Неверно введён город: " + start_city), 400
    if not end_location_key:
        return render_template('form.html', error="Неверно введён город: " + end_city), 400

    start_weather_url = f"http://dataservice.accuweather.com/currentconditions/v1/{start_location_key}?apikey={API_KEY}&language=ru-ru"
    end_weather_url = f"http://dataservice.accuweather.com/currentconditions/v1/{end_location_key}?apikey={API_KEY}&language=ru-ru"

    try:
        start_response = requests.get(start_weather_url)
        start_response.raise_for_status()
        end_response = requests.get(end_weather_url)
        end_response.raise_for_status()

        start_data = start_response.json()[0]
        end_data = end_response.json()[0]

        start_weather_info = {
            'temperature': start_data['Temperature']['Metric']['Value'],
            'wind_speed': start_data.get('Wind', {}).get('Speed', {}).get('Metric', {}).get('Value', 0),
            'precipitation_probability': start_data.get('PrecipitationProbability', 0),
            'humidity': start_data.get('RelativeHumidity', 0),
            'weather_text': start_data.get('WeatherText', 'Нет данных')
        }

        end_weather_info = {
            'temperature': end_data['Temperature']['Metric']['Value'],
            'wind_speed': end_data.get('Wind', {}).get('Speed', {}).get('Metric', {}).get('Value', 0),
            'precipitation_probability': end_data.get('PrecipitationProbability', 0),
            'humidity': end_data.get('RelativeHumidity', 0),
            'weather_text': end_data.get('WeatherText', 'Нет данных')
        }

        start_condition = check_bad_weather(float(start_weather_info['temperature']),
                                            float(start_weather_info['wind_speed']),
                                            float(start_weather_info['precipitation_probability']))

        end_condition = check_bad_weather(float(end_weather_info['temperature']),
                                           float(end_weather_info['wind_speed']),
                                           float(end_weather_info['precipitation_probability']))

        return render_template('results.html', start_city=start_city, end_city=end_city,
                               start_condition=start_condition, end_condition=end_condition,
                               start_weather_info=start_weather_info, end_weather_info=end_weather_info)
    except requests.exceptions.RequestException:
        return render_template('form.html', error="Ошибка попробуйте позже."), 500
    except Exception as e:
        return render_template('form.html', error=f"Ошибка: {str(e)}"), 500

if __name__ == '__main__':
    app.run(debug=True)
