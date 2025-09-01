import tkinter as tk
from tkinter import ttk, messagebox
import requests
from io import BytesIO
from PIL import Image, ImageTk
import datetime

API_KEY = "a1878f1669852018bcb82dae37b52d2a"
def kelvin_to_celsius(k):
    return k - 273.15

def c_to_f(c):
    return c * 9/5 + 32

def get_coordinates(city_name):
    """Use OpenWeatherMap Geocoding API to get lat, lon for a city"""
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {"q": city_name, "limit": 1, "appid": API_KEY}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError("City not found")
    return data[0]["lat"], data[0]["lon"], data[0].get("name", city_name), data[0].get("country", "")

def fetch_current_weather(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": API_KEY}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def fetch_forecast(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"lat": lat, "lon": lon, "appid": API_KEY}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_icon_image(icon_code):
    try:
        url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        img_data = resp.content
        image = Image.open(BytesIO(img_data)).resize((100, 100), Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)
    except Exception:
        return None

class WeatherApp:
    def __init__(self, root):
        self.root = root
        root.title("Weather App")
        root.geometry("520x520")
        root.resizable(False, False)

        self.unit = tk.StringVar(value="C")

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill="x")

        ttk.Label(frame, text="City:").pack(side="left")
        self.city_entry = ttk.Entry(frame, width=30)
        self.city_entry.pack(side="left", padx=5)
        self.city_entry.insert(0, "Kolkata") 

        search_btn = ttk.Button(frame, text="Search", command=self.search_weather)
        search_btn.pack(side="left", padx=5)

        ttk.Label(frame, text="Unit:").pack(side="left", padx=(10,0))
        ttk.Radiobutton(frame, text="°C", variable=self.unit, value="C", command=self.update_ui_units).pack(side="left")
        ttk.Radiobutton(frame, text="°F", variable=self.unit, value="F", command=self.update_ui_units).pack(side="left")

        self.display = ttk.Frame(root, padding=10)
        self.display.pack(fill="both", expand=True)

        self.city_label = ttk.Label(self.display, text="", font=("Segoe UI", 16, "bold"))
        self.city_label.pack()

        self.icon_label = ttk.Label(self.display)
        self.icon_label.pack()

        self.temp_label = ttk.Label(self.display, text="", font=("Segoe UI", 14))
        self.temp_label.pack()

        self.desc_label = ttk.Label(self.display, text="", font=("Segoe UI", 12))
        self.desc_label.pack()

        self.details_label = ttk.Label(self.display, text="", font=("Segoe UI", 10))
        self.details_label.pack()

        ttk.Separator(self.display, orient="horizontal").pack(fill="x", pady=8)

        self.forecast_frame = ttk.Frame(self.display)
        self.forecast_frame.pack(fill="x", pady=5)

        self.forecast_cards = []
        for i in range(3):
            card = ttk.Frame(self.forecast_frame, borderwidth=1, relief="groove", padding=6)
            card.grid(row=0, column=i, padx=6, sticky="n")
            lbl_date = ttk.Label(card, text="Date", font=("Segoe UI", 10, "bold"))
            lbl_date.pack()
            lbl_icon = ttk.Label(card)
            lbl_icon.pack()
            lbl_temp = ttk.Label(card, text="—", font=("Segoe UI", 10))
            lbl_temp.pack()
            lbl_desc = ttk.Label(card, text="", font=("Segoe UI", 9))
            lbl_desc.pack()
            self.forecast_cards.append((lbl_date, lbl_icon, lbl_temp, lbl_desc))

        ttk.Button(root, text="Clear", command=self.clear).pack(pady=(6,10))

        self._icon_image = None
        self._forecast_images = [None]*3

    def clear(self):
        self.city_label.config(text="")
        self.icon_label.config(image="")
        self.temp_label.config(text="")
        self.desc_label.config(text="")
        self.details_label.config(text="")
        for t,i,l,d in self.forecast_cards:
            t.config(text="")
            i.config(image="")
            l.config(text="")
            d.config(text="")

    def update_ui_units(self):
        cur = self.city_entry.get().strip()
        if cur:
            self.search_weather()

    def search_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input needed", "Please enter a city name.")
            return

        try:
            lat, lon, name, country = get_coordinates(city)
        except Exception as e:
            messagebox.showerror("Error", f"Could not find city: {e}")
            return

        try:
            current = fetch_current_weather(lat, lon)
            forecast = fetch_forecast(lat, lon)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch weather data: {e}")
            return

        temp_k = current["main"]["temp"]
        temp_c = kelvin_to_celsius(temp_k)
        if self.unit.get() == "C":
            temp_text = f"{temp_c:.1f} °C"
        else:
            temp_text = f"{c_to_f(temp_c):.1f} °F"

        desc = current["weather"][0]["description"].capitalize()
        humidity = current["main"].get("humidity", "N/A")
        wind = current.get("wind", {}).get("speed", "N/A")
        icon_code = current["weather"][0].get("icon", "")

        self.city_label.config(text=f"{name}, {country}")
        self.temp_label.config(text=f"Temperature: {temp_text}")
        self.desc_label.config(text=desc)
        self.details_label.config(text=f"Humidity: {humidity}%    Wind: {wind} m/s")

        icon_img = get_icon_image(icon_code)
        if icon_img:
            self._icon_image = icon_img
            self.icon_label.config(image=self._icon_image)
        else:
            self.icon_label.config(image="")

        forecast_map = {}
        for item in forecast.get("list", []):
            dt = datetime.datetime.fromtimestamp(item["dt"])
            day = dt.date()
            target_hour = 12
            score = abs(dt.hour - target_hour)
            if day not in forecast_map or score < forecast_map[day][0]:
                forecast_map[day] = (score, item)

        days = sorted(forecast_map.keys())
        today = datetime.date.today()
        future_days = [d for d in days if d > today][:3]

        for idx in range(3):
            if idx < len(future_days):
                d = future_days[idx]
                item = forecast_map[d][1]
                dt_txt = d.strftime("%a %d")
                icon_code = item["weather"][0].get("icon", "")
                temp_k = item["main"]["temp"]
                temp_c = kelvin_to_celsius(temp_k)
                if self.unit.get() == "C":
                    temp_text = f"{temp_c:.1f} °C"
                else:
                    temp_text = f"{c_to_f(temp_c):.1f} °F"
                desc = item["weather"][0]["description"].capitalize()
                icon_img = get_icon_image(icon_code)
                self._forecast_images[idx] = icon_img

                lbl_date, lbl_icon, lbl_temp, lbl_desc = self.forecast_cards[idx]
                lbl_date.config(text=dt_txt)
                if icon_img:
                    lbl_icon.config(image=icon_img)
                else:
                    lbl_icon.config(image="")
                lbl_temp.config(text=temp_text)
                lbl_desc.config(text=desc)
            else:
                lbl_date, lbl_icon, lbl_temp, lbl_desc = self.forecast_cards[idx]
                lbl_date.config(text="")
                lbl_icon.config(image="")
                lbl_temp.config(text="")
                lbl_desc.config(text="")


def main():
    if API_KEY == "YOUR_API_KEY_HERE":
        print("Please put your OpenWeatherMap API key in the API_KEY variable in the script.")
        return
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
