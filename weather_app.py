import requests

def get_weather(city_name, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric'
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        
        print(f"Weather in {city_name}:")
        print(f"Temperature: {temp} °C")
        print(f"Humidity: {humidity}%")
        print(f"Condition: {description.capitalize()}")
    else:
        print("Sorry, I couldn't find that city.")

def main():
    api_key = "a1878f1669852018bcb82dae37b52d2a"
    city = input("Enter city name: ")
    get_weather(city, api_key)

if __name__ == "__main__":
    main()
