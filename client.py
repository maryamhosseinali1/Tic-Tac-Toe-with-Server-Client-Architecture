import socket

CUR_PLAYER_TURN_SIGN = '#'
END_GAME_SIGN = '$'

SERVER_PORT = 8080
HOST = '127.0.0.1'


# Here we will connect to server and wait for its acknowledgement.
def connect_to_server():
    server_socket = socket.socket()
    server_socket.connect(('127.0.0.1', SERVER_PORT))
    connection_confirmation_message = server_socket.recv(1024).decode()
    print(connection_confirmation_message)
    return server_socket


# Here we will get table size from plyer and send it to the server. We also wait for the server acknowledgement.
def set_table_size(server_socket):
    print("Choose your table size: ", end="")
    ts = int(input())
    server_socket.send(f'{ts}\n'.encode())
    table_size_confirmation = server_socket.recv(1024).decode()
    print(table_size_confirmation)
    return ts


# We first, connect to the server socket and then get table size from player wih standard input.
server_socket = connect_to_server()
table_size = set_table_size(server_socket)

# Here we will communicate with the server, to start a game.
print("Waiting for the game to start...")
loading_game_message = server_socket.recv(1024).decode()
print(loading_game_message)
start_game_message = server_socket.recv(1024).decode()
print(start_game_message)

# Here, in while loop, we will play the game. The player will wait until get activated and then
# chose their position which they want to be marked with their sign. Two players will player with each other, until
# one of them wins the game or draw.
while True:
    turn_ack_message = server_socket.recv(1024).decode()
    if END_GAME_SIGN in turn_ack_message:
        print(turn_ack_message[1:])
        break
    elif CUR_PLAYER_TURN_SIGN in turn_ack_message:
        print(turn_ack_message[1:])
        print("Enter the place you want to mark position X,Y:", end=" ")
        x, y = map(int, input().split())
        message = str((x - 1) * table_size + (y - 1)) + "\n"
        server_socket.send(message.encode())
        end_turn_message = server_socket.recv(1024).decode()
        print(end_turn_message)
    else:
        print(turn_ack_message)

server_socket.close()
