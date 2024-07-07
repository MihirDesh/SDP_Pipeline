import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv
load_dotenv()
speech_config = speechsdk.SpeechConfig(subscription=os.getenv("speech_key"), region=os.getenv("speech_region"))
def from_mic():
        
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    print("listening")
    result = speech_recognizer.recognize_once_async().get()
    return result.text