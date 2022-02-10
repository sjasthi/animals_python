#!/usr/bin/python
# program name: Bulls And Cows Game
# your name: Justin Wilmot
# class: ICS 499
# date: 2022

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

#Bulls and Cows Game function
def bulls_and_cows():

    #temporary input word to guess
    code = 'share'

    #display program ready for guesses
    print('Okay.  A 5-letter word has been generated.')
    print('Try to guess the word.')
    print()
    
    #set counters
    counter = 1
    bulls = 0
    cows = 0
    match = ''

    #game header display
    display ='Try\tGuess\tResult\n' + \
             '---\t-----\t---------------\n'        

    #game priming read
    game = True

    #while loop controls how long game runs
    while game == True:
        guess = input('Guess the word: ').lower()

        #input validation loop
        while input_check(guess) == False:
            print('Oops.  Make sure you are guessing a 5-letter word with no repeating letters.')
            guess = input('Guess the word: ').lower()
        print()

        #loop compares digits in guess versus digits
        #in code.  Determines how many bulls and cows
        #in each guess.
        for x in range(len(code)):
            if guess[x] in code:
                if x == code.index(guess[x]):
                    match += '1'
                    bulls += 1
                else:
                    match += '2'
                    cows += 1
            else:
                match += '0'

        #display output expands for each guess
        result = str(bulls)+' Bulls,'+' '+str(cows)+' Cows, ' #+ match
        row = str(counter)+'\t'+guess+'\t'+result+'\n'
        display += row
        print(display)

        #winning guess determination. Terminates game.
        if bulls == 5:
            print()
            print('Congratulations.  You guessed the word!')
            print()
            game = False

        #Number of allotted guesses used.  Terminates game.
        elif counter == 8:
            print()
            print('Sorry, you did not guess the word in the allowed number of tries.')
            print()
            print('The answer was "' + code + '".')
            print()
            game = False

        #game continues. Adds 1 to counter. Resets bulls and cows.
        else:
            counter += 1
            bulls = 0
            cows = 0
            match = ''

#define main funtion
def main():

   bulls_and_cows()



   
#call main to execute program
main()
