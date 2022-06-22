from datetime import date

from flask import Flask, render_template, session, redirect, url_for, request
from flask_session.__init__  import Session
from tempfile import mkdtemp
import csv
import random
import json
import requests
import os.path
from datetime import timedelta

counter = 0
initial = True
status = True
in_play = False
word_index = 0
wordlist = []
word = ''
word_array = []
baseword_array = []
guess_array = []
used_words = []
custom_words = []
custom_message = ''
custom_check = False
c_id = ' '
custom_success_flag = False
end_game = False


#add language variable and CSV filepath for English quotes
language = "English"
# input_file = "static/words_english.csv"

#add language variable and CSV filepath for Telugu quotes
# language = "Telugu"
#input_file = "static/words_telugu.csv"

#choose initial word length
word_length = 5

#choose initial number of tries
num_tries = 8

#add get logical characters API path
request_path = "https://indic-wp.thisisjava.com/api/getLogicalChars.php"

#add get base characters API path
request_basecharpath = "https://indic-wp.thisisjava.com/api/getBaseCharacters.php"

#path to custom_words list
custom_words_path = "static/custom_words.csv"

#Icon for correct logical character in the correct position (1)
icon_one = "/static/elephant_1.png"

#Icon for correct logical character in the wrong position (2)
icon_two = "/static/fish_1.png"

#Icon for correct a base character in the correct position (3)
icon_three = "/static/horse_1.png"

#Icon for correct base character in the wrong position (4)
icon_four = "/static/frog_1.png"

#Icon for  character that does not appear in the word (5)
icon_five = "/static/mouse_1.png"