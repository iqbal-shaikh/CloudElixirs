import azure.cognitiveservices.speech as speechsdk
from azure.servicebus import QueueClient, Message
import configparser
import sys
from os import walk
import os, shutil

class SpeechToAzure:

    def __init__(self):
        
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        # Creates an instance of a speech config with  subscription key and service region.
        self.speech_config = speechsdk.SpeechConfig(subscription=self.config['speech_text']['speech_key']
                                               , region=self.config['speech_text']['service_region'])

        # Create the QueueClient
        conn_string = self.config['service_bus']['endpoint'] + ";" + \
                        self.config['service_bus']['accesskeyname'] + ";" + \
                        self.config['service_bus']['accesskey']
                        
        self.queue_client = QueueClient.from_connection_string(conn_string, self.config['service_bus']['msg_queue'])
        
    def speechtotext(self):                
        print("[Info] Cloud Elixir's Listening to you...")
        
        # Creates a recognizer with the given settings
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config)
        
        translated_text = self.recognizespeech(speech_recognizer)
                
        return translated_text
    
    def audiototext(self, audio_filename):        
        # Creates an audio configuration that points to an audio file.
        audio_input = speechsdk.AudioConfig(filename=audio_filename)
        
        # Creates a recognizer with the given settings
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_input)
        
        print("[Info] Prcoessing Audio to Text")
        translated_text = self.recognizespeech(speech_recognizer)
                
        return translated_text
    
    def getaudiofile(self):
        cwd = os.getcwd()
        filelist = os.path.join(cwd, "file_to_send")
        audiofile = []
        for (dirpath, dirnames, filenames) in walk(filelist):
            for file in filenames:
                currentfile = os.path.join(filelist, file)
                audiofile.append(currentfile)
                
        return audiofile
    
    def recognizespeech(self, speech_recognizer):
        # Starts speech recognition, and returns after a single utterance is recognized. The end of a
        # single utterance is determined by listening for silence at the end or until a maximum of 15
        # seconds of audio is processed.  The task returns the recognition text as result. 
        # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
        # shot recognition like command or query. 
        # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
        result = speech_recognizer.recognize_once()
        # Checks result.
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            translated_text = result.text
            print("Recognized: {}".format(translated_text))
        elif result.reason == speechsdk.ResultReason.NoMatch:
            translated_text = result.no_match_details
            print("No speech could be recognized: {}".format(translated_text))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            translated_text = cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                
        return translated_text
    
    def messagetoqueue(self, msg_bytes):        
        # Send a test message to the queue
        print("[Info] Publishing to Queue :", self.config['service_bus']['msg_queue'])
        msg = Message(msg_bytes)
        self.queue_client.send(msg)


def main(argv):
    if len(argv) != 2:
        print("[Error] Invalid Number Arguments", argv)
        print("[Info] Valid Arguments are 1.Recorded OR 2.RealTime")
        exit()
    if argv[1].lower() not in ("recorded", "realtime"):
        print("[Error] Valid Arguments are 1.Recorded OR 2.RealTime ")
        exit()
        
    stoa = SpeechToAzure()
    
    print("[Info] Speech to Text - Processing", argv[1], "Audio")
    
    if argv[1].lower() == "recorded":
        audiofile = stoa.getaudiofile()
        sendfile = os.path.join(os.getcwd(), "files_sent")
        for file in audiofile:
            translated_text = stoa.audiototext(file)
            msg_bytes = str.encode(translated_text)
            stoa.messagetoqueue(msg_bytes)
            shutil.move(file, sendfile)
            
    elif argv[1].lower() == "realtime":
        while True:
            translated_text = stoa.speechtotext()
            if translated_text.lower() == "end of demo.":
                print("[Cloud Elixir's] Demo Ends ")
                break
                
            msg_bytes = str.encode(translated_text)
            stoa.messagetoqueue(msg_bytes)
        
    
if __name__== "__main__":
    main(sys.argv)