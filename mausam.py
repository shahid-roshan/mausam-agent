from google import genai
from google.genai import types
import json
import urllib.request
import urllib.parse
import os
import time
from datetime import datetime

client = genai.Client(api_key="YOUR_GEMINI_API_KEY")
hidayat = "Tum ek Weather & Day-Planning Assistant Agent ho. Tumhe user ke sheher ka asal mausam data diya jayega (temperature aur barish ka chance) jo tools se aya hai. Sirf usi data ki bunyad pe asaan Roman Urdu mein chhota sa practical mashwara do: garm kapre ya jacket pehenna hai ya nahi, chhata (umbrella) lena hai ya nahi, aur bahir nikalna ya safar munasib hai ya nahi. Agar hawa ki quality ka AQI number bhi diya gaya ho to us pe bhi mashwara do: AQI kam ho to hawa saaf hai; AQI 150 se zyada ho to bahir sair kam karne aur mask pehenne ka mashwara do. Agar kal aur parso ke mausam ka data bhi diya gaya ho to din ke plan mein us ka zikr bhi kar do. Agar suraj nikalne aur doobne ka waqt bhi diya gaya ho to bahir ke kaam ya sair ka waqt tay karne mein us ka zikr bhi kar do. Mausam ka koi number khud mat banao, sirf diya gaya data istemal karo. Jawab zyada se zyada 4 lines ka ho."
sahi_hidayat = "User Pakistan se hai. Wo kisi jagah (sheher, town ya mashhoor ilaqa/valley) ka naam likhta hai — spelling ghalat bhi ho sakti hai. Apne ilm se pehchano ke wo sab se zyada kis jagah ki baat kar raha hai, aur us jagah ki bilkul pakki jankari do jo mausam maloom karne ke kaam aye. Jawab SIRF is format mein ek hi line mein do, is ke ilawa ek lafz bhi nahi: NAAM | MULK | LAT | LON. Jahan NAAM wo jagah ka mashhoor English naam hai, MULK us mulk ka English naam hai, LAT us ki latitude hai aur LON us ki longitude hai (decimal numbers). Misal: Murree | Pakistan | 33.9084 | 73.3903. Agar tumhe us jagah ki pakki jankari nahi hai to sirf NONE likho."

if os.path.exists("sheher.txt"):
    f = open("sheher.txt", "r")
    mera_sheher = f.read().strip()
    f.close()
else:
    mera_sheher = ""

while True:
    print()
    print("=== Mausam Agent ===")
    if mera_sheher != "":
        print("Apka yad kia hua sheher: " + mera_sheher + " hai")
    city = input("Ap kis jgah ki mosam malom krna chaty ha (English mein likho), apne sheher ke liye sirf mera sheher likho, rukne ke liye band likho: ")
    if city.strip() == "":
        print("Ap ne koi jgah nahi likhi. Pehle jgah ka naam likho.")
        continue
    if city.strip().lower() == "band":
        print("Allah Hafiz")
        break
    if city.strip().lower() == "mera sheher":
        if mera_sheher == "":
            print("Ap ne abhi tak koi sheher yad nahi kia. Pehle kisi sheher ka mausam dekho, phir me use yad kar lu ga.")
            continue
        city = mera_sheher

    try:
        guess = client.models.generate_content(model="gemini-3.5-flash-lite", contents="User ne ye naam likha hai: " + city + ". Is jagah ki pakki jankari do.", config=types.GenerateContentConfig(system_instruction=sahi_hidayat))
    except:
        print("Abhi model jawab nahi de saka. Thodi dair baad dobara koshish karo.")
        print("Or kya m apki madad kr skta hu? Koi or sawal h apka?")
        continue
    guess_text = guess.text.strip()
    if guess_text == "NONE" or "|" not in guess_text:
        print("Ye jgah meri maloomat mein nahi mili.")
        print("Or kya m apki madad kr skta hu? Koi or sawal h apka?")
        continue
    parts = guess_text.split("|")
    name = parts[0].strip()
    country = parts[1].strip()
    lat = float(parts[2].strip())
    lon = float(parts[3].strip())
    if name.lower() != city.strip().lower():
        print("Ap ne jo naam likha, lagta hai ap " + name + " ki baat kar rhy hain. Us jgah ka mausam ye hai:")

    print("Jgah mili: " + name + ", " + country)
    weather_link = "https://api.open-meteo.com/v1/forecast?latitude=" + str(lat) + "&longitude=" + str(lon) + "&current=temperature_2m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset&timezone=auto&forecast_days=3"
    weather_data = None
    koshish = 0
    while koshish < 3:
        try:
            weather_data = json.loads(urllib.request.urlopen(weather_link).read())
            break
        except:
            koshish = koshish + 1
            print("Mausam lene mein rukawat ai, dobara koshish kar raha hoon... (" + str(koshish) + "/3)")
            time.sleep(2)
    if weather_data is None:
        print("Abhi mausam nahi mil saka. Thodi dair baad dobara koshish karo.")
        print("Or kya m apki madad kr skta hu? Koi or sawal h apka?")
        continue
    temp = weather_data["current"]["temperature_2m"]
    rain_chance = weather_data["daily"]["precipitation_probability_max"][0]
    print("Abhi ka temperature: " + str(temp) + " C")
    print("Aaj barish ka chance: " + str(rain_chance) + " %")
    dates = weather_data["daily"]["time"]
    max_list = weather_data["daily"]["temperature_2m_max"]
    min_list = weather_data["daily"]["temperature_2m_min"]
    rain_list = weather_data["daily"]["precipitation_probability_max"]
    print("Kal (" + dates[1] + "): zyada se zyada " + str(max_list[1]) + " C, kam se kam " + str(min_list[1]) + " C, barish " + str(rain_list[1]) + " %")
    print("Parso (" + dates[2] + "): zyada se zyada " + str(max_list[2]) + " C, kam se kam " + str(min_list[2]) + " C, barish " + str(rain_list[2]) + " %")
    sunrise_list = weather_data["daily"]["sunrise"]
    sunset_list = weather_data["daily"]["sunset"]
    suraj_nikalna = sunrise_list[0].split("T")[1]
    suraj_doobna = sunset_list[0].split("T")[1]
    print("Aaj suraj nikalne ka waqt: " + suraj_nikalna)
    print("Aaj suraj doobne ka waqt: " + suraj_doobna)

    aqi = None
    air_link = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=" + str(lat) + "&longitude=" + str(lon) + "&current=us_aqi&timezone=auto"
    try:
        air_data = json.loads(urllib.request.urlopen(air_link).read())
        aqi = air_data["current"]["us_aqi"]
    except:
        aqi = None
    if aqi is not None:
        print("Hawa ki quality (AQI): " + str(aqi))
    else:
        print("Hawa ki quality abhi nahi mil saki.")

    data_text = "Jgah: " + name + ", " + country + ". Abhi ka temperature: " + str(temp) + " C. Aaj barish ka chance: " + str(rain_chance) + "% hai."
    if aqi is not None:
        data_text = data_text + " Hawa ki quality ka AQI number: " + str(aqi) + " hai."
    data_text = data_text + " Kal zyada se zyada " + str(max_list[1]) + " C, kam se kam " + str(min_list[1]) + " C, barish " + str(rain_list[1]) + "% hai. Parso zyada se zyada " + str(max_list[2]) + " C, kam se kam " + str(min_list[2]) + " C, barish " + str(rain_list[2]) + "% hai."
    data_text = data_text + " Aaj suraj " + suraj_nikalna + " pe nikalta hai aur " + suraj_doobna + " pe doobta hai."
    data_text = data_text + " Is data ki bunyad pe din ka mashwara do."
    try:
        jawab = client.models.generate_content(model="gemini-3.5-flash-lite", contents=data_text, config=types.GenerateContentConfig(system_instruction=hidayat))
        print("Agent ka mashwara: " + jawab.text)
    except:
        print("Mausam mil gaya hai, lekin mashwara abhi nahi mil saka.")

    if name != mera_sheher:
        mera_sheher = name
        f = open("sheher.txt", "w")
        f.write(mera_sheher)
        f.close()
        print("Note: " + mera_sheher + " apka sheher yad kar lia hai.")

    log_line = str(datetime.now()) + " | " + name + ", " + country + " | " + str(temp) + " C | barish " + str(rain_chance) + "%"
    if aqi is not None:
        log_line = log_line + " | AQI " + str(aqi)
    log_f = open("log.txt", "a")
    log_f.write(log_line + "\n")
    log_f.close()

    print("Or kya m apki madad kr skta hu? Koi or sawal h apka?")
