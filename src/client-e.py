# client-e.py (python 3)

import sys
import socket
import string


board = []
guesses = []
incorrect_guesses = []


def send_message_packet(socket, data):
    msg_flag = chr(len(data))
    if len(data) is not 1:
        data = ''
    socket.send((msg_flag + data).encode())


def handle_message_packet(socket, msg_flag):
    print(socket.recv(msg_flag).decode())


def handle_gamecontrol_packet(socket):
    global board, incorrect_guesses

    word_length = ord(socket.recv(1).decode())
    num_incorrect = ord(socket.recv(1).decode())
    board = list(socket.recv(word_length).decode())
    incorrect_guesses = list(socket.recv(num_incorrect).decode())
    update_guesses()

    print(' '.join(board))
    print('Incorrect Guesses: ', ' '.join(incorrect_guesses))
    print()


def update_guesses():
    global guesses, board, incorrect_guesses
    guesses = [letter for letter in list(string.ascii_lowercase)
               if (letter in guesses or letter in board or letter in incorrect_guesses)
               ]


def wannaMultiplayer():
    return (input('Two Player? (y/n): ') == 'y')


def shouldStartTheGame():
    return (input('Ready to start game? (y/n): ') == 'y')


def connect(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    return s


def guess():
    global guesses

    while True:
        guess = input('Letter to guess: ').lower()
        if len(guess) is not 1 or not guess in list(string.ascii_lowercase):
            print('Error! Please guess one letter.')
        elif guess in guesses:
            print('Error! Letter', guess,
                  'has been guessed before, please guess another letter.')
        else:
            guesses.append(guess)
            return guess


def play(socket, game_mode):
    global board, incorrect_guesses

    send_message_packet(socket, game_mode)

    while True:
        something = socket.recv(1).decode()
        if len(something) is 0:
            break

        msg_flag = ord(something)

        if msg_flag:
            handle_message_packet(socket, msg_flag)
        else:
            handle_gamecontrol_packet(socket)
            if '_' in board and len(incorrect_guesses) < 6:
                send_message_packet(socket, guess())

    socket.close()


if __name__ == "__main__":

    # ip, port = '127.1', 9012

    argc, argv = len(sys.argv), sys.argv
    ip, port = argv[1], int(argv[2])

    game_mode = ''
    if wannaMultiplayer():
        game_mode = '  '

    if shouldStartTheGame():
        play(connect(ip, port), game_mode)
