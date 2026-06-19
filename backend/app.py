import os
from flask import Flask, render_template, request, season
import requests

# Configure paths for templates and static folders
template_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates')
static_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = "change-this-to-a-secure-random-key"

API_KEY = "081a493e95fe0f17512e8feedb5044d7"


LANG_TEXT = {
    "en": {
        "title": "Farmer Weather Dashboard",
        "welcome": "Welcome Farmer!",
        "city": "Enter City",
        "button": "Get Weather"
    },
    # UI strings for English added below
    "te": {
        "title": "రైతు వాతావరణ డాష్‌బోర్డ్",
        "welcome": "రైతా! స్వాగతం!",
        "city": "నగరం నమోదు చేయండి",
        "button": "వాతావరణం చూడండి"
    },
    "hi": {
        "title": "किसान मौसम डैशबोर्ड",
        "welcome": "किसान आपका स्वागत है!",
        "city": "शहर दर्ज करें",
        "button": "मौसम देखें"
    }
}

# Extend LANG_TEXT with additional UI strings for each language
for k, v in LANG_TEXT.items():
    extra = {
        'crop_suggestions': {'en': 'Crop Suggestions', 'te': 'పంట సూచనలు', 'hi': 'फसल सुझाव'}[k] if k in ['en','te','hi'] else 'Crop Suggestions',
        'crop_advice_title': {'en': 'Crop Advice', 'te': 'పంట సలహా', 'hi': 'फसल सलाह'}[k] if k in ['en','te','hi'] else 'Crop Advice',
        'season_suggestions_title': {'en': 'Season Crop Suggestions', 'te': 'సెషన్ పంట సూచనలు', 'hi': 'सत्र फसल सुझाव'}[k] if k in ['en','te','hi'] else 'Season Crop Suggestions',
        'season_suggestions_desc': {'en': 'Based on your recent searches, these crops are most recommended:', 'te': 'మీ సమీప శోధనల ఆధారంగా, ఈ పంటలు ఎక్కువగా సూచించబడతాయి:', 'hi': 'आपकी हालिया खोजों के आधार पर, ये फसलें सबसे अधिक अनुशंसित हैं:'}[k] if k in ['en','te','hi'] else '',
        'recent_searches': {'en': 'Recent Searches', 'te': 'తాజా శోధనలు', 'hi': 'हाल की खोजें'}[k] if k in ['en','te','hi'] else 'Recent Searches',
        'suggested_label': {'en': 'Suggested:', 'te': 'సూచించబడింది:', 'hi': 'सुझाव:'}[k] if k in ['en','te','hi'] else 'Suggested:',
        'speak_button': {'en': 'Speak location, crop, season', 'te': 'నగరం, పంట, సెషన్ ఒక్క మాటలో చెప్పు', 'hi': 'स्थान, फसल, सत्र बोलें'}[k] if k in ['en','te','hi'] else 'Speak location, crop, season',
        'crop_placeholder': {'en': 'Enter crop name (e.g. Rice, Cotton, Corn, Pulses)', 'te': 'పంట పేరు రాయండి (ఉదా: అత్తి, పత్తి, మొక్కజొన్న)', 'hi': 'फसल का नाम दर्ज करें (जैसे: चावल, कपास, मकई, दालें)'}[k] if k in ['en','te','hi'] else 'Enter crop name',
        'season_placeholder': {'en': 'Ask if this crop is good for this season', 'te': 'ఈ సీజన్‌కు ఈ పంట బాగుందా అని అడగండి', 'hi': 'पूछें कि क्या यह फसल इस सत्र के लिए ठीक है'}[k] if k in ['en','te','hi'] else 'Ask if this crop is good for this season',
        'listening_prompt': {'en': 'Listening for location, crop, and season in one sentence.', 'te': 'ఒకే వాక్యంతో నగరం, పంట, సెషన్ చెప్తారా?', 'hi': 'एक वाक्य में स्थान, फसल और सत्र कहें।'}[k] if k in ['en','te','hi'] else 'Listening...',
        'confirm_capture': {'en': 'Captured. Location: {city}, Crop: {crop}. Submitting now.', 'te': 'సరే పట్టుకున్నాం — నగరం: {city}, పంట: {crop}. పంపిస్తున్నాం.', 'hi': 'कैप्चर किया गया। स्थान: {city}, फसल: {crop}. अब सबमिट कर रहे हैं।'}[k] if k in ['en','te','hi'] else 'Captured.',
        # Reason/explanation fragments
        'reason_temp': {'en': 'Temperature: {temp}°C.', 'te': 'తాపన: {temp}°C.', 'hi': 'तापमान: {temp}°C.'}[k] if k in ['en','te','hi'] else 'Temperature: {temp}°C.',
        'reason_humidity': {'en': 'Humidity: {humidity}%.', 'te': 'తేమ: {humidity}%.', 'hi': 'नमी: {humidity}%.'}[k] if k in ['en','te','hi'] else 'Humidity: {humidity}%.',
        'reason_condition': {'en': 'Weather: {condition}.', 'te': 'మౌసం: {condition}.', 'hi': 'मौसम: {condition}.'}[k] if k in ['en','te','hi'] else 'Weather: {condition}.',
        'reason_season_support': {'en': 'Season history also supports this crop.', 'te': 'మునుపటి సెషన్లు కూడా ఈ పంటకు సరిపోతున్నాయి.', 'hi': 'सत्र इतिहास भी इस फसल का समर्थन करता है.'}[k] if k in ['en','te','hi'] else 'Season history supports this crop.',
        'reason_not_supported': {'en': 'Current conditions do not strongly support {crop}.', 'te': 'ఇప్పటి పరిస్థితులు {crop}కి చాలు మద్దతు ఇవ్వవు.', 'hi': 'वर्तमान परिस्थितियाँ {crop} का मजबूत समर्थन नहीं करतीं.'}[k] if k in ['en','te','hi'] else 'Current conditions do not strongly support {crop}.',
        'reason_alternatives': {'en': 'Consider alternatives: {alternatives}.', 'te': 'ఇంటి చుట్టూ ఈ పంటలు చూడు: {alternatives}.', 'hi': 'विकल्पों पर विचार करें: {alternatives}.'}[k] if k in ['en','te','hi'] else 'Consider alternatives: {alternatives}.',
        'reason_no_weather': {'en': 'No weather data available to evaluate the crop.', 'te': 'వాతావరణ డేటా లభించలేదు; అంచనా వేయలేము.', 'hi': 'फसल का मूल्यांकन करने के लिए मौसम डेटा उपलब्ध नहीं है.'}[k] if k in ['en','te','hi'] else 'No weather data available.'
        ,
        'reason_label': {'en': 'Reason:', 'te': 'కారణం:', 'hi': 'कारण:'}[k] if k in ['en','te','hi'] else 'Reason:'
        ,
        'read_all_button': {'en': 'Read all inputs', 'te': 'అందరినీ చదవండి', 'hi': 'सभी इनपुट पढ़ें'}[k] if k in ['en','te','hi'] else 'Read all inputs',
        'read_summary_template': {
            'en': 'Summary — City: {city}. Crop: {crop}. Season: {season}.',
            'te': 'సారాంశం — నగరం: {city}. పంట: {crop}. సెషన్: {season}.',
            'hi': 'सारांश — शहर: {city}. फसल: {crop}. सत्र: {season}.'
        }[k] if k in ['en','te','hi'] else 'Summary — City: {city}. Crop: {crop}. Season: {season}.'
    }
    v.update(extra)


ADVICE_MESSAGES = {
    "en": {
        "yes_strong": "Yes — based on the current weather and season history, {crop} is a good choice for this season.",
        "yes_weather": "Yes — current weather supports {crop}.",
        "no_reason": "No — {crop} may not be suitable currently. Consider: {alternatives}.",
        "no_reason_simple": "No — {crop} may not be suitable currently due to weather conditions. Consider: {alternatives}."
    },
    "te": {
        "yes_strong": "అవును — వాతావరణం బాగుండటం, సెలవు-పేజీలు చూసినట్లే, {crop} ఈ సీజన్కి బాగుంది.",
        "yes_weather": "అవును — ప్రస్తుతం వాతావరణం {crop}కు అనుకూలంగా ఉంది.",
        "no_reason": "కాదు — ఇప్పుడిప్పుడు {crop} బాగాలే కాదు. బదులుగా అనుకున్నవి: {alternatives}.",
        "no_reason_simple": "కాదు — వాతావరణ పరిస్థితుల వల్ల {crop}కి సమయం సరిపోదు. ఇతర పంటలు చూడండి: {alternatives}."
    },
    "hi": {
        "yes_strong": "हाँ — वर्तमान मौसम और सत्र इतिहास के आधार पर, {crop} इस सत्र के लिए अच्छा विकल्प है।",
        "yes_weather": "हाँ — वर्तमान मौसम {crop} का समर्थन करता है।",
        "no_reason": "नहीं — वर्तमान में {crop} उपयुक्त नहीं हो सकता। विचार करें: {alternatives}।",
        "no_reason_simple": "नहीं — मौसम की स्थिति के कारण {crop} उपयुक्त नहीं है। विचार करें: {alternatives}।"
    }
}


@app.route("/", methods=["GET", "POST"])
def home():

    lang = request.args.get("lang", "en")
    text = LANG_TEXT.get(lang, LANG_TEXT["en"])

    weather = None
    season_suggestions = []
    history = season.get("history", [])
    city_input = None
    crop_advice = None
    crop_input = None
    season_input = None
    speech_text = None
    explanation_detail = None
    # overall_crops removed per user preference (not shown anymore)

    def suggest_crops(temp, humidity, condition):
        condition_text = condition.lower()
        crops = []

        if humidity >= 80 or "rain" in condition_text or "storm" in condition_text:
            crops.extend(["Rice", "Sugarcane", "Banana"])

        if temp >= 30:
            crops.extend(["Sorghum", "Pearl millet", "Cotton"])
        elif temp >= 25:
            crops.extend(["Maize", "Soybean", "Groundnut"])
        elif temp >= 18:
            crops.extend(["Wheat", "Barley", "Chickpea"])
        else:
            crops.extend(["Potato", "Spinach", "Carrot"])

        if humidity <= 40 and temp >= 28:
            crops.insert(0, "Millet")

        return list(dict.fromkeys(crops))[:4]

    def normalize_crop(name):
        if not name:
            return None
        normalized = name.strip().lower()
        if normalized == "corn":
            return "Corn"
        if normalized in ["pulse", "pulses"]:
            return "Pulses"
        return normalized.title()

    if request.method == "POST":
        city = request.form.get("city")
        city_input = city
        crop_input = request.form.get("crop", "").strip()
        season_input = request.form.get("season", "").strip()
        normalized_crop = normalize_crop(crop_input)
        season_use = bool(season_input and any(keyword in season_input.lower() for keyword in ["season", "yes", "use", "based", "recommend"]))

        if city:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()

            print(data)

            if data.get("main"):
                weather = {
                    "city": data["name"],
                    "temp": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "condition": data["weather"][0]["description"]
                }
                weather["crops"] = suggest_crops(weather["temp"], weather["humidity"], weather["condition"])

                history.insert(0, {
                    "city": weather["city"],
                    "temp": weather["temp"],
                    "humidity": weather["humidity"],
                    "condition": weather["condition"],
                    "crops": weather["crops"]
                })
                season["history"] = history[:5]

        if history:
            all_crops = [crop for entry in history for crop in entry["crops"]]
            season_suggestions = sorted(set(all_crops), key=lambda crop: all_crops.count(crop), reverse=True)[:4]

        if normalized_crop:
            msgs = ADVICE_MESSAGES.get(lang, ADVICE_MESSAGES['en'])
            alternatives = ', '.join(weather['crops']) if weather and weather.get('crops') else ''

            if weather and normalized_crop in weather["crops"]:
                # supported by weather
                if season_use and normalized_crop in season_suggestions:
                    crop_advice = msgs['yes_strong'].format(crop=normalized_crop)
                else:
                    crop_advice = msgs['yes_weather'].format(crop=normalized_crop)
            else:
                # not supported by weather
                if alternatives:
                    crop_advice = msgs['no_reason'].format(crop=normalized_crop, alternatives=alternatives)
                else:
                    crop_advice = msgs['no_reason_simple'].format(crop=normalized_crop, alternatives='other crops')

            # Build a localized explanation detail string
            parts = []
            if weather:
                parts.append(text['reason_temp'].format(temp=weather['temp']))
                parts.append(text['reason_humidity'].format(humidity=weather['humidity']))
                parts.append(text['reason_condition'].format(condition=weather['condition']))

                if weather and normalized_crop in weather.get('crops', []):
                    if season_use and normalized_crop in season_suggestions:
                        parts.append(text['reason_season_support'])
                else:
                    parts.insert(0, text['reason_not_supported'].format(crop=normalized_crop))
                    if alternatives:
                        parts.append(text['reason_alternatives'].format(alternatives=alternatives))
            else:
                parts.append(text['reason_no_weather'])

            explanation_detail = ' '.join(p for p in parts if p)

        if crop_advice:
            # localized speech text includes explanation
            if explanation_detail:
                speech_text = f"{crop_advice} {explanation_detail}"
            else:
                speech_text = crop_advice
    else:
        if history:
            all_crops = [crop for entry in history for crop in entry["crops"]]
            season_suggestions = sorted(set(all_crops), key=lambda crop: all_crops.count(crop), reverse=True)[:4]

    return render_template(
        "index.html",
        weather=weather,
        text=text,
        lang=lang,
        history=history,
        season_suggestions=season_suggestions,
        crop_advice=crop_advice,
        city_input=city_input,
        crop_input=crop_input,
        season_input=season_input,
        speech_text=speech_text,
    )


if __name__ == "__main__":
    app.run(debug=True)
