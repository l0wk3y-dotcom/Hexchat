import socket
import click
import threading
import sys
usernames=[]
passwords=[]
def print_banner(name, description, line_char="*"):
    terminal_width = 80 
    line = line_char * terminal_width
    banner = f"{line}\n{name.center(terminal_width)}\n{description.center(terminal_width)}\n{line}"
    return banner

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


@click.group()
def cli():
    pass



@cli.command()
@click.option("--host","-h",prompt="host(e.g 192.168.1.1)",help="host to be connected at (e.g 192.168.1.1)")
@click.option("--port","-p",help="user preferenced port to be connected at(e.g 55555)",default=47821,type=int)
@click.option("--username","-un",prompt="Username(e.g 4doorsmorewhores)",help="username of the user")
@click.option("--password","-pw",prompt="password(e.g password)",help="password of the user")
def createuser(host,port,username,password):
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    s.send(username.encode('utf-8'))
    msg=s.recv(1024).decode('utf-8')
    while msg=='UA':
            username = input("Username already exists! \n Enter a new username:")
            s.send(username.encode('utf-8'))
            msg=s.recv(1024).decode('utf-8')
    if msg=='OK':
        s.send(password.encode('utf-8'))
        msg=s.recv(1024).decode('utf-8')
        if msg=='OK2':
            usernames.append(username)
            passwords.append(password)
            print(f'[*] user: {username} with password{password} have been created succesfully!')


def authenticate(username, password, socket):
    socket.send(username.encode('utf-8'))
    response = socket.recv(1024).decode('utf-8')

    if response == "CONTINUE":
        socket.send(password.encode('utf-8'))
        authentication_response = socket.recv(1024).decode('utf-8')

        if authentication_response == "ACCEPT":
            print("authentication completed")
            return True
        else:
            print("Authentication failed. Please check your username and password.")
            new_username = input("Enter your username again: ")
            return authenticate(new_username, password, socket)

    elif response == "BREAK":
        print("Username not recognized by the server. Use 'createuser' to register.")
        return False

    else:
        print(response)
        print("Unexpected response from the server. Check the server's configuration.")
        return False


@cli.command()
@click.option("-h","--host",help="ip address of the server to listen")
@click.option("-p","--port",help="desired port",default=55555)
@click.option("-u","--username",help="username")
@click.option("-pw","--password",help="password")
def joinchatT(username,password,host,port):
    exit=False
    join_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    join_socket.connect((host,port))
    def write():
        while True:            
            try:
                msg = input()
                if msg == "--exit":
                    join_socket.close()
                    print("Closed the socket")
                    exit=True
                    sys.exit()  # This line will close the program
                else:
                    chat = f"{username}:{msg}"
                    join_socket.send(chat.encode('utf-8'))
            except:
                break


    def read():
        while True:
            try:
                msg=join_socket.recv(1024).decode('utf-8')
                print(msg,"\n")
            except:
                print('An error occured while recieving from the server')
                join_socket.close()
                sys.exit()
                break
            
 
    if authenticate(username,password,join_socket):
        join_socket.send("START".encode('utf-8'))
        name=join_socket.recv(1024).decode('utf-8')
        join_socket.send(username.encode('utf-8'))
        description=join_socket.recv(1024).decode('utf-8')
        print("connected to the room....")

        banner=print_banner(name,description)
        print(banner)
        read_thread= threading.Thread(target=read) 
        read_thread.start()
        write_thread= threading.Thread(target=write)
        write_thread.start()
        read_thread.join()
        write_thread.join()
        sys.exit()
    else:
        print(f"you were not recognized by the server use 'createuser' command to register yourself to the'")
        print("lets try again!!")
if __name__ =='__main__':
    print_hexchat_banner()
    cli()