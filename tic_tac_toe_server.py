import tkinter as tk
import socket
import threading
from time import sleep
import random


window = tk.Tk()
window.title("Tic-Tac-Toe Server")

# Top frame yang terdiri dari button start dan stop
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Start", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

# Middle frame yang terdiri dari dua label untuk menampilkan host dan port info
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Address: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

# Client Frame
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="**********Client List**********").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=10, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


server = None
HOST_ADDR = "192.168.0.105"
HOST_PORT = 8080
client_name = " "
clients = []
clients_names = []
player_data = []


# Fungsi start server
def start_server():
    global server, HOST_ADDR, HOST_PORT # code is fine without this
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  # server is listening for client connection

    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Address: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)


# fungsi start server
def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)


def accept_clients(the_server, y):
    while True:
        if len(clients) < 2:
            client, addr = the_server.accept()
            clients.append(client)

            # menggunakan thread agar tidak menghambat gui thread
            threading._start_new_thread(send_receive_client_message, (client, addr))


# Fungsi untuk menerima pesan dari klien saat ini dan
# mengirim pesan ke klien lain
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, player_data, player0, player1

    client_msg = " "

    # mengirim pesan "welcome" ke klien
    client_name = client_connection.recv(4096).decode()

    if len(clients) < 2:
        client_connection.send("welcome1".encode())
    else:
        client_connection.send("welcome2".encode())

    clients_names.append(client_name)
    update_client_names_display(clients_names)  # memperbarui display nama klien

    if len(clients) > 1:
        sleep(1)
        symbols = ["O", "X"]

        # mengirim nama dan simbol lawan
        out1 = "opponent_name$" + clients_names[1] + "symbol" + symbols[0]
        out2 = "opponent_name$" + clients_names[0] + "symbol" + symbols[1]
        clients[0].send(out1.encode())
        clients[1].send(out2.encode())


    while True:

        # mendapatkan pilihan pemain dari data yang diterima
        data = client_connection.recv(4096).decode()
        if not data: break

        # data koordinat pemain (x,y). dikirimkan ke pemain lain
        if data.startswith("$xy$"):
            # memeriksa apakah pesan dari klien1 atau klien2
            if client_connection == clients[0]:
                # mengirim data dari klien satu ke klien lainnya
                clients[1].send(data.encode())
            else:
                # mengirim data dari klien satu ke klien lainnya
                clients[0].send(data.encode())

    # temukan indeks klien lalu hapus dari kedua daftar (daftar nama klien dan daftar koneksi)
    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    client_connection.close()

    update_client_names_display(clients_names)  # memperbarui display nama klien


# Kembalikan indeks klien saat ini dalam daftar klien
def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx


# Perbarui tampilan nama klien saat klien baru terhubung atau
# Saat koneksi klien saat ini terputus
def update_client_names_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c+"\n")
    tkDisplay.config(state=tk.DISABLED)


window.mainloop()