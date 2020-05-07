# server-e.py (python 3)

import sys
import socket
import _thread
import random


words = ['amount', 'voice', 'oven', 'snake', 'umbrella', 'volcano', 'request',
         'month', 'slope', 'bite', 'form', 'trucks', 'man', 'building', 'toys']

running_games = 0
open_games = 0
waitlist = []


class Hangman(object):
    def __init__(self):
        self.word = random.choice(words).lower()
        self.board = list(("_"*len(self.word)))
        self.incorrect_guesses = []
        self.over = False
        self.won = False

        print(self.word)

    def guess(self, letter):
        correct = True

        if(letter in self.word):
            indices = [i for i, a in enumerate(self.word) if a == letter]
            for i in indices:
                self.board[i] = letter
            self.won = not ('_' in self.board)
        else:
            self.incorrect_guesses.append(letter)
            correct = False

        self.over = not ('_' in self.board) or len(self.incorrect_guesses) >= 6
        return correct


def receive_message_packet(client):
    read = client.recv(1).decode()
    if len(read) is 0:
        return None
    else:
        msg_flag = ord(read)
        if msg_flag == 0:
            return 'solo'
        elif msg_flag == 2:
            return 'multiplayer'
        else:
            return client.recv(msg_flag).decode()


def send_message_packet(client, data):
    msg_flag = chr(len(data))
    client.send((msg_flag + data).encode())


def send_gamecontrol_packet(client, game):
    msg_flag = chr(0)
    word_length = chr(len(game.word))
    num_incorrect = chr(len(game.incorrect_guesses))
    data = ''.join(game.board) + ''.join(game.incorrect_guesses)
    client.send((msg_flag + word_length + num_incorrect + data).encode())


def run_solo(client, game):
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

    client.close()


def run_multiplayer(client1, client2, game):
    both_connected = True
    turn = True

    for client in [client1, client2]:
        send_message_packet(client, 'Game Starting!')

    while(both_connected and not game.over):
        if turn:
            both_connected = handle_turn(client1, client2, '1', game)
        else:
            both_connected = handle_turn(client2, client1, '2', game)

        turn = not turn

    if both_connected:
        for client in [client1, client2]:
            send_gamecontrol_packet(client, game)
            if (game.won):
                send_message_packet(client, 'You Win!')
            else:
                send_message_packet(client, 'You Lose!')

    client1.close()
    client2.close()


def handle_turn(clientA, clientB, num, game):
    send_message_packet(clientA, 'Your Turn!')
    send_message_packet(clientB, 'Waiting on Player ' + num + '...')
    send_gamecontrol_packet(clientA, game)
    guess = receive_message_packet(clientA)
    if guess is None:
        return False
    else:
        if game.guess(guess):
            send_message_packet(clientA, 'Correct!')
        else:
            send_message_packet(clientA, 'Incorrect!')
        return True


def handle_new_client(client, address):
    global running_games, open_games, waitlist

    game_mode = receive_message_packet(client)

    if(running_games >= 3):
        send_message_packet(client, 'server-overloaded')
        client.close()
    else:
        if game_mode is 'solo':
            running_games += 1
            run_solo(client, Hangman())
            running_games -= 1
        elif game_mode is 'multiplayer':
            if open_games is 0:
                open_games += 1
                waitlist.append(client)
                send_message_packet(client, 'Waiting for other player!')
            else:
                open_games -= 1
                running_games += 1
                run_multiplayer(waitlist.pop(0), client, Hangman())
                running_games -= 1


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
