from flask import Flask, render_template, session, redirect, url_for, request
from flask_session import Session
from tempfile import mkdtemp
import csv
import random
import json
import requests

#################################################################################################################

#add language variable and CSV filepath for English quotes
language = "English"
input_file = "static/words_english.csv"

#add language variable and CSV filepath for Telugu quotes
# language = "Telugu"
# input_file = "E:\ICS499\A3A4A5_sliderPuzzle\quotes_telugu.csv"

#add API path
request_path = "https://indic-wp.thisisjava.com/api/getLogicalChars.php"

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

@app.route('/')
def index():

    if "board" not in session:
        session["board"] = [[None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None]]

    if "score" not in session:
        session["score"] = [[None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None]]

    if "message" not in session:
        session["message"] = 'Make your first guess'

    return render_template("game.html", game=session["board"], score=session["score"], message=session["message"], status=status)


@app.route('/', methods=['POST'])
def play():

    global wordlist
    global word
    guess = request.form['guess'].lower()

    if guess != 'yes':

        global counter
        global status

        while status == True:

            while input_check(guess) == False:
                session["message"] = 'Oops. Make sure you are guessing a 5-letter word with no repeating letters.'
                return redirect(url_for("index"))

            #process guess
            for x in range(len(guess)):
                session["board"][counter][x] = guess[x]
                if guess[x] in word:
                    if x == word.index(guess[x]):
                        session["score"][counter][x] = 1
                    else:
                        session["score"][counter][x] = 2
                else:
                    session["score"][counter][x] = 5

            session["score"][counter].sort()

            if session["score"][counter] == [1,1,1,1,1]:
                session["message"] = 'Congratulations. You guessed the word!'
                status = False

            elif counter == 7:
                session["message"] = f'Sorry, you did not guess the word in the allowed number of tries. The answer is "{word}".'
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
                ###print(inMessage) # inId + " " + inMessage

                # process_message(inMessage, language)

    random.shuffle(wordlist)
    print(wordlist)
    print("done")
    return wordlist

def choose_word(wordlist, language):

    global word_index
    global word
    word = wordlist[word_index]
    word_index += 1

    params = {'string': word, 'language': language}
    response = requests.get(request_path, params,
                            headers={'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})
    # convert text response to json array
    json_array = json.loads(response.text[2:])
    print(json_array['data'])
    print(len(json_array['data']))
    if len(json_array['data']) != 5:
        choose_word(wordlist,language)
    else:
        word = "".join(json_array['data'])
        
    return word


#validate user input
def input_check(input):

    flag = True

    #check if input is all alphabet characters, is only 5 characters, and has no repeat characters
    if input.isalpha():
        if len(input) == 5:
            for char in input:
                if input.count(char) > 1:
                    flag = False
        else:
            flag = False
    else:
        flag = False

    return flag


def main():
    global word
    wordlist = create_wordlist()
    word = choose_word(wordlist,language)
    # if __name__ == "__main__":
    app.run( )


main()