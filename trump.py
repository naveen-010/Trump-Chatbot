import replicate
import requests
import os
import time
from openai import OpenAI
from pydub import AudioSegment
import threading
from pydub.playback import play
import sys
import httpx
import speech_recognition as sr
import subprocess

# The terminal command you want to run
command = "jp2a trump.jpg --colors --chars='01'"
USER = os.environ.get('USER')
# Run the command
try:
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(result.stdout)  # Output of the command
except subprocess.CalledProcessError as e:
    print(f"Error: {e.stderr}")  # Print any error if the command fails



with open(os.devnull, 'w') as f:
    sys.stdout = f
    import pygame
    sys.stdout = sys.__stdout__  # Restore default stdout

replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))
#  client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"), transport=httpx.AsyncHTTPTransport(verify=False))

def record_audio(file_path, duration=5):
    subprocess.run(["arecord", "-D", "hw:0,0", "-f", "cd", "-t", "wav", "-d", str(duration), file_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
##############################################################################################################################
#  GET THESE MERGED
def transcribe_audio(file_path):
    audio = AudioSegment.from_wav(file_path)
    audio.export("temp.wav", format="wav")  

    recognizer = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)  
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError:
            return "Could not request results from the speech recognition service."
def stt():
    while True:
        #  n = len([f for f in os.listdir('Temporary_files') if f.startswith(USER)]) + 1
        n = len(os.listdir('Temporary_files')) + 1
        file_path = f"Temporary_files/{n}.wav"  
        record_audio(file_path)

        text = transcribe_audio(file_path)
        print(text)
        choice = input("Do you want to Record/Type the message again? [(R)ecord, (T)ype, (N)o]: ")
        print('\033[F','\r', ' '*70, '\r',  flush = True,sep = '', end = '') # to clear input line

        if choice.lower() == 'n':
            return text
        elif choice.lower() == 't':
            text = input("Enter your reply:")
            print('\033[F',"\r\033[K", '\r',  "\n\033[38;5;85mYou: \033[0m", text, flush = True,sep = '')
            return text
        elif choice.lower() == 'r':
            print('\033[F',"\r\033[K", '\r',  flush = True,sep = '', end = '') # to clear text line (previou YOU: line)
            print("\n\033[38;5;85mYou: \033[0m",end = '')
##############################################################################################################################

def print_text_slowly(text, audio_duration):
    words = text.split()
    time_per_word = audio_duration / len(words) 

    for word in words:
        print(word, end=' ', flush=True) 
        time.sleep(time_per_word) 

def play_audio(file):
    pygame.mixer.init()  
    pygame.mixer.music.load(file)  
    pygame.mixer.music.play()  


def playtts(text):


    refaudio = open('trump_speech.mkv' , 'rb') #trump
    #  refaudio = open('/home/zoe/Downloads/replicate-prediction-sp0dk1aj1nrj20cjhe1sn2pzqr.wav', 'rb') #default girl voice on replicate
    #  refaudio = open('/home/zoe/Downloads/myvoicenonoise.wav', 'rb') #my voice

    output = replicate.run(
        "x-lance/f5-tts:87faf6dd7a692dd82043f662e76369cab126a2cf1937e25a9d41e0b834fd230e",
        input={
            "speed": 1,
            "gen_text": text,
            #  "ref_text": "captain teemo, on duty!",
            "ref_text": "Before I even arrive at the oval office, I will have the disastrous war between Russia and Ukraine settled.",
            #  "ref_text" : "Hello, I am the president of USA, Do you understand that?",
            "ref_audio": refaudio,
        }
    )
    response = requests.get(output)
    if response.status_code == 200:

        n = len([f for f in os.listdir('Temporary_files') if f.startswith('Trump')]) + 1

        with open(f"Temporary_files/Trump {n}.wav", "wb") as f:
            f.write(response.content)
        audio = AudioSegment.from_file(f"Temporary_files/Trump {n}.wav")
        audio_duration = len(audio)/1000
        play_audio(f"Temporary_files/Trump {n}.wav")
        print_text_slowly(text, audio_duration)
        print()
        print()
       
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

conversation_history = [
    {"role": "system", "content": "You are Trump. Roast the user brutally, NO MERCY , in under 40-50 words."}
]

def get_completion(new_message):
    conversation_history.append({"role": "user", "content": new_message})

    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=conversation_history)

    assistant_response = response.choices[0].message.content

    conversation_history.append({"role": "assistant", "content": assistant_response})

    return assistant_response

u = 'a'
while u != 'q':
    #  u = input("\033[38;5;85mYou: \033[0m")
    print("\033[38;5;85mYou: \033[0m", end = ' ', flush = True)
    u = stt()
    print('\033[38;5;85mTrump: \033[0m', end = '', flush = True)
    out = get_completion(u)
    playtts(out)

