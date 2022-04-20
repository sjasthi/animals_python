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

#################################################################################################################

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

################### Icon Configurations  ##########################

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

###################################################################

##################################################################################################################

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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

@app.route('/')
@app.route('/myword/<custom_id>')
#@app.route('/language/<lang>')
def index(custom_id=None, lang=None):
    global custom_check
    global c_id
    global custom_success_flag
    global initial
    global wordlist
    global word
    global language
    global word_length
    global word_array

    # if initial == True:
    #     wordlist = create_wordlist()
    #     word = choose_word(wordlist, language)
    #     word_length = len(word_array)
    #     initial = False


    if initial == True and custom_id != None:
        custom_check = True
        c_id = custom_id
        wordlist = create_wordlist()
        word = choose_word(wordlist, language)
        word_length = len(word_array)
        initial = False
    # else:
    #     c_id = ' '
    #     custom_check = False

    custom_success_flag = False

    print("custom check check: " + str(custom_check))
    print("status check: " + str(status))

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
        session["message"] = 'Make your first guess'

    return render_template("game.html", game=session["board"], score=session["score"], message=session["message"], status=status, in_play = in_play, initial = initial, end_game=end_game, custom_check = custom_check, num_tries=int(num_tries), word_length=word_length, language=language, icon_one=icon_one, icon_two=icon_two, icon_three=icon_three, icon_four=icon_four, icon_five=icon_five)



@app.route('/myword')
def custom_form():
    global custom_message
    global custom_success_flag

    # session["message"] = 'Enter a word with no repeating letters. '
    return render_template("myword.html", message = custom_message, custom_flag = custom_success_flag)

@app.route('/myword', methods=['POST'])
def custom_input():

    global language
    global word_length
    global custom_word
    global custom_message
    global custom_success_flag

    language = request.form['custom_lang']
    custom_word = request.form['custom_input']
    word_length = len(custom_word)


    while input_check(custom_word) == False:
        custom_message = 'Oops. Make sure your word contains no repeating letters.'
        return redirect(url_for("custom_form"))

    if not os.path.exists(custom_words_path):
        with open(custom_words_path, 'w', newline='') as wf:
            next_index = 1
            new_custom_entry = [next_index, language, custom_word, word_length]
            writer = csv.writer(wf)
            writer.writerow(new_custom_entry)
    else:
        with open(custom_words_path, 'r') as rcf:
            data = rcf.readlines()
            print(len(data))
            print ("checkpoint pre-last row")
            next_index = len(data) + 1

        with open(custom_words_path, 'a', newline='') as af:
            custom_entry = [next_index, language, custom_word, word_length]
            writer = csv.writer(af)
            writer.writerow(custom_entry)


    #custom_words.append([language, custom_word, word_length, num_tries])
    custom_success_flag = True
    #print(custom_words)
    #custom_message = "http://animals.pythonanywhere/myword/" + str(next_index)
    custom_message = "http://127.0.0.1:5000/myword/" + str(next_index)
    return redirect(url_for("custom_form"))

#validate user input
def input_check(input):

    flag = True
    global guess_array

    params = {'string': input, 'language': language}
    response = requests.get(request_path, params,
                            headers={'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})
    # convert text response to json array
    json_array = json.loads(response.text[2:])
    print("Guess array: ", json_array['data'])
    guess_array = json_array['data']
    print("Guess array length: ", len(json_array['data']))
    if len(json_array['data']) != word_length:
        flag = False
    else:
        for char in guess_array:
            print("character count: ", char, guess_array.count(char))
            if guess_array.count(char) > 1:
                flag = False

    return flag

@app.route('/', methods=['POST'])
@app.route('/myword/<custom_id>', methods=['POST'])
def play(custom_id = None):

    global num_tries
    global word_length
    global language
    global word_index
    global wordlist
    global word
    global word_array
    global baseword_array
    global guess_array
    global c_id
    global counter
    global status
    global in_play
    global custom_check
    global custom_message
    global custom_success_flag
    global initial
    global end_game

    custom_message = ''
    custom_success_flag = False

    if not wordlist:
        wordlist = create_wordlist()
        word = choose_word(wordlist, language)
        initial = False

    guess = request.form['guess'].lower()

    if guess != 'yes':

        global counter
        global status

        in_play = True

        while status == True:

            while input_check(guess) == False:
                session["message"] = 'Oops. Make sure you are guessing a word with no repeating letters.'
                return redirect(url_for("index"))

            #############get guess base chars####################
            if language =="Telugu":
                params = {'string': guess, 'language': language}
                response_basechars = requests.get(request_basecharpath, params,
                                              headers={
                                                  'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})

                # convert text response to json array
                json_guessbasechararray = json.loads(response_basechars.text[2:])
                print(json_guessbasechararray)
                print("json_guessbasechararray['data']: ", json_guessbasechararray['data'])
                guessbaseword_array = json_guessbasechararray['data']
                print("guess base array length: ", len(guessbaseword_array))
            #####################################################################

            #process guess
            for x in range(len(guess_array)):
                session["board"][counter][x] = guess_array[x]

                if guess_array[x] in word_array:
                    if x == word_array.index(guess_array[x]):
                        session["score"][counter][x] = 1
                    else:
                        session["score"][counter][x] = 2

                elif language == "Telugu" and guessbaseword_array[x] in baseword_array:
                    if x == baseword_array.index(guessbaseword_array[x]):
                        session["score"][counter][x] = 3
                    else:
                        session["score"][counter][x] = 4
                else:
                    session["score"][counter][x] = 5

            session["score"][counter].sort()

            if session["score"][counter].count(1)  == word_length :
                if c_id == ' ':
                    session["message"] = 'Congratulations. You guessed the word of the day!'
                else:
                    session["message"] = 'Congratulations. You guessed the word!'
                status = False
                c_id = ' '
                in_play = False
                end_game = True


            elif counter == num_tries - 1:
                session["message"] = f'Sorry, you did not guess the word in the allowed number of tries. The word was "{word}".'
                status = False
                c_id = ' '
                in_play = False
                end_game = True


            else:
                counter += 1
                session["message"] = 'Guess another word'

            return redirect(url_for("index"))
            # return render_template("game.html", game=session["board"], score=session["score"],
            #                        message=session["message"], status=status, custom_check=custom_check,
            #                        num_tries=int(num_tries), word_length=word_length, language=language,
            #                        icon_one=icon_one, icon_two=icon_two, icon_three=icon_three, icon_four=icon_four,
            #                        icon_five=icon_five)


    else:
        # if not custom_check:
            counter = 0
            word_index = 0
            status = True
            initial = True
            end_game = False
            session.clear()
            if custom_check:
                custom_check = False
                c_id = ' '
                word_index = 0
                wordlist.clear()
                # wordlist = create_wordlist()
                # word = choose_word(wordlist, language)
            if language != request.form['lang_toggle'] or word_length != request.form['c_length'] or num_tries != int(request.form['c_numattempts']):
                language = request.form['lang_toggle']
                word_length = int(request.form['c_length'])
                num_tries = int(request.form['c_numattempts'])
                word_index = 0
                wordlist.clear()
                # wordlist = create_wordlist()
                # word = choose_word(wordlist, language)
            else:
                wordlist.clear()
                # word = choose_word(wordlist, language)

            return redirect(url_for("index"))
            # return render_template("game.html", game=session["board"], score=session["score"],
            #                        message=session["message"], status=status, custom_check=custom_check,
            #                        num_tries=int(num_tries), word_length=word_length, language=language,
            #                        icon_one=icon_one, icon_two=icon_two, icon_three=icon_three, icon_four=icon_four,
            #                        icon_five=icon_five)

def create_wordlist():
    global wordlist
    global language
    global word_length

    if custom_check:

        with open(custom_words_path, 'r') as read_custom:
            rline = csv.reader(read_custom, delimiter =',')
            for row in rline:
                print(row)
                if int(row[0]) == int(c_id):
                    language = row[1]
                    wordlist.append(row[2])
                    word_length = int(row[3])
                    break

        print("After custom_check:")
        print("language: " + language)
        print("checkpoint after custom word added to wordlist")
        print(wordlist)
        print("word length: " + str(word_length))

    else:
        ###############To Be Implemented - Need to change name of csv files
        #input_file = "static/words_" + language + "_" + word_length + ".csv"
        #####temp
        input_file = "static/words_" + language.lower() + ".csv"

        if language == "Telugu":
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
    global used_words
    global custom_check
    global word_length
    word = wordlist[word_index]
    #word_index += 1

    params = {'string': word, 'language': language}
    response = requests.get(request_path, params,
                            headers={'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})
    # convert text response to json array
    json_array = json.loads(response.text[2:])
    print("json_array['data']: ", json_array['data'])
    word_array = json_array['data']
    print("array length: ", len(word_array))
    if language == "Telugu":
        response_basechars = requests.get(request_basecharpath, params,
                            headers={'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})


        # convert text response to json array
        json_basechararray = json.loads(response_basechars.text[2:])
        print(json_basechararray)
        print("json_basechararray['data']: ", json_basechararray['data'])
        baseword_array = json_basechararray['data']
        print("base array length: ", len(baseword_array))

    #if len(word_array) != word_length:
        #choose_word(wordlist,language)
    #else:
        word_length = len(word_array)
        word = "".join(word_array)
        #if not custom_check and word in used_words:
            #choose_word(wordlist, language)
        #else:
        #    if not custom_check:
        #        used_words.append(word)
        #        print("used words list: ", used_words)

    return word


#validate user input
def input_check(input):

    flag = True
    global guess_array

    params = {'string': input, 'language': language}
    response = requests.get(request_path, params,
                            headers={'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})
    # convert text response to json array
    json_array = json.loads(response.text[2:])
    print("Guess array: ", json_array['data'])
    guess_array = json_array['data']
    print("Guess array length: ", len(json_array['data']))
    if len(json_array['data']) != word_length:
        flag = False
    else:
        for char in guess_array:
            print("character count: ", char, guess_array.count(char))
            if guess_array.count(char) > 1:
                flag = False

    return flag

if __name__ == "__main__":
    app.run( )
