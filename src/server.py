# server.py (python 3)

import sys
import socket
import _thread
import random


words = ['amount', 'voice', 'oven', 'snake', 'umbrella', 'volcano', 'request',
         'month', 'slope', 'bite', 'form', 'trucks', 'man', 'building', 'toys']
games = 0


class Hangman(object):
    def __init__(self):
        self.word = random.choice(words).lower()
        self.board = list(("_"*len(self.word)))
        self.incorrect_guesses = []
        self.over = False
        self.won = False

        print(self.word)

    def guess(self, letter):
        if(letter in self.word):
            indices = [i for i, a in enumerate(self.word) if a == letter]
            for i in indices:
                self.board[i] = letter
            self.won = not ('_' in self.board)
        else:
            self.incorrect_guesses.append(letter)

        self.over = not ('_' in self.board) or len(self.incorrect_guesses) >= 6


def receive_message_packet(client):
    read = client.recv(1).decode()
    if len(read) is 0:
        return None
    else:
        msg_flag = ord(read)
        if msg_flag == 0:
            return ''
        else:
            return client.recv(msg_flag).decode()


def send_message_packet(client, data):
    msg_flag = chr(len(data))
    # print msg_flag + data
    client.send((msg_flag + data).encode())


def send_gamecontrol_packet(client, game):
    msg_flag = chr(0)
    word_length = chr(len(game.word))
    num_incorrect = chr(len(game.incorrect_guesses))
    data = ''.join(game.board) + ''.join(game.incorrect_guesses)
    # print msg_flag + word_length + num_incorrect + data
    client.send((msg_flag + word_length + num_incorrect + data).encode())


def run_game(client, game):
    connected = True

    while(connected and not game.over):
        send_gamecontrol_packet(client, game)
        guess = receive_message_packet(client)

        if guess is None:
            connected = False
        else:
            game.guess(guess)

    if connected:
        send_gamecontrol_packet(client, game)
        if (game.won):
            send_message_packet(client, 'You Win!')
        else:
            send_message_packet(client, 'You Lose!')


def handle_new_client(client, address):
    global games

    receive_message_packet(client)

    if(games >= 3):
        send_message_packet(client, 'server-overloaded')
    else:
        game = Hangman()
        games += 1
        run_game(client, game)
        games -= 1

    client.close()
    # print 'Connection with', address, 'has been closed.'


def fire_server(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(5)

    while True:
        client, address = s.accept()
        # print 'Connection with', address, 'has been established!'
        _thread.start_new_thread(handle_new_client, (client, address))


if __name__ == "__main__":

    # ip, port = '127.1', 9012

    argc, argv = len(sys.argv), sys.argv
    ip, port = argv[1], int(argv[2])

    fire_server(ip, port)
