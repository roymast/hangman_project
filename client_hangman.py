# -*- coding: utf-8 -*-
import socket
import pygame
import sys
import select
import time
from textboxClass import *
HANGMAN_MSG = "welcome to my hangman game"
PORT = 31987
START_GAME_REQUEST = "~~start the game request++"
GAME_STARTED_MSG = "~~game starting++"
REQUEST_FOR_WORD = "~~Hello player, it's your turn to pick word++"
WORD_IS_OK = "~~Hello player, the word is ok, the game is starting++"
GUESSING_MODE = "~~Hello player, it's your turn to guess++"
GAME_OVER_MSG = "~~game over++"
TOO_SHORT = "The word is too short, please enter a word with more than 1 char"
WORD_IS = "~~word is:"
ENGLISH_ONLY = "Please enter only english letters"
MAX_LENGTH = 20
TOO_LONG_WORD = "The word is too long, please enter a word with less than 20 chars"
TOO_LONG_GUESS = "The guess is too long, please enter a guess with less than 20 chars"
CONNECTION_ERROR_MSG = "there is an error in connection with the server, game is stopping(press any key to exit)"
WAITING_FOR_WORD_MAG = "one of the players is picking a word, please wait"
EXIT_MSG = "exiting, thanks for playing"
PICKING_PLAYER_QUIT = "player that picked the word quit, game over"
IP_REQUEST = "insert ip"
END_OF_MSG = "++"
START_OF_MSG = "~~"
HOME_IP = "127.0.0.1"
ERROR_IP = "please check your ip address"
NAME_BOX_X = 100
NAME_BOX_Y = 200
NAME_REQUEST = "insert name"
GUESS_MSG = "~~guess:"
GUESS_REQUEST = "enter your guess"
WRONG_LETTERS_MSG = "wrong letters: "
WRONG_WORDS_MSG = "wrong words: "
#pygame----------------------------------------------
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREY = (192, 192, 192)
BLUE = (0, 0, 255)
X_WRONG_LETTERS, Y_WRONG_LETTERS = (20, 400)
X_WRONG_WORDS, Y_WRONG_WORDS = (20, 20)
X_SECRET_WORD, Y_SECRET_WORD = (600, 500)
IP_TEXT_X = 100
IP_TEXT_Y = 100
EXIT_MSG_X = 400
EXIT_MSG_Y = 400
TEXT_HEIGHT_SIZE = 100
CHAR_WIDTH = 100
WAITING_FOR_WORD_X = 50
WAITING_FOR_WORD_Y = 50
PICKING_PLAYER_QUIT_X = 300
PICKING_PLAYER_QUIT_Y = 400

PATH_TO_PICS = r"hangman_pics/hangman_pic_"
PATH_TO_WIN = r"hangman_pics/win.jpg"
FONT = r'fonts/secret_word_2.ttf'

def main():
    screen = init_screen()          # init the screen
    print_text_to_screen(HANGMAN_MSG, screen, 100, 0, WHITE)
    my_socket = connect(screen)
    game_mode(my_socket, screen)
    try:
        my_socket.close()
    except:
        sys.exit()


def init_screen():
    """
    init screen
    return the screen
    """
    pygame.init()
    size = (WINDOW_WIDTH, WINDOW_HEIGHT)
    #screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Game")
    return screen


def print_connection_error(screen):
    """
    func get screen and socket
    func print to screen that there is a connection error, and wait till the user press on key or X
    """
    print_text_to_screen(CONNECTION_ERROR_MSG, screen, 300, 400, RED)
    pygame.display.flip()
    #exit if their is a connection error
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                pygame.quit()
                sys.exit()


def connect(screen):
    """
    func connecting to server
    func return the socket
    """
    ip = pick_ip(screen)
    name = pick_name(screen)
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.settimeout(1)
    try:
        my_socket.connect((ip, PORT))
    except:
        print_connection_error(screen)
    try:
        my_socket.send((name.encode()))
    except:
        print_connection_error(screen)
    start_flag = False
    screen.fill(BLACK)
    #waiting for server to send message to start the game
    while not start_flag:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                try:
                    my_socket.close()
                except:
                    sys.exit()
                sys.exit()
        ready, x, y = select.select([my_socket], [], [], 0)
        if ready:
            data = receive_from_server(my_socket, screen)
            if data == GAME_STARTED_MSG[2:-2]:
                start_flag = True
            screen.fill(BLACK)
            print_str(data, screen)
    return my_socket


def pick_ip(screen):
    """
    func get the surface
    func get from user the ip address from server
    """

    ip_box = textbox(IP_TEXT_X, IP_TEXT_Y, BLACK)
    ip_box.print_box(screen)

    print_text_to_screen(IP_REQUEST, screen, ip_box.get_x()+3, ip_box.get_y()-3, WHITE)
    #loop until the player enters the ip
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if ip_box.get_text() == "home":
                        return HOME_IP
                    if check_ip(ip_box.get_text()):
                        return ip_box.get_text()
                    else:
                        print_text_to_screen(ERROR_IP, screen, ip_box.get_x()+360,
                                             ip_box.get_y()-3, RED)
                elif event.key == pygame.K_BACKSPACE:
                    ip_box.remove_char()
                    screen.fill(ip_box.get_background(), ip_box.get_rect())
                    if ip_box.get_text() == "":
                        print_text_to_screen(IP_REQUEST, screen, ip_box.get_x()+3, ip_box.get_y()-3, WHITE)
                else:
                    if len(ip_box.get_text()) < MAX_LENGTH:
                        ip_box.add_char(event.unicode)
                        if len(ip_box.get_text()) == 1:
                            screen.fill(ip_box.get_background(), ip_box.get_rect())
        ip_box.print_box(screen)


def check_ip(ip):
    """
    func get string that represents ip address
    return true if its ok
    else return false
    """
    if "." in ip:
        if len(ip.split(".")) == 4:
            for part in ip.split("."):
                print (part)
                if part.isdigit():
                    if not 0 <= int(part) <= 255:
                        return False
                else:
                    return False
            return True
        else:
            return False
    else:
        return False


def pick_name(screen):
    """
    func get the surface
    func get from user his name
    """
    name_box = textbox(NAME_BOX_X, NAME_BOX_Y, BLACK)
    name_box.print_box(screen)
    print_text_to_screen(NAME_REQUEST, screen, name_box.get_x()+3, name_box.get_y()-3, WHITE)
    #loop until the user enter his name
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if check_word(name_box.get_text()):
                        return name_box.get_text()
                    else:
                        print_text_to_screen(ENGLISH_ONLY, screen, name_box.get_x()+360, name_box.get_y()-3, RED)
                elif event.key == pygame.K_BACKSPACE:
                    name_box.remove_char()
                    screen.fill(name_box.get_background(), name_box.get_rect())
                    if name_box.get_text() == "":
                        print_text_to_screen(NAME_REQUEST, screen, name_box.get_x()+3, name_box.get_y()-3, WHITE)
                else:
                    if len(name_box.get_text()) < MAX_LENGTH:
                        name_box.add_char(event.unicode)
                        if len(name_box.get_text()) == 1:
                            screen.fill(name_box.get_background(), name_box.get_rect())
        name_box.print_box(screen)
        #pygame.display.flip()


def game_mode(my_socket, screen):
    """
    func get screen surface and socket
    func recieces from socket if player will be in guessing mode or picking mode.
        than func sending the player to the correct func
    """
    while True:
        try:
            mode = receive_from_server(my_socket, screen)
            if mode == REQUEST_FOR_WORD[2:-2]:
                word = pick_word(screen)
                try:
                    my_socket.send((WORD_IS + word.lower() + END_OF_MSG).encode())
                except:
                    print_connection_error(screen)
                picking_mode(screen, my_socket)
            elif mode == GUESSING_MODE[2:-2]:
                guessing_mode(screen, my_socket)
        except:
            print_connection_error(screen)


def picking_mode(screen, my_socket):
    """
    func get screen serface and socket
    func loop till get an input from server
    """
    time.sleep(2)
    word_revealed_letters = receive_from_server(my_socket, screen)  # var that saves the parts of  revealed secret word
    print ("secret word"+word_revealed_letters)
    word_revealed_letters = word_revealed_letters.split(":")[1]
    wrong_letters = ""
    wrong_words = ""
    level_of_hang = "1"
    #draw_board_pick_mode(word_revealed_letters, wrong_letters, wrong_words, screen, level_of_hang)
    over = False
    first = True
    while not over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                screen.fill(GREY)
                print_text_to_screen(EXIT_MSG, screen, EXIT_MSG_X, EXIT_MSG_Y, BLUE)
                pygame.time.delay(500)
                pygame.quit()
                try:
                    my_socket.close()
                except:
                    sys.exit()
                sys.exit()
        over, is_new_data, word_revealed_letters, wrong_letters, wrong_words, level_of_hang = \
            new_data(word_revealed_letters, wrong_letters, wrong_words, my_socket, level_of_hang, screen)
        if is_new_data or first or over:
            draw_hang_man(screen, level_of_hang)
            print_word_revealed_letters(word_revealed_letters, screen)
            print_wrong_letters(wrong_letters, screen)
            print_wrong_words(wrong_words, screen)
            first = False
            pygame.display.flip()
        if over:
            pygame.time.delay(200)
            result = receive_from_server(my_socket, screen)
            print (result)
            draw_results(result, level_of_hang, screen)
            print ("after results")
            pygame.quit()


def guessing_mode(screen, my_socket):
    """
    main func of game:
        func get data from the server for the hangman game and from the player
    """
    word_revealed_letters = get_initial_data(screen, my_socket)
    wrong_letters = ""          # var that saves the wrong letters that players guessed
    wrong_words = ""            # var that saves the wrong words that players guessed
    level_of_hang = "1"         # var that saves the level of the hangman
    last_level_of_hang = 0      # var that saves the last level of the hangman
    over = False                # flag that tells if the game is over or not
    first = True                # flag that tells if this is the first time in loop
    guess_box = textbox(0, 0, GREY)     # text box of the guessing

    #guess_box.print_box(screen
    #print_text_to_screen("enter your guess", screen, guess_box.get_x()+3, guess_box.get_y()-3, BLUE)   # enter guess msg
    # main loop, in this loop the program will take data from player and send it to server.
    # it will also check data from socket and print it
    while not over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                screen.fill(GREY)
                print_text_to_screen(EXIT_MSG, screen, EXIT_MSG_X, EXIT_MSG_Y, BLUE)
                pygame.time.delay(500)
                pygame.quit()
                try:
                    my_socket.close()
                except:
                    sys.exit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # if player pressed ENTER, the program check if it's ok to send, and send it if it does
                if event.key == pygame.K_RETURN:
                    if check_guess(guess_box.get_text()):
                        try:
                            my_socket.send((GUESS_MSG+guess_box.get_text().lower() + END_OF_MSG).encode())
                        except:
                            print ("try to send guess")
                            print_connection_error(screen)
                        guess_box.clear()
                        screen.fill(guess_box.get_background(), guess_box.get_rect())
                        #guess_box.print_box(screen)

                        print_text_to_screen(GUESS_, screen, guess_box.get_x()+3, guess_box.get_y()-3, BLUE)
                #if player pressed backspace, remove char
                elif event.key == pygame.K_BACKSPACE:
                    guess_box.remove_char()
                    screen.fill(guess_box.get_background(), guess_box.get_rect())
                    guess_box.print_box(screen)
                    if guess_box.is_empty():

                        print_text_to_screen(GUESS_REQUEST, screen, guess_box.get_x()+3, guess_box.get_y()-3, BLUE)
                #if player pressed of regular char, add it to the guess
                else:
                    if len(guess_box.get_text()) < MAX_LENGTH and check_guess(event.unicode):
                        guess_box.add_char(event.unicode)
                        if len(guess_box.get_text()) < 1:
                            screen.fill(guess_box.get_background(), guess_box.get_rect())
                            print_text_to_screen(GUESS_REQUEST, screen, guess_box.get_x()+3, guess_box.get_y()-3,
                                                 BLUE)
                        if len(guess_box.get_text()) == 1:
                            screen.fill(guess_box.get_background(), guess_box.get_rect())
                        guess_box.print_box(screen)
        #check if their is a new data from server, and change the parameters
        over, is_new_data, word_revealed_letters, wrong_letters, wrong_words, level_of_hang = \
            new_data(word_revealed_letters, wrong_letters, wrong_words, my_socket, level_of_hang, screen)
        # if the game is over, draw results
        if over:
            print ("in over")
            #draw_over(screen, my_socket, level_of_hang, word_revealed_letters, wrong_letters, wrong_words, guess_box)
            draw_hang_man(screen, level_of_hang)
            print_word_revealed_letters(word_revealed_letters, screen)
            print_wrong_letters(wrong_letters, screen)
            print_wrong_words(wrong_words, screen)
            pygame.time.delay(2000)
            result = receive_from_server(my_socket, screen)
            print (result)
            draw_results(result, level_of_hang, screen)
            break
        # if their is a new data from server, print it to screen
        if is_new_data:
            print ("in new data")
            #draw_new_data(screen, last_level_of_hang, level_of_hang, guess_box, word_revealed_letters, wrong_letters,wrong_words)
            if last_level_of_hang != level_of_hang:
                draw_hang_man(screen, level_of_hang)
            if guess_box.is_empty():
                guess_box.print_box(screen)
                print_text_to_screen(GUESS_REQUEST, screen, guess_box.get_x()+3, guess_box.get_y()-3, BLUE)
            else:
                guess_box.print_box(screen)
            print_word_revealed_letters(word_revealed_letters, screen)
            print_wrong_letters(wrong_letters, screen)
            print_wrong_words(wrong_words, screen)
            pygame.display.flip()
        # if it the first time at loop, print all of the data
        if first:
            print ("in first")
            #draw_first(screen, last_level_of_hang, guess_box, word_revealed_letters, wrong_letters, wrong_words)
            print ("draw hang man")
            draw_hang_man(screen, level_of_hang)
            print ("print_text_to_screen")
            print_text_to_screen(GUESS_REQUEST, screen, guess_box.get_x()+3, guess_box.get_y()-3, BLUE)
            guess_box.print_box(screen)
            print_word_revealed_letters(word_revealed_letters, screen)
            print_wrong_letters(wrong_letters, screen)
            print_wrong_words(wrong_words, screen)
            pygame.display.flip()
            last_level_of_hang = level_of_hang
            print ("done first")
            first = False


def get_initial_data(screen, my_socket):
    word_revealed_letters = ""  # var that saves the parts of the revealed secret word
    #waiting for server to send the word
    while word_revealed_letters == "":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                screen.fill(GREY)
                print_text_to_screen(EXIT_MSG, screen, 400, 400, BLUE)
                pygame.time.delay(500)
                pygame.quit()
                try:
                    my_socket.close()
                except:
                    sys.exit()
                sys.exit()
        print_text_to_screen(WAITING_FOR_WORD_MAG, screen, WAITING_FOR_WORD_X, WAITING_FOR_WORD_Y, BLUE)
        pygame.display.flip()
        rlist, wlist, xlist = select.select([my_socket], [], [], 0)
        for current in rlist:
            try:
                word_revealed_letters = receive_from_server(current, screen)
                if word_revealed_letters == PICKING_PLAYER_QUIT:
                    picking_player_quit(screen)
                word_revealed_letters = word_revealed_letters.split(":")[1]
            except:
                print_connection_error(screen)
    return word_revealed_letters

def picking_player_quit(screen):
    screen.fill(GREY)
    print_text_to_screen(PICKING_PLAYER_QUIT, screen, PICKING_PLAYER_QUIT_X, PICKING_PLAYER_QUIT_Y, RED)
    #exit if their is a connection error
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                pygame.quit()
                sys.exit()
        print_text_to_screen(PICKING_PLAYER_QUIT, screen, PICKING_PLAYER_QUIT_X, PICKING_PLAYER_QUIT_Y, RED)


def new_data(word_revealed_letters, wrong_letters, wrong_words, my_socket, level_of_hang, screen):
    """
    func return true if the game ended, else return false
    func return true if their is a new data from server, else return false
    func return the parts of that reavield from secret word
    func return the wrong letters that players guessed
    func return the wrong words that players guessed
    func return the level of the hang
    """
    over = False
    rlist, wlist, xlist = select.select([my_socket], [], [], 0)
    for current in rlist:
        try:
            data = receive_from_server(current, screen)
            if data.split(":")[0] == "changed":
                level_of_hang = data.split(":")[1]
                word_revealed_letters = receive_from_server(my_socket, screen)
                word_revealed_letters = word_revealed_letters.split(":")[1]
                wrong_letters = receive_from_server(my_socket, screen)
                wrong_letters = wrong_letters.split(":")[1]
                wrong_words = receive_from_server(my_socket, screen)
                wrong_words = wrong_words.split(":")[1]
            if data == GAME_OVER_MSG[2:-2]:
                over = True
            return over, True, word_revealed_letters, wrong_letters, wrong_words, level_of_hang
        except:
            print_connection_error(screen)
    return over, False, word_revealed_letters, wrong_letters, wrong_words, level_of_hang


def draw_first(screen, level_of_hang, guess_box, word_revealed_letters, wrong_letters, wrong_words):
    """
    draw the screen at the beggining of the game
    :param screen: the screen
    :param level_of_hang: level
    :param guess_box: box of the guess
    :param word_revealed_letters: var that saves the parts of the revealed secret word
    :param wrong_letters: saves the wrong letter that already guessed
    :param wrong_words: saves the wrong words that already guessed
    """
    print ("draw hang man")
    draw_hang_man(screen, level_of_hang)
    print ("print_text_to_screen")
    print_text_to_screen(GUESS_REQUEST, screen, guess_box.get_x()+3, guess_box.get_y()-3, BLUE)
    guess_box.print_box(screen)
    print_word_revealed_letters(word_revealed_letters, screen)
    print_wrong_letters(wrong_letters, screen)
    print_wrong_words(wrong_words, screen)
    pygame.display.flip()


def draw_new_data(screen, last_level_of_hang, level_of_hang, guess_box, word_revealed_letters, wrong_letters,wrong_words):
    """
    func draw the screen when there is new data
    :param screen: the screen
    :param last_level_of_hang: the last level
    :param level_of_hang: the current level
    :param guess_box: box of the guess
    :param word_revealed_letters: var that saves the parts of the revealed secret word
    :param wrong_letters: saves the wrong letter that already guessed
    :param wrong_words: saves the wrong words that already guessed
    """
    if last_level_of_hang != level_of_hang:
        draw_hang_man(screen, level_of_hang)
    if guess_box.is_empty():
        guess_box.print_box(screen)
        print_text_to_screen(GUESS_REQUEST, screen, guess_box.get_x()+3, guess_box.get_y()-3, BLUE)
    else:
        guess_box.print_box(screen)
    print_word_revealed_letters(word_revealed_letters, screen)
    print_wrong_letters(wrong_letters, screen)
    print_wrong_words(wrong_words, screen)
    pygame.display.flip()

def draw_over(screen, my_socket, level_of_hang, word_revealed_letters, wrong_letters, wrong_words, guess_box):
    """
    func draw the screen when over, than print results
    :param screen: the screen
    :param level_of_hang: level
    :param guess_box: box of the guess
    :param word_revealed_letters: var that saves the parts of the revealed secret word
    :param wrong_letters: saves the wrong letter that already guessed
    :param wrong_words: saves the wrong words that already guessed
    :param my_socket: the socket
    """
    draw_hang_man(screen, level_of_hang)
    print_word_revealed_letters(word_revealed_letters, screen)
    print_wrong_letters(wrong_letters, screen)
    print_wrong_words(wrong_words, screen)
    pygame.time.delay(2000)
    result = receive_from_server(my_socket, screen)
    print (result)
    draw_results(result, level_of_hang, screen)


def draw_hang_man(screen_in, level_of_hang):
    """
    func prints the picture of the hangman according to the level
    """
    print ("a")
    img = pygame.image.load(PATH_TO_PICS+level_of_hang+".png")
    print ("b")
    screen_in.blit(img, (0, 0))
    print ("c")


def print_word_revealed_letters(word_revealed_letters, screen):
    """
    printing to screen the revealed letter from secret words
    """
    pygame.draw.rect(screen, GREY, (0, Y_SECRET_WORD-30, 1280, 60))
    #pygame.display.flip()
    font = pygame.font.Font(FONT, 60)
    # copying the text surface object
    # to the display surface object
    # at the center coordinate.
    word_revealed_letters_text = font.render(word_revealed_letters, True, BLACK)
    word_revealed_letters_rect = word_revealed_letters_text.get_rect()
    word_revealed_letters_rect.center = (X_SECRET_WORD, Y_SECRET_WORD)
    screen.blit(word_revealed_letters_text, word_revealed_letters_rect)
    #pygame.display.flip()


def print_wrong_letters(wrong_letters, screen):
    """
    printing to screen the wrong letters that already guessed
    """
    font = pygame.font.Font(FONT, 30)
    wrong_letters_text = font.render(WRONG_LETTERS_MSG , True, BLACK)

    wrong_letters_rect = (X_WRONG_LETTERS, Y_WRONG_LETTERS)
    screen.blit(wrong_letters_text, wrong_letters_rect)
    #pygame.display.flip()
    wrong_letters_text = font.render(wrong_letters, True, RED)

    wrong_letters_rect = (X_WRONG_LETTERS+155, Y_WRONG_LETTERS)
    screen.blit(wrong_letters_text, wrong_letters_rect)
    #pygame.display.flip()


def print_wrong_words(wrong_words, screen):
    """
    printing to screen the wrong words that already guessed
    """
    font = pygame.font.Font(FONT, 30)
    wrong_words_text = font.render(WRONG_WORDS_MSG, True, BLACK)

    # set the center of the rectangular object.
    wrong_words_rect = (X_WRONG_WORDS, Y_WRONG_WORDS)
    screen.blit(wrong_words_text, wrong_words_rect)
    # create a rectangular object for the
    # text surface object
    #pygame.display.flip()
    wrong_words = wrong_words.split(", ")

    for i in range(len(wrong_words)):
        word = wrong_words[i]
        if len(word) > 0:
            font = pygame.font.Font(FONT, 30)
            text = font.render(word, True, RED)
            screen.blit(text, (30, int(TEXT_HEIGHT_SIZE/3)*i+45))
    #pygame.display.flip()


def draw_results(result, level_of_hang, screen):
    """
    func get the result that sended from server, the level of the hang, the screen
    func print to screen picture of victory if the man is not dead,
    """
    if level_of_hang != "10":
        img = pygame.image.load(PATH_TO_WIN)
        screen.blit(img, (0, 0))
        pygame.display.flip()
    else:
        screen.fill(GREY)
        pygame.display.flip()
    print_results(result, screen)
    finish = False
    #waitng for player to press on keyboard, or press of the X with the mouse
    while not finish:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finish = True
            if event.type == pygame.KEYDOWN:
                finish = True
    pygame.quit()


def print_str(string, screen):
    """
    func print to screen string with \n
    """
    lst = string.split("\n")
    for i in range(len(lst)):
        name = lst[i]
        if len(name) > 0:
            font = pygame.font.Font(FONT, 30)
            text = font.render(name, True, (0, 128, 0))
            screen.blit(text, (30, int(TEXT_HEIGHT_SIZE/3)*i+5))

            print (name)
    pygame.display.flip()


def print_text_to_screen(text, screen, x, y, color):
    """
    func get text, screen, x and y coordinations of text and his color
    func print regular text to screen
    """
    font = pygame.font.Font(FONT, 30)
    text_surface = font.render(text, True, color)
    # Blit the text.
    screen.blit(text_surface, (x, y))
    # Blit the input_box rect.


def receive_from_server(my_socket, screen):
    """
    func get socket and screen
    func receive data from the server
    """
    my_socket.settimeout(0)
    rlist, wlist, xlist = select.select([my_socket], [], [], 0)
    for current in rlist:
        try:
            prefix = current.recv(2)
            if prefix != "":
                data = ""
                #keep receive till "++"
                while END_OF_MSG not in data:
                    data += current.recv(1).decode()
                return data[:-2]
            else:
                print_connection_error(screen)
        except:
            print_connection_error(screen)


def check_word(word):
    """
    :param word: the word of the player
    :return: bool
     if word is a string with only english letters-  return True
     else-  return False
    """
    if len(word) <= 1:
        print (TOO_SHORT)
        return False
    elif len(word) > MAX_LENGTH:
        print (TOO_LONG_WORD)
        return False
    else:
        for let in word:
            if (ord(let) < 65) or (ord(let) > 90) and (ord(let) < 97) or (ord(let) > 122):
                print (ENGLISH_ONLY)
                return False
        return True


def check_guess(guess):
    """
    :param guess: the guess of the player
    :return: bool
     if guess is a char/string with only english letters-  return True
     else-  return False
    """
    if len(guess) > 20:
        print (TOO_LONG_GUESS)
        return False
    for let in guess:
        if (ord(let) < 65) or (ord(let) > 90) and (ord(let) < 97) or (ord(let) > 122):
            return False

    return True


def pick_word(screen):
    """
    func request from player to pick a word
    func return the word
    """
    secret_word_box = textbox(100, 200, BLACK)
    secret_word_box.print_box(screen)
    print_text_to_screen("pick word", screen, secret_word_box.get_x()+3, secret_word_box.get_y()-3, WHITE)
    #loop until the user enter his name
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if check_word(secret_word_box.get_text()):
                        return secret_word_box.get_text()
                    else:
                        print_text_to_screen(ENGLISH_ONLY, screen, secret_word_box.get_x()+360,
                                             secret_word_box.get_y()-3, RED)
                elif event.key == pygame.K_BACKSPACE:
                    secret_word_box.remove_char()
                    screen.fill(secret_word_box.get_background(), secret_word_box.get_rect())
                    if secret_word_box.get_text() == "":
                        print_text_to_screen("pick word", screen, secret_word_box.get_x()+3, secret_word_box.get_y()-3,
                                             WHITE)
                else:
                    if len(secret_word_box.get_text()) < MAX_LENGTH:
                        secret_word_box.add_char(event.unicode)
                        if len(secret_word_box.get_text()) == 1:
                            screen.fill(secret_word_box.get_background(), secret_word_box.get_rect())
        secret_word_box.print_box(screen)


def print_results(results, screen):
    """
    func get results from server
    func prints them to screen
    """
    lst = results.split("\n")
    for i in range(len(lst)):
        if i == 0:
            name = lst[i]
        else:
            name = lst[i]
        if len(name) > 0:
            font = pygame.font.Font(FONT, 30)
            text = font.render(name, True, (0, 128, 0))
            #text = pygame.transform.scale(text, (len(name[0])*CHAR_WIDTH, TEXT_HEIGHT_SIZE))
            screen.blit(text, (30, (TEXT_HEIGHT_SIZE/3)*i+5))

            print (name)
    pygame.display.flip()


if __name__ == '__main__':
    main()
