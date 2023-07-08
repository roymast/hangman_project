# -*- coding: utf-8 -*-
from ClassPlayer import *
import select
import socket
import random
import time
import sys
PORT = 31987
REQUEST_FOR_SECRET_WORD = "~~Hello player, it's your turn to pick word++"
GUESSING_MODE = "~~Hello player, it's your turn to guess++"
REQUEST_TIMEOUT = "~~Hello player, time is up to pick a secret word, someone else will pick the secret word++"
SECRET_WORD_IS_OK = "~~Hello player, the word is ok, the game is starting++"
START_GAME_REQUEST = "~~start the game request++"
GAME_STARTED_MSG = "~~game starting++"
GAME_OVER_MSG = "~~game over++"
PICKING_PLAYER_QUIT = "player that picked the word quit, game over"
EMPTY = '_'
level_of_hang = 1
MAX_GUESS = 20
END_OF_MSG = "++"
START_OF_MSG = "~~"


def main():
    hostname = socket.gethostname()         # get computer name
    IPAddr = socket.gethostbyname(hostname) # get computer ip
    print("Your Computer IP Address is:" + IPAddr)
    server_socket, clients = create_connection()
    index_players = random.randint(0, len(clients)-1)
    secret_word, word_reveled_letters = request_word(clients, server_socket, index_players)
    game(clients, server_socket, secret_word, word_reveled_letters)


def create_connection():
    """
    func create connection with all of the clients
    func return server socket and clients list
    """
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', PORT))
    number_of_players = input("enter amount of players(more than 2): ")
    while not number_of_players.isdigit() or int(number_of_players) < 2:
        number_of_players = input("enter amount of players again(more than 2): ")
    print ("amount of players is ok")
    server_socket.listen(int(number_of_players))         #start connection with
    clients = []
    while len(clients) < int(number_of_players):
        clients_sockets = []
        for c in clients:
            clients_sockets.append(c.get_socket())
        rlist, wlist, xlist = select.select([server_socket]+clients_sockets, clients_sockets, [], 0)
        for current_socket in rlist:
            if current_socket is server_socket:
                (new_socket, address) = server_socket.accept()
                clients.append(Player(new_socket))
                clients[-1].set_name(clients[-1].get_socket().recv(1024).decode())
                game_players_msg = START_OF_MSG + "Players amount: " + str(len(clients)) + "/" + str(number_of_players)\
                                   + "\n players names:\n"   # make message with the players amount and their names
                for c in clients:                       # add players name to the message
                    game_players_msg += c.get_name()+"\n"
                for c in clients:                       # send the message to all of clients
                    try:
                        c.get_socket().send((game_players_msg+END_OF_MSG).encode())
                    except:
                        continue
                print (game_players_msg)
    for c in clients:                       # sending to all players that the game started
        try:
            c.get_socket().send((GAME_STARTED_MSG).encode())
            print (GAME_STARTED_MSG)
        except:
            continue
    return server_socket, clients


def request_word(clients, server_socket, index_players):
    """
    func request secret word for the game
    func return: secret word to guess, next player index in list, word_reveled_letters
    :param clients: list of the clients
    :param server_socket: socket of the server
    :param index_players: number that index the player that will pick word
    """
    server_socket.settimeout(None)
    word_reveled_letters = []       # list of the hidden secret word
    secret_word = ""                # string of the secret word
    # sending to all of the players if they will puck word, or guess the word
    for c in range(len(clients)):
        if c == index_players:
            clients[c].get_socket().send(REQUEST_FOR_SECRET_WORD.encode())
        else:
            clients[c].get_socket().send(GUESSING_MODE.encode())
    # wait till the player send a good word
    while secret_word is "":
        ready, x, y = select.select([clients[index_players].get_socket()], [], [], 0)
        if ready:
            try:
                secret_word = clients[index_players].get_socket().recv(1024).decode()
            except:
                picking_player_quit(clients)
                sys.exit()
    print (index_players)
    # create the list of the hidden secret word
    secret_word = secret_word.split(":")[1][:-2]
    for char in secret_word:                       #create "word_reveled_letters". It will be the list that will show what reveled from secret word
        word_reveled_letters.append(EMPTY)
        print (char)
    print (word_reveled_letters)
    #sending to all of the players the secret word
    for c in range(len(clients)):
        clients[c].get_socket().send((START_OF_MSG + "word is:"+list_to_string_no_comma(word_reveled_letters) + END_OF_MSG).encode())
    return secret_word, word_reveled_letters


def picking_player_quit(clients):
    for client in clients:
        try:
            client.send((START_OF_MSG + PICKING_PLAYER_QUIT + END_OF_MSG).encode())
        except:
            continue

def check_word(secret_word):
    """
    :param secret_word: the secret word of the player
    :return: bool
     if guess is a string with only english letters-  return True
     else-  return False
    """
    if ":" not in secret_word:
        return False
    if secret_word.split(":")[0] == START_OF_MSG + "word is":
        secret_word = secret_word.split(":")[1][:-2]
        if len(secret_word) <= 1:
            return False
        else:
            for let in secret_word:
                if (ord(let) < 65) or ((ord(let) > 90) and (ord(let) < 97)) or (ord(let) > 122):
                    return False
            return True


def game(clients, server_socket, secret_word, word_reveled_letters):
    """
    :param clients: list of players
    :param server_socket:
    :param secret word: the secret word to guess
    func wait for the clients to send guess.
    when someone send guess-->check the input
    (if true)-->check if in the guess was right-->(if was)-->add point for player-->check if word is fully guessed(if was, end game)
    """
    global level_of_hang
    wrong_letters = []
    wrong_words = []
    is_done = False
    is_dead = False
    changed = False
    print ("len of clients"+str(len(clients)))
    while not is_done and not is_dead:
        sockets = []
        for client in clients:
            sockets.append(client.get_socket())
        guess = ""
        rlist, wlist, xlist = select.select(sockets, [], [], 0)
        for c in rlist:
            try:
                guess = c.recv(1024).decode()
            except:
                continue
            if guess != "":
                print (len(guess))
                if check_guess(guess):
                    guess = guess.split(":")[1][:-2]
                    print (guess)
                    client_socket = match_socket_to_player(c, clients)
                    in_word, done, word_reveled_letters, wrong_letters, wrong_words = is_in_word(
                        guess, secret_word, word_reveled_letters, wrong_letters, wrong_words, client_socket)
                    if in_word:
                        changed = True
                        if done == "done":
                            is_done = True
                    else:
                        wrong_letters.sort()
                        wrong_words.sort()
                        level_of_hang += 1
                        changed = True
                        if level_of_hang == 10:
                            is_dead = True
                else:
                    continue
        if changed:
            print (START_OF_MSG + "changed:"+list_to_string_no_comma(word_reveled_letters)+END_OF_MSG)
            sockets = []
            for client in clients:
                sockets.append(client.get_socket())
            rlist, wlist, xlist = select.select([], [server_socket] + sockets, [server_socket] + sockets, 0)
            print ("wlist=="+str(wlist))
            for c in wlist:
                if wlist:
                    try:
                        print (START_OF_MSG + "changed:"+str(level_of_hang) + END_OF_MSG)
                        c.send((START_OF_MSG + "changed:"+str(level_of_hang) + END_OF_MSG +
                               START_OF_MSG + "changed:"+list_to_string_no_comma(word_reveled_letters) + END_OF_MSG +
                               START_OF_MSG + "changed:"+list_to_string_with_comma(wrong_letters) + END_OF_MSG +
                               START_OF_MSG + "changed:"+list_to_string_with_comma(wrong_words) + END_OF_MSG).encode())
                    except:
                        continue
            changed = False
    print ("game over")
    show_points(clients, server_socket, is_dead)


def match_socket_to_player(socket, clients):
    for client in clients:
        if client.get_socket() is socket:
            return client


def is_in_word(guess, secret_word, word_reveled_letters, wrong_letters, wrong_words, c):
    """
    :param secret_word: the secret_word that need to guess
    :param guess: the guess of the player(string or char)
    :param word_reveled_letters: list of the letters that reveled
    :param wrong_letters: list of the letters that guessed wrong
    :param wrong_words: list of the word that guessed wrong
    return:bool, string("done"/"not done")
    if guess is char of the secret word AND if the secret word completed --> return true, "done"
    if guess is char of the secret word AND if the secret word is not completed --> return true, "not done"
    if guess is not char of the secret word --> return false, "not done"
    """
    if len(guess) > 1:                              #check if the guess is a word or char
        if guess == secret_word:                           #check if the guess equals to the secret word
            for char in word_reveled_letters:
                if word_reveled_letters != EMPTY:
                    c.add_point()
                    c.add_point()
            return True, "done", secret_word, wrong_letters, wrong_words
        if guess in wrong_words:
            return True, "not done", word_reveled_letters, wrong_letters, wrong_words
        wrong_words.append(guess)
        return False, "not done", word_reveled_letters, wrong_letters, wrong_words
    if guess in secret_word:                               #check if the guess is in the word
        if guess not in word_reveled_letters and guess not in wrong_letters:
            for let in range(len(secret_word)):                              #going all over the word to make sure that all of the letters guessed are reveled
                if secret_word[let] == guess:
                    word_reveled_letters[let] = guess
                    c.add_point()
        if EMPTY in word_reveled_letters:           #check if the secret word complete
            return True, "not done", word_reveled_letters, wrong_letters, wrong_words
        else:
            return True, "done", word_reveled_letters, wrong_letters, wrong_words
    else:
        if guess not in wrong_letters:
            wrong_letters.append(guess)
            return False, "not done", word_reveled_letters, wrong_letters, wrong_words
        return True, "not done", word_reveled_letters, wrong_letters, wrong_words


def list_to_string_with_comma(lst):
    """
    func get list and return string of the values supperated by comma
    """
    if len(lst) == 0:
        return ""
    s = ""
    for char in lst[:-1]:
        s += char + ", "
    return s + lst[-1]


def list_to_string_no_comma(lst):
    """
    func get list and return string of the values
    """
    s = ""
    for char in lst:
        s += char + " "
    return s


def show_points(clients, server_socket, is_dead):
    """
    :param clients: list of the players
    :server_socket: server_socket
    func send to all of the players the results of the players
    """
    time.sleep(3)
    server_socket.settimeout(0)
    endgame_msg = START_OF_MSG + "RESULTS\n"
    clients_sockets = []
    #creating sockets list
    for c in clients:
        clients_sockets.append(c.get_socket())
    #creating the message for the end
    for c in clients:
        endgame_msg += c.get_name()+":" + str(c.get_points()) + '\n'
    #sending the results to the players
    rlist, wlist, xlist = select.select([], clients_sockets, [], 0)
    for current_client in wlist:
        try:
            current_client.send((GAME_OVER_MSG+endgame_msg + END_OF_MSG).encode())
        except:
            continue
    #closeing the sockets
    for client in clients:
        try:
            client.get_socket().close()
        except:
            continue


def check_guess(guess):
    """
    :param guess: the guess of the player
    :return: bool
     if guess is a char/string with only english letters-  return True
     else-  return False
    """
    if len(guess) == 0:
        return False
    if len(guess.split(":")[1][:-2]) > MAX_GUESS:
        return False
    if guess.split(":")[0] == START_OF_MSG + "guess":
        print (guess.split(":")[1][:-2])
        guess = guess.split(":")[1][:-2]
        for let in guess:
            if (ord(let) < 65) or ((ord(let) > 90) and (ord(let) < 97)) or (ord(let) > 122):
                return False
        return True
    return False


if __name__ == '__main__':
    main()
