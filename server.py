import socket
import threading
from _thread import start_new_thread
import time
from game_engine import GameEngine

VALID_TABLE_SIZES = [3, 4, 5]
MINIMUM_TABLE_SIZE = 3
SERVER_PORT = 8080
HOST = ""
GAME_LOBBY = 0
IN_GAME = 1
FIRST_PLAYER = 0
SECOND_PLAYER = 1
CUR_PLAYER_TURN_SIGN = '#'
END_GAME_SIGN = '$'

CORRECT_MOVE = 1
WRONG_MOVE = -1

waiting_list = [[] for i in range(3)]
client_status = {}

waiting_list_lock = threading.Lock()
client_status_lock = threading.Lock()


# It's a helper function, which we use in check_waiting_lists functions.
# We use this function to check each table size waiting list and pair players in waiting lists
# which have more than one player and update corresponding waiting lists.
# Also, we change players status from GAME_LOBBY to IN_GAME.
def manage_waiting_list(table_size_ind):
    table_size = table_size_ind + MINIMUM_TABLE_SIZE
    with client_status_lock:
        for i in range(0, len(waiting_list[table_size_ind]), 2):
            new_game_engine = GameEngine(table_size=table_size)
            client_status[waiting_list[table_size_ind][i]] = (IN_GAME, new_game_engine, FIRST_PLAYER)
            client_status[waiting_list[table_size_ind][i + 1]] = (IN_GAME, new_game_engine, SECOND_PLAYER)
    if len(waiting_list[table_size_ind]) % 2 == 0:
        return []
    else:
        return [waiting_list[table_size_ind][-1]]


# It's the function which checks the waiting list each 5 secs and match the players with same chosen table size.
def check_waiting_lists():
    while True:
        with waiting_list_lock:
            print("Before:", waiting_list)
            for table_size in VALID_TABLE_SIZES:
                table_size_ind = table_size - MINIMUM_TABLE_SIZE
                if len(waiting_list[table_size_ind]) >= 2:
                    waiting_list[table_size_ind] = manage_waiting_list(table_size_ind)
            print("After:", waiting_list)
        time.sleep(5)


# It's a function which manages the game lobby. When a player is in GAME_LOBBY state, he/she will wait in
# here until another player is found with same chose table size. When the player state changes from
# GAME_LOBBY to IN_GAME, the run_game function will be called and the player can start playing.
def game_lobby(client_fd):
    with client_status_lock:
        client_status[client_fd] = (GAME_LOBBY, None)
    client_fd.sendall('Welcome to the Tic-Tac-Toe Server\n'.encode())
    client_table_size = int(client_fd.recv(1024).decode().strip())
    client_fd.sendall(f'Table size={client_table_size}\n'.encode())
    with waiting_list_lock:
        client_table_size_ind = client_table_size - MINIMUM_TABLE_SIZE
        waiting_list[client_table_size_ind].append(client_fd)
    while client_status[client_fd][0] == GAME_LOBBY:
        continue
    client_fd.sendall("Your game will start shortly...\n".encode())
    run_game(client_fd=client_fd, game_engine=client_status[client_fd][1], client_turn=client_status[client_fd][2])


# It's a function to create welcome message for players.
def create_welcome_message(game_engine, client_turn):
    message = "Your game has started and "
    if client_turn == game_engine.get_cur_player():
        message += "You are the first player; your sign is X\n"
    else:
        message += "You are the second player; your sign is O\n"
        message += create_table_message(game_engine.get_table())
    return message


# It's a function to read table and convert its information to string.
def create_table_message(table):
    message = ""
    for i in range(len(table)):
        for j in range(len(table)):
            message += table[i][j]
            if j != len(table) - 1:
                message += " | "
        message += "\n"
    return message


# It's a function to convert player movements status to string.
def create_status_message(status):
    message = ""
    if status == WRONG_MOVE:
        message += "Wrong Move!\n"
    else:
        message += "Marked Successfully!\n"
    return message


# It's a function to create the message which we want to send after a player has made his/her move.
# It will concat game table information and movement status.
def create_end_turn_message(table, status):
    message = create_table_message(table)
    message += create_status_message(status)
    return message


# It's a function to create the message which we want to send in the end of the game.
# It has the table information for the loser and the information about
# the status of the game which can be Win, lose, or Draw.
def send_final_message(client_fd, game_engine, client_turn):
    message = END_GAME_SIGN
    if game_engine.get_cur_player() == client_turn:
        message += create_table_message(game_engine.get_table())
        if game_engine.get_draw_flag():
            message += "Draw...\n"
        else:
            message += "You just lost the game...\n"
    else:
        if game_engine.get_draw_flag():
            message += "Draw...\n"
        else:
            message += "\n" + "You won...\n"
    client_fd.sendall(message.encode())


# It's a function which we use to put the player in game. Two matched players, will use
# this function to play with each other. This function, will get players movement, updates the table,
# change the active player, and specify win/lose/draw state of the game.
def run_game(client_fd, game_engine, client_turn):
    message = create_welcome_message(game_engine, client_turn)
    client_fd.sendall(message.encode())
    time.sleep(2)
    while True:
        if game_engine.get_cur_player() != client_turn:
            client_fd.sendall("Waiting for the other player...\n".encode())
        while game_engine.get_cur_player() != client_turn:
            continue
        if game_engine.is_game_finished():
            break
        cur_table_message = create_table_message(game_engine.get_table())
        client_fd.sendall(
            f"{CUR_PLAYER_TURN_SIGN}\n{cur_table_message}\nIts your turn! Enter the place you want to mark...\n".encode())
        mark_position = int(client_fd.recv(1024).decode().strip())
        updated_table, status = game_engine.update_table(mark_position)
        end_turn_message = create_end_turn_message(updated_table, status)
        client_fd.sendall(end_turn_message.encode())
        if status != WRONG_MOVE:
            game_engine.update_active_player()
        time.sleep(1)
        if game_engine.is_game_finished():
            break
    send_final_message(client_fd, game_engine, client_turn)


# This function creates socket for server to listen and accept connections
def create_server_socket():
    s = socket.socket()
    print("Server socket has been created...")
    s.bind((HOST, SERVER_PORT))
    return s


# In the main body, we will create server sockets. Then, we will create a thread which just checks our waiting list.
# After that, in the main, we just check new connections and for each new connection, we will create
# new thread and will send them to game lobby
server_socket = create_server_socket()
server_socket.listen(5)
start_new_thread(check_waiting_lists, ())
while True:
    c, addr = server_socket.accept()
    print(f"Got connection from {addr}")
    start_new_thread(game_lobby, (c,))
