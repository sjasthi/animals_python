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

from helper import *


app = Flask(__name__)
app.secret_key = "#ICS499sp22andthecowjumpedoverthemoonD1dDl3dIDDlE"
app.permanent_session_lifetime = timedelta(minutes=20)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route('/login')
def start():
    if "board" not in session:
        session["board"] = []
        row_list = []
        for i in range(num_tries):
            for j in range(word_length):
                row_list.append(None)
            session["board"].append(row_list)
            row_list = []

    if "score" not in session:
        session["score"] = []
        row_list = []
        for i in range(num_tries):
            for j in range(word_length):
                row_list.append(None)
            session["score"].append(row_list)
            row_list = []

    return render_template("login.html", game=session["board"], score=session["score"], status=status, in_play = in_play, initial = initial, end_game=end_game, custom_check = custom_check, num_tries=int(num_tries), word_length=word_length, language=language, icon_one=icon_one, icon_two=icon_two, icon_three=icon_three, icon_four=icon_four, icon_five=icon_five)

@app.route('/login', methods=['POST'])
def login():
    if "user" not in session:
        session['user'] = request.form['user']
        session.pop("board", None)
        session.pop("score", None)
        return redirect(url_for("user"))

    else:
        return redirect(url_for("index"))

@app.route("/user")
def user():
    if "user" in session:
        session.permanent = True
        session['initial'] = True
        session['status'] = True
        session['in_play'] = False
        session['language'] = language
        session['end_game'] = False
        session['c_id'] = ' '
        session['custom_check'] = False
        session['counter'] = 0
        return redirect(url_for("index"))
    else:
        return redirect(url_for("start"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("board", None)
    session.pop("score", None)
    session.pop("message", None)
    session.pop('custom_check', None)
    session.pop('language', None)
    session.pop('c_id', None)
    session.pop('initial', None)
    session.pop('wordlist', None)
    session.pop('word', None)
    session.pop('word_length', None)
    session.pop('custom_success_flag', None)
    session.pop('custom_message', None)
    session.pop('status', None)
    session.pop('in_play', None)
    session.pop('end_game', None)
    session.pop('word_array', None)
    session.pop('guess', None)
    session.pop('guess_array', None)
    session.pop('guessbaseword_array', None)
    session.pop('counter', None)
    session.pop('baseword_array', None)
    return redirect(url_for("start"))


@app.route('/')
@app.route('/myword/<lang>/<custom_id>')
def index(custom_id=None, lang=None):
    # global custom_check
    # global c_id
    # global custom_success_flag
    # global initial
    global wordlist
    global word
    # global language
    global word_length
    global word_array

    if "user" not in session:
        return redirect(url_for("start"))



    if session['initial'] == True and custom_id != None:
        session.pop("board", None)
        session.pop("score", None)
        session.pop("message", None)
        session['custom_check'] = True
        session['language'] = lang
        session['c_id'] = custom_id
        # session['initial'] = False
        wordlist = create_wordlist()
        print("inital wordlist", wordlist)
        word = choose_word(wordlist, language)
        print("inital word", word)
        word_length = len(word_array)
        print("inital word_length", word_length)
        # session['num_tries'] = num_tries



    session['custom_success_flag'] = False
    session['custom_message'] = ''

    if "board" not in session:
        session["board"] = []
        row_list = []
        for i in range(num_tries):
            for j in range(word_length):
                row_list.append(None)
            session["board"].append(row_list)
            row_list = []

    if "score" not in session:
        session["score"] = []
        row_list = []
        for i in range(num_tries):
            for j in range(word_length):
                row_list.append(None)
            session["score"].append(row_list)
            row_list = []

    if "message" not in session:
        session["message"] = 'Welcome, ' + session['user'] + '!  Please make your first guess'

    return render_template("game.html", game=session["board"], score=session["score"], message=session["message"],
                           status=session['status'], in_play = session['in_play'], initial = session['initial'],
                           end_game=session['end_game'], custom_check = session['custom_check'],
                           num_tries=num_tries, word_length=word_length,
                           language=session['language'], icon_one=icon_one, icon_two=icon_two,
                           icon_three=icon_three, icon_four=icon_four, icon_five=icon_five)


@app.route('/myword')
def custom_form():
    global custom_message
    global custom_success_flag

    # session["message"] = 'Enter a word with no repeating letters. '
    return render_template("myword.html", message = session['custom_message'],
                           custom_flag = session['custom_success_flag'])

@app.route('/myword', methods=['POST'])
def custom_input():

    # global language
    global word_length
    global custom_word
    # global custom_message
    # global custom_success_flag

    cust_language = request.form['custom_lang']
    custom_word = request.form['custom_input']

    while custom_input_check(custom_word) == False:
        session['custom_message'] = 'Oops. Make sure you are guessing a {word_length}-letter word that contains no repeating letters.'
        return redirect(url_for("custom_form"))

    cust_wordpath = 'static/custom_words_' + cust_language
    if cust_language == 'Telugu':
        set_encoding = "utf-8"
    else:
        set_encoding = "ascii"

    if not os.path.exists(cust_wordpath):
        with open(cust_wordpath, mode='w', encoding = set_encoding, newline='') as wf:
            next_index = 1
            new_custom_entry = [next_index, cust_language, custom_word, word_length] ######eliminate lenght
            writer = csv.writer(wf)
            writer.writerow(new_custom_entry)
    else:
        with open(cust_wordpath, mode= 'r', encoding = set_encoding ) as rcf:
            data = rcf.readlines()
            print(len(data))
            print ("checkpoint pre-last row")
            next_index = len(data) + 1

        with open(cust_wordpath, mode = 'a', encoding = set_encoding, newline='') as af:
            custom_entry = [next_index, cust_language, custom_word, word_length] ######eliminate lenght
            writer = csv.writer(af)
            writer.writerow(custom_entry)

    session['custom_success_flag'] = True

    #session['custom_message'] = "http://animals.pythonanywhere/myword/" + str(next_index)
    session['custom_message'] = "http://127.0.0.1:5000/myword/" + cust_language + "/" + str(next_index)

    return redirect(url_for("custom_form"))


@app.route('/', methods=['POST'])
@app.route('/myword/<lang>/<custom_id>', methods=['POST'])
def play(lang = None, custom_id = None):

    global num_tries
    global word_length
    global word_index
    global wordlist
    global word
    global word_array
    global baseword_array
    global guess_array

    session['initial'] = False
    session['custom_message'] = ''
    session['custom_success_flag'] = False

    if not wordlist:
        print("if not wordlist checkpoint")
        wordlist = create_wordlist()
        word = choose_word(wordlist, session['language'])


    print("checkpoint 1 word: ", word)
    word_array = get_wordarray(word)
    guess = request.form['guess'].lower()

    if guess != 'yes':

        global counter
        global status

        session['in_play'] = True

        while session['status'] == True:

            while input_check(guess) == False:
                session["message"] = 'Oops. Make sure you are guessing a word with no repeating letters.'
                return redirect(url_for("index"))

            guess_array = get_wordarray(guess)

            if session['language'] =="Telugu":
                guessbaseword_array = get_basearray(guess)

            #process guess
            for x in range(len(guess_array)):
                session["board"][session['counter']][x] = guess_array[x]

                if guess_array[x] in word_array:
                    if x == word_array.index(guess_array[x]):
                        session["score"][session['counter']][x] = 1
                    else:
                        session["score"][session['counter']][x] = 2

                elif session['language'] == "Telugu" and guessbaseword_array[x] in baseword_array:
                    if x == baseword_array.index(guessbaseword_array[x]):
                        session["score"][session['counter']][x] = 3
                    else:
                        session["score"][session['counter']][x] = 4
                else:
                    session["score"][session['counter']][x] = 5

            session["score"][session['counter']].sort()

            if session["score"][session['counter']].count(1)  == word_length :
                if session['c_id'] == ' ':
                    session["message"] = 'Congratulations. You guessed the word of the day!'
                else:
                    session["message"] = 'Congratulations. You guessed the word!'
                session['status'] = False
                session['c_id'] = ' '
                session['in_play'] = False
                session['end_game'] = True


            elif session['counter'] == num_tries - 1:
                session["message"] = f'Sorry, you did not guess the word in the allowed number of tries. The word was "{word}".'
                session['status'] = False
                session['c_id'] = ' '
                session['in_play'] = False
                session['end_game'] = True

            else:
                session['counter'] += 1
                session["message"] = 'Guess another word'

            return redirect(url_for("index"))

    else:
        session['counter'] = 0
        word_index = 0
        session['status'] = True
        session['initial'] = True
        session['end_game'] = False
        session.pop('board', None)
        session.pop('score', None)
        session.pop('message', None)
        if session['custom_check']:
            session['custom_check'] = False
            session['c_id'] = ' '
            word_index = 0
            wordlist.clear()
            word = ''

        if session['language'] != request.form['lang_toggle'] or word_length != request.form['c_length'] or num_tries != int(request.form['c_numattempts']):
            session['language'] = request.form['lang_toggle']
            if session['language'] == 'English':
                word_length = 5;
            else:
                word_length = 4;
            # word_length = int(request.form['c_length'])
            num_tries = int(request.form['c_numattempts'])
            word_index = 0
            wordlist.clear()


        else:
            wordlist.clear()


        return redirect(url_for("index"))


def create_wordlist():
    global wordlist
    # global language
    global word_length
    wordlist = []

    if session['custom_check']:

        cust_wordpath = 'static/custom_words_' + session['language']
        if session['language'] == 'Telugu':
            set_encoding = "utf-8"
        else:
            set_encoding = "ascii"

        with open(cust_wordpath, mode='r', encoding=set_encoding) as read_custom:
            rline = csv.reader(read_custom, delimiter =',')
            for row in rline:
                print(row)
                if int(row[0]) == int(session['c_id']):
                    session['language'] = row[1]
                    wordlist.append(row[2])
                    word_length = int(row[3])
                    break

        print("After custom_check:")
        print("language: ", session['language'])
        print("checkpoint after custom word added to wordlist")
        print(wordlist)
        print("word length: " + str(word_length))

    else:

        #####temp
        input_file = "static/words_" + session['language'].lower() + ".csv"

        if session['language'] == "Telugu":
            #open input file
            with open(input_file, 'r', encoding='utf-8') as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')

                #read each row in CSV file and store values in variables
                for row in readCSV:
                    if row[0] == date.today().isoformat():
                        print("Today is: " + date.today().isoformat())
                        wordlist.append(row[1])

        else:
            #open input file
            with open(input_file, 'r') as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')

                #read each row in CSV file and store values in variables
                for row in readCSV:
                    if row[0] == date.today().isoformat():
                        print("Today is: " + date.today().isoformat())
                        wordlist.append(row[1])

        #random.shuffle(wordlist)
        print("Wordlist: ", wordlist)

    return wordlist


def choose_word(wordlist, language):

    global word_index
    global word
    global word_array
    global baseword_array
    # global used_words
    # global custom_check
    global word_length

    word = wordlist[0]
    word_array = get_wordarray(word)
    session['word_array'] = word_array
    word_length = len(word_array)

    if session['language'] == "Telugu":
        baseword_array = get_basearray(word)
        session['base_array'] = baseword_array
        print("basearray LLLLL")
        print(baseword_array)
        word_length = len(word_array)
        word = "".join(word_array)
    return word


#validate user input
def input_check(input):

    flag = True
    global guess_array

    guess_array = get_wordarray(input)

    if len(guess_array) != word_length:
        flag = False
    else:
        for char in guess_array:
            print("character count: ", char, guess_array.count(char))
            if guess_array.count(char) > 1:
                flag = False

    return flag


if __name__ == "__main__":
    app.run( )
