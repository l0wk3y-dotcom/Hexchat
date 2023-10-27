import socket
import click
import threading
import sys
import json
import os
file_name="log.txt"
if not os.path.exists(file_name):
    print("creating the file")
    with open(file_name,'w') as f:
        print("created the file")
        initial_data=[]
        json.dump(initial_data, f)
with open(file_name, 'r') as u:
    users=json.load(u)
@click.group()
def cli():
    pass
def print_hexchat_banner():
    banner = r"""
     ██░ ██ ▓█████ ▒██   ██▒ ▄████▄   ██░ ██  ▄▄▄     ▄▄▄█████▓
    ▓██░ ██▒▓█   ▀ ▒▒ █ █ ▒░▒██▀ ▀█  ▓██░ ██▒▒████▄   ▓  ██▒ ▓▒
    ▒██▀▀██░▒███   ░░  █   ░▒▓█    ▄ ▒██▀▀██░▒██  ▀█▄ ▒ ▓██░ ▒░
    ░▓█ ░██ ▒▓█  ▄  ░ █ █ ▒ ▒▓▓▄ ▄██▒░▓█ ░██ ░██▄▄▄▄██░ ▓██▓ ░
    ░▓█▒░██▓░▒████▒▒██▒ ▒██▒▒ ▓███▀ ░░▓█▒░██▓ ▓█   ▓██▒ ▒██▒ ░
    ▒ ░░▒░▒░░ ▒░ ░▒▒ ░ ░▓ ░░ ░▒ ▒  ░ ▒ ░░▒░▒ ▒▒   ▓▒█░ ▒ ░░
    ▒ ░▒░ ░ ░ ░  ░░░   ░▒ ░  ░  ▒    ▒ ░▒░ ░  ▒   ▒▒ ░   ░
    ░  ░░ ░   ░    ░    ░  ░         ░  ░░ ░  ░   ▒    ░
    ░  ░  ░   ░  ░ ░    ░  ░ ░       ░  ░  ░      ░  ░

    Welcome to HexChat - The tool for secure and fast TCP transfer
    """
    print(banner)
@cli.command()
@click.option("--host","-h",prompt="host(e.g 192.168.1.1)")
@click.option("--port","-p",default=47821,type=int,help="Port to listen for requests")
def acceptnewusers(host,port):
    with open(file_name,'r') as f:
        users=json.load(f)
    def GetUser(host):
        try:
            username=host.recv(1024).decode('utf-8')
            for user in users:
                if user['username']!=username:
                    continue
                else:
                    host.send("UA".encode('utf-8'))
                    GetUser(host)
                    return                 
            host.send("OK".encode('utf-8'))
            print(f"username recieved going for passowrd")
            password=host.recv(1024).decode('utf-8')
            host.send("OK2".encode('utf-8'))
            print("password recieved as well adding to the users..")
            user ={
                'username':username,
                'password':password
            }
            users.append(user)
            print(f"created a user from {host} with username:{username} and password:{password} \n press 'ctrl+c' to save the new users and exit the program")
        except:
            print("[!]could not fetch username didn't even try for passowrd check the instructions to look for reason")

    def ListenNewUsers(host,port):
            try:
                s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.bind((host,port))
                s.listen()
                print("listening......")
                while True:
                    try:
                        host,address=s.accept()
                        print(f"request accepted from {address} fetching username and password...")
                        thread =threading.Thread(target=GetUser,args=(host,))
                        thread.start()
                    except KeyboardInterrupt:
                        print("[*] keyboardinterrupt closing the socket(done) \n exiting the program(done)")
                        with open(file_name , 'w') as f:
                            json.dump(users, f)
                        s.close()
                        sys.exit(0)
            except Exception as e:
                print(f'error {e}')
    ListenNewUsers(host,port)

def authenticate(client,chat_socket):
    username = client.recv(1024).decode('utf-8')
    
    found_user = None
    for user in users:
        if user['username'] == username:
            found_user = user
            break
    
    if found_user:
        print("user found")
        client.send("CONTINUE".encode('utf-8'))
        password = client.recv(1024).decode('utf-8')
        if password == found_user['password']:
            client.send("ACCEPT".encode('utf-8'))
            return True
        else:
            client.send("AUTHENTICATION_FAILED".encode('utf-8'))
            return False
    else:
        print("couldn't find user")
        client.send("BREAK".encode('utf-8'))
        print(f"Connection attempt from {host} with username: {username} which was not registered.")
        return False
def broadcast(msg,clients,client):
    for user in clients:
            if client != user:
                try:
                    user.send(msg.encode('utf-8'))
                except:
                    clients.remove(user)
    print(f"broadcasted {msg}")
def handle(client,clients,name,description,username):
    broadcast(f"{username} joined the chat", clients, client)
    while True:
        try:
            msg=client.recv(1024).decode('utf-8')
            if msg:
                print("trying to broadcast")
                broadcast(msg,clients,client)
                print("broadcasted message")
            else:
                broadcast(f"{client} as {username} left the chat", clients, client)
                clients.remove()
                client.close()
                break
        except:
            clients.remove(client)
            broadcast(f"{username} left the chat", clients, client)
            break
@cli.command()
@click.option("-h","--host",help="ip address of the server to listen")
@click.option("-p","--port",help="desired port",default=55555)
@click.option("-n","--name",help="Name of the room",prompt="Name")
@click.option("-d","--description",help="description of the room",prompt="Description")
def startchat(host, port, name, description):
    with open(file_name,'r') as f:
        users=json.load(f)
    print("Starting a chat room...")
    clients = []
    chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    chat_socket.bind((host, port))
    chat_socket.listen()
    print(f"Chat room '{name}' is now listening on {host}:{port}")
    
    while True:
        try:
            client, address = chat_socket.accept()
            if authenticate(client, chat_socket):
                per=client.recv(1024).decode('utf-8')
                client.send(f"{name}".encode('utf-8'))
                username=client.recv(1024).decode('utf-8')
                print(username)
                client.send(f"{description}".encode('utf-8'))
                clients.append(client)
                client_thread = threading.Thread(target=handle, args=(client,clients,name,description,username))
                client_thread.start()
                
                print(f"Client connected from {address}")
            else:
                print("Authentication failed for a client.")
        except Exception as e:
            print("An error occurred while handling a client connection.")
            print(f"Error: {e}")
            sys.exit(0)

if __name__ =='__main__':

    print_hexchat_banner()
    cli()