import wave, os, math, sys, random, string, re
from pydub import AudioSegment
from pydub.playback import play

from flask import Flask, Response, jsonify, request, send_file
from flask_cors import CORS
import base64
import urllib.parse

TEMP_FILE_NAME = "temp.wav"
letter_graphs = [# add symbols you want unique sounds for here, add the symbol.wav to the letter foler
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
    "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
    "w", "x", "y", "z", 
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" 
]

digraphs = [
    "ch", "sh", "ph", "th", "wh"
]

bebebese = "bebebese_slow"

def build_sentence(sentence):
    sentence_wav = AudioSegment.empty()
    sentence = sentence.lower()
    sentence = replace_swear_words(sentence)
    sentence = replace_parentheses(sentence)
    i = 0
    while (i < len(sentence)):
        char = None
        if (i < len(sentence)-1) and ((sentence[i] + sentence[i+1]) in digraphs):
            char = sentence[i] + sentence[i+1]
            i+=1
        elif sentence[i] in letter_graphs:
            char = sentence[i]
        elif sentence[i] in string.punctuation:
            char = bebebese
        i+=1

        if char != None:
            new_segment = AudioSegment.from_wav("letters/sans.wav".format(char))
            sentence_wav += new_segment

    return sentence_wav

def replace_swear_words(sentence):
    swear_words = ["fuck", "shit", "piss", "crap", "bugger"]
    for word in swear_words:
        sentence = sentence.replace(word, "*"*len(word))
    return sentence
    

def replace_parentheses(sentence):
    while "(" in sentence or ")" in sentence:
        start = sentence.index("(")
        end = sentence.index(")")
        sentence = sentence[:start] + "*"*(end-start) + sentence[end+1:]

    return sentence

def change_playback_speed(sound, speed_change):
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed_change)
    })
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

from pydub.effects import speedup
def change_playback_speed_not_pitch(sound, speed_change):
    return speedup(sound, speed_change) 


def build_and_say_sentence(sentence):
    sound = build_sentence(sentence)
    sound = change_playback_speed(sound, random.uniform(1.75,2.5))
    play(sound)
    return sound

def build_and_say_sentence_with_voice(sentence, voice):
    sound = build_sentence(sentence)
    sound = change_playback_speed(sound, voice)
    #play(sound) #dont play because sending over api
    return sound

#if len(sys.argv) > 1:
    #sentence = sys.argv[1]
#else:
    #sentence = "Tommy nook his fuckie wook!"
#pitch_shift = 2
#sound = build_and_say_sentence_with_voice(sentence, pitch_shift)
#sound.export("output.wav", format="wav")

OUTPUT_FILE = "audio/output/output.wav"
app = Flask(__name__)
CORS(app, supports_credentials=True)



@app.route('/synthesize/', defaults={'text': 'testingHere'})
@app.route('/synthesize/<path:text>')
def synthesize(text):
    line = urllib.parse.unquote(request.url[request.url.find('synthesize/?')+12:])

    pitch_shift = 1
    sound = build_and_say_sentence_with_voice(line, pitch_shift)
    sound.export(OUTPUT_FILE, format="wav")
    enc = base64.b64encode(open(OUTPUT_FILE, "rb").read())
    return(enc) 

if __name__ == "__main__":
    PORT = 8124
    app.run(host="127.0.0.1", port=8124)
