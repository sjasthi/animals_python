from flask import Flask, render_template, session, redirect, url_for, request
from flask_session import Session
from tempfile import mkdtemp
import csv
import random
import json
import requests

#################################################################################################################

#add language variable and CSV filepath for English quotes
# language = "English"
# input_file = "static/words_english.csv"

#add language variable and CSV filepath for Telugu quotes
language = "Telugu"
input_file = "static/words_telugu.csv"

#choose word length
word_length = 4

#choose number of tries
num_tries = 4

#add get logical characters API path
request_path = "https://indic-wp.thisisjava.com/api/getLogicalChars.php"

#add get base characters API path
request_basecharpath = "https://indic-wp.thisisjava.com/api/getBaseCharacters.php"

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
status = True
word_index = 0
wordlist = []
word = ''
word_array = []
baseword_array = []
guess_array = []
used_words = []



@app.route('/')
def index():

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

    return render_template("game.html", game=session["board"], score=session["score"], message=session["message"], status=status, num_tries=num_tries, word_length=word_length, language=language, icon_one=icon_one, icon_two=icon_two, icon_three=icon_three, icon_four=icon_four, icon_five=icon_five)


@app.route('/', methods=['POST'])
def play():

    global wordlist
    global word
    global word_array
    global baseword_array
    global guess_array
    guess = request.form['guess'].lower()

    if guess != 'yes':

        global counter
        global status

        while status == True:

            while input_check(guess) == False:
                session["message"] = 'Oops. Make sure you are guessing a word with no repeating letters.'
                return redirect(url_for("index"))

            #############get guess base chars####################
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

                elif guessbaseword_array[x] in baseword_array:
                    if x == baseword_array.index(guessbaseword_array[x]):
                        session["score"][counter][x] = 3
                    else:
                        session["score"][counter][x] = 4
                else:
                    session["score"][counter][x] = 5

            session["score"][counter].sort()

            if session["score"][counter].count(1)  == word_length :
                session["message"] = 'Congratulations. You guessed the word!'
                status = False

            elif counter == num_tries - 1:
                session["message"] = f'Sorry, you did not guess the word in the allowed number of tries. The word was "{word}".'
                status = False

            else:
                counter += 1
                session["message"] = 'Guess another word'

            return redirect(url_for("index"))

    else:
        counter = 0
        status = True
        session.clear()
        word = choose_word(wordlist, language)
        print(word)
        return redirect(url_for("index"))


def create_wordlist():

    global wordlist

    if (language == "Telugu"):
        #open input file
        with open(input_file, 'r', encoding='utf-8') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')

            #read each row in CSV file and store values in variables
            for row in readCSV:
                wordlist.append(row[1])

    else:
        #open input file
        with open(input_file) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')

            #read each row in CSV file and store values in variables
            for row in readCSV:
                wordlist.append(row[1])

    random.shuffle(wordlist)
    print("Wordlist: ", wordlist)

    return wordlist


def choose_word(wordlist, language):

    global word_index
    global word
    global word_array
    global baseword_array
    global used_words
    word = wordlist[word_index]
    word_index += 1

    params = {'string': word, 'language': language}
    response = requests.get(request_path, params,
                            headers={'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})
    # convert text response to json array
    json_array = json.loads(response.text[2:])
    print("json_array['data']: ", json_array['data'])

    response_basechars = requests.get(request_basecharpath, params,
                            headers={'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})


    # convert text response to json array
    json_basechararray = json.loads(response_basechars.text[2:])
    print(json_basechararray)
    print("json_basechararray['data']: ", json_basechararray['data'])

    word_array = json_array['data']
    baseword_array = json_basechararray['data']
    print("array length: ", len(word_array))
    print("base array length: ", len(baseword_array))

    if len(word_array) != word_length:
        choose_word(wordlist,language)
    else:
        word = "".join(word_array)
        if word in used_words:
            choose_word(wordlist, language)
        else:
            used_words.append(word)
            print("used words list: ", used_words)
        
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


def main():
    global word
    wordlist = create_wordlist()
    word = choose_word(wordlist,language)
    # if __name__ == "__main__":
    app.run( )


main()