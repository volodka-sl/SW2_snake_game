import os
import socket
import threading

host = '127.0.0.1'
port = 8010

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []
engaged_cells = []


def check_free_space_for_turn(coordinates: tuple):
    if len(engaged_cells) == 0 or len(engaged_cells) == 1:
        return True
    cells_around = [(coordinates[0] + 1, coordinates[1]), (coordinates[0] - 1, coordinates[1]),
                    (coordinates[0], coordinates[1] + 1), (coordinates[0], coordinates[1] - 1)]

    is_free = False
    for cell in cells_around:
        if cell not in engaged_cells and cell[0] in range(0, 10) and cell[1] in range(0, 10):
            is_free = True

    if not is_free:
        return "GAMEOVER"

    prev_coords = engaged_cells[len(engaged_cells) - 2]
    new_cells = [(prev_coords[0] + 1, prev_coords[1]), (prev_coords[0] - 1, prev_coords[1]),
                 (prev_coords[0], prev_coords[1] + 1), (prev_coords[0], prev_coords[1] - 1)]
    filtered_new_cells = [i for i in new_cells if
                          i[0] in range(0, 10) and i[1] in range(0, 10) and i not in engaged_cells]
    if len(filtered_new_cells) == 1 and not is_free:
        return "GAMEOVER"
    if coordinates in filtered_new_cells:
        return True
    return False


def broadcast(message):
    for client in clients:
        client.send(message.encode('ascii'))


def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == "HOWMANYNICKNAMES":
                broadcast(f"{nicknames[0]},{nicknames[1]}")
            elif len(message) == 3:
                engaged_cell = tuple(int(i) for i in message if i != ',')
                if check_free_space_for_turn(engaged_cell):
                    if check_free_space_for_turn(engaged_cell) == "GAMEOVER":
                        if len(engaged_cells) % 2 == 0:
                            broadcast(f"GAME OVER,{nicknames[1]}")
                        else:
                            broadcast(f"GAME OVER,{nicknames[0]}")
                    else:
                        engaged_cells.append(engaged_cell)
                        broadcast(message)
                else:
                    broadcast("Hm, it seems it is impossible to choose this cell :(\nTry again!")
            else:
                broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f"{nickname} left!")
            nicknames.remove(nickname)
            break


def receive():
    while True:
        client, address = server.accept()
        clients.append(client)

        message = client.recv(1024).decode('ascii')
        nicknames.append(message[4:])
        broadcast(f"Player {len(clients)} '{message[4:]}' connected.")

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


os.system('clear')
receive()
