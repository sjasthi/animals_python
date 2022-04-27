from config import *


def get_wordarray(input):
        params = {'string': input, 'language': language}
        response = requests.get(request_path, params,
                                headers={'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})
        # convert text response to json array
        json_array = json.loads(response.text[2:])
        print("Guess array: ", json_array['data'])
        guess_array = json_array['data']
        return guess_array


def get_basearray(guess):
    params = {'string': guess, 'language': "Telugu"}
    response_basechars = requests.get(request_basecharpath, params,
                                      headers={
                                          'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})

    # convert text response to json array
    json_guessbasechararray = json.loads(response_basechars.text[2:])
    print(json_guessbasechararray)
    print("json_guessbasechararray['data']: ", json_guessbasechararray['data'])
    base_array = json_guessbasechararray['data']
    print("guess base array length: ", len(base_array))
    return base_array

# validate user custom input
def custom_input_check(input):
    # flag = True
    global guess_array
    global word_length

    guess_array = get_wordarray(input)
    session['guess_array'] = guess_array
    word_length = len(guess_array)
    print("Word length: ", word_length)
    print("Guess array length: ", len(guess_array))

    flag = check_for_duplicate_letters(guess_array)

    return flag


def check_for_duplicate_letters(guess_array):
        flag = True
        for char in guess_array:
                print("character count: ", char, guess_array.count(char))
                if guess_array.count(char) > 1:
                        flag = False

        return flag
