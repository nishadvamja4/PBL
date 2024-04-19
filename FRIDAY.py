import requests
import pyttsx3
import speech_recognition as sr
import datetime
import random
import wikipedia
import pywhatkit
import webbrowser
import json
import time


engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)


def speak(text):
    engine.say(text)
    engine.runAndWait()


def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  
        audio = recognizer.listen(source, timeout=10)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
        return query.lower()
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand. Please try again.")
    except sr.RequestError as e:
        print(f"Speech recognition request failed: {e}")
    return None


def process_command(command):
    if 'friday' in command or 'hey friday' in command:
        responses = ["Hello! How can I assist you today?",
                     "Hi there! How can I help you?",
                     "Hey! What can I do for you?"]
        speak(random.choice(responses))
    elif 'time' in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
    elif 'date' in command:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")
    elif 'thank' in command:
        speak("You're welcome!")
    elif 'exit' in command:
        speak("Goodbye!")
        exit()
    elif 'wikipedia' in command:
        query = command.replace('wikipedia', '')
        try:
            result = wikipedia.summary(query, sentences=5)
            speak(f"According to Wikipedia, {result}")
        except wikipedia.exceptions.WikipediaException as e:
            print(f"Wikipedia search error: {e}")
            speak("Sorry, I couldn't find any information on that topic.")
    elif 'open youtube' in command:
        query = command.replace('open youtube', '')
        pywhatkit.playonyt(query)
    elif 'search on google' in command:
        query = command.replace('search on google', '')
        webbrowser.open(f"https://www.google.com/search?q={query}")
    elif 'news' in command:
        try:
            url = 'https://newsapi.org/v2/top-headlines'
            params = {'country': 'in', 'apiKey': 'df76f1f9b4f544fa954c9bc53d70b1ff'}
            response = requests.get(url, params=params, timeout=10) 
            response.raise_for_status()  
            news = response.json()
            speak("Here are the top headlines:")
            for headline in news['articles'][:5]:
                speak(headline['title'])
        except Exception as e:
            print(f"Error fetching news: {e}")
            speak("Sorry, I couldn't retrieve the latest news at the moment.")
    elif 'joke' in command:
        joke = pyjokes.get_joke()
        speak(joke)
    elif 'advice' in command:
        try:
            response = requests.get("https://api.adviceslip.com/advice", timeout=10)  
            response.raise_for_status() 
            advice = json.loads(response.text)['slip']['advice']
            speak(f"Here's a random advice for you: {advice}")
        except Exception as e:
            print(f"Error fetching advice: {e}")
            speak("Sorry, I couldn't retrieve an advice at the moment.") 
            
    elif 'open whatsapp' in command:
        speak("Sure, what message would you like to send?")
        message = listen()
        if message:
            speak("Please specify the recipient's phone number.")
            recipient_number = listen()
            if recipient_number:
                try:
                    pywhatkit.sendwhatmsg(f"+{recipient_number}", message, 
                                          datetime.datetime.now().hour, 
                                          datetime.datetime.now().minute + 1)
                    speak("Message sent successfully!")
                except Exception as e:
                    print(f"Error sending message: {e}")
                    speak("Sorry, there was an error sending the message.")
            else:
                speak("Sorry, I couldn't hear the recipient's phone number.")
        else:
            speak("Sorry, I couldn't hear the message.")
    else:
        speak("I'm sorry, I don't understand that command.") 

        
                

def get_weather(city):
    api_key = '8e8beb72f77b4c0b8929730f71551b8f'
    url = f'https://api.weatherbit.io/v2.0/current?city={city}&key={api_key}'
    response = requests.get(url, timeout=10)  
    response.raise_for_status()  
    weather_data = response.json()
    if 'data' in weather_data:
        temperature = weather_data['data'][0]['temp']
        weather_description = weather_data['data'][0]['weather']['description']
        return f"The current temperature in {city} is {temperature} degrees Celsius with {weather_description}."
    else:
        return "Sorry, I couldn't retrieve weather information at the moment."

def main():
    speak("Hello! I'm your voice assistant FRIDAY. How can I assist you today?")
    while True:
        command = listen()
        if not command:
            print("No command detected. Please try again.")
            continue
        
        if 'weather' in command:
            try:
                city = 'Ahmedabad'
                weather_info = get_weather(city)
                speak(weather_info)
            except Exception as e:
                print(f"Error fetching weather: {e}")
                speak("Sorry, I couldn't retrieve weather information at the moment.")
        else:
            process_command(command)

if __name__ == "__main__":
    main()