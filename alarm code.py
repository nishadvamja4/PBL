import pyttsx3
import speech_recognition as sr
import datetime
import time
import os

# Initialize the text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Function to speak out the given text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to recognize user speech
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Reduce duration for faster response
        audio = recognizer.listen(source, timeout=5)

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

# Function to set alarm
def set_alarm():
    try:
        speak("Please specify the time for the alarm in 12-hour format, for example, 7:30 AM or 7:30 PM.")
        alarm_time_str = listen()
        if "a.m." in alarm_time_str:
            alarm_time_str = alarm_time_str.replace("a.m.", "AM")
        elif "p.m." in alarm_time_str:
            alarm_time_str = alarm_time_str.replace("p.m.", "PM")
        alarm_time = datetime.datetime.strptime(alarm_time_str, "%I:%M %p")
        now = datetime.datetime.now()
        alarm_datetime = datetime.datetime.combine(now.date(), alarm_time.time())
        if alarm_datetime <= now:
            alarm_datetime += datetime.timedelta(days=1)
        delta = alarm_datetime - now
        alarm_seconds = delta.total_seconds()
        # Set wait time to 5 minutes before the alarm
        wait_time = max(alarm_seconds - 300, 1)  # Ensure wait_time is not negative
        time.sleep(wait_time)
        speak("Alarm activated!")
        os.system("start alarm.wav")  # Replace 'alarm.wav' with the path to your alarm sound file
    except Exception as e:
        print(f"Error setting alarm: {e}")
        speak("Sorry, there was an error setting the alarm.")

def main():
    set_alarm()

if __name__ == "__main__":
    main()
