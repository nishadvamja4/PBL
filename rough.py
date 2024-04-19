import argparse
import os
import subprocess
import pyttsx3
import datetime
import random
import wikipedia
import pywhatkit
import webbrowser
import json
import pyjokes
import time
import requests
from google.auth.transport import grpc

from google.auth.transport import grpc
from google.assistant.embedded.v1alpha2 import (
    embedded_assistant_pb2,
    embedded_assistant_pb2_grpc
)
from google.oauth2.credentials import Credentials

# Initialize the text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Function to speak out the given text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to recognize user speech using Google Assistant SDK
def listen():
    credentials = Credentials.from_authorized_user_file(args.credentials)
    with open(args.model, 'rb') as f:
        model = f.read()

    assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(
        grpc.secure_channel('embeddedassistant.googleapis.com:443', credentials))
    config = embedded_assistant_pb2.AssistConfig(
        audio_in_config=embedded_assistant_pb2.AudioInConfig(
            encoding='LINEAR16',
            sample_rate_hertz=16000,
        ),
        audio_out_config=embedded_assistant_pb2.AudioOutConfig(
            encoding='LINEAR16',
            sample_rate_hertz=16000,
            volume_percentage=100,
        ),
        device_config=embedded_assistant_pb2.DeviceConfig(
            device_id=args.device_id,
            device_model_id=args.device_model_id,
        )
    )

    for resp in assistant.Assist(config):
        if resp.event_type == embedded_assistant_pb2.AssistRespEventType.END_OF_UTTERANCE:
            print('End of audio request detected')
        if resp.speech_results:
            for result in resp.speech_results:
                print('Transcript of user request:', result.transcript)
                return result.transcript.lower()

# Function to get weather information
def get_weather(city):
    api_key = 'your_api_key'  # Replace 'your_api_key' with your actual API key
    url = f'https://api.weatherapi.com/v1/current.json?key={api_key}&q={city}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        if 'error' in weather_data:
            return "Sorry, I couldn't retrieve weather information for that location."
        else:
            temperature_c = weather_data['current']['temp_c']
            condition = weather_data['current']['condition']['text']
            return f"The current temperature in {city} is {temperature_c} degrees Celsius with {condition}."
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return "Sorry, I couldn't retrieve weather information at the moment."

# Function to process user commands
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
            response = requests.get(url, params=params, timeout=10)  # Set timeout for API request
            response.raise_for_status()  # Raise exception for HTTP errors
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
                    # Send the message via WhatsApp
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
    elif 'weather' in command:
        city = 'Vadodara'  # You can change this to your desired city
        weather_info = get_weather(city)
        speak(weather_info)
    else:
        speak("I'm sorry, I don't understand that command.")         


# Main function to handle voice assistant functionality
def main():
    speak("Hello! I'm your voice assistant FRIDAY. How can I assist you today?")
    while True:
        command = listen()
        if not command:
            print("No command detected. Please try again.")
            continue
        
        process_command(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '--credentials', type=str, default=os.path.join(
            os.path.expanduser('~'), '.config',
            'google-oauthlib-tool', 'credentials.json'),
        help='Path to the file containing the OAuth2.0 credentials.')
    parser.add_argument(
        '--device-model-id',
        required=True,
        help='Unique device model identifier, '
             'if not specifed, it is read from --device-config.')
    parser.add_argument(
        '--device-id',
        required=True,
        help='Unique registered device instance identifier, '
             'if not specified, it is read from --device-config.')
    parser.add_argument(
        '--model', type=str, default=os.path.join(
            os.path.dirname(__file__), 'data',
            'googlesamples-assistant', 'device_config.json'),
        help='Path to the file containing the device configurations.')
    args = parser.parse_args()
    main()