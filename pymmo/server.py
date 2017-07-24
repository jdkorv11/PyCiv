import os
import pickle
import select
import socket
import sys
import time

import player
import world

from pymmo import encoding


def unload(name):
    try:
        del (sys.modules[name])
        del (globals()[name])
    except:
        print(name + " wasn't a loaded module")


try:
    sys.path.index(".")
except:
    sys.path.insert(0, ".")

CURRENT_PROTOCOL_VERSION = 1

acceptSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
acceptSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
acceptSocket.bind(("0.0.0.0", 7755))
acceptSocket.listen(10)

socks = {acceptSocket}
clients = {}


class Notifier(object):
    @staticmethod
    def add_entity(entity):
        global clients
        command = "add " + str(entity.id) + "," + entity.getrep() + "\n"
        for client in clients.values():
            if client and client.entity:
                client.output(command)

    @staticmethod
    def remove_entity(entity):
        global clients
        for client in clients.values():
            if client and client.entity:
                client.output("del " + str(entity.id) + "\n")

    @staticmethod
    def command(command):
        global clients
        for client in clients.values():
            if client and client.entity:
                client.output(command)


# make sure to notify everyone
world.notify = Notifier()

start = time.clock()
now = start
last = now - 1


class Client(object):
    inputdata = ""
    outputdata = ""
    entity = None
    sock = -1
    state = 0
    lastcommand = 0
    address = "unknown"
    commands = None
    userData = {}
    name = None
    init = 0

    def __init__(self, sock):
        global clients
        global socks
        global now
        self.address = str(sock.getpeername())
        print("New connection from " + self.address)
        self.sock = sock
        clients[sock] = self
        socks.update((sock,))
        self.commands = {"con": Client.cmd_connect}
        self.lastcommand = now
        self.init = now

    def step(self):
        global now
        #   attempt to parse input data
        while 1:
            t = self.inputdata.partition("\\n")
            if t[1] == "":
                break
            self.do_command(t[0])
            self.inputdata = t[2]
        # time out unresponsive clients
        if now - self.lastcommand > 1500:  # TODO put back to normal timeout
            print("Closing unresponsive client " + self.address)
            self.close()
        elif len(self.inputdata) > 1024:
            print("Client sent too large command: " + self.address)
            self.close()
        elif len(self.outputdata) > 8192 and self.init < now - 30:
            # the first 30 seconds are allowed to use more data
            print("Client is too laggy: " + self.address)
            self.close()

    def do_command(self, cmd):
        global now
        self.lastcommand = now
        cmd3 = cmd[:3]
        if len(cmd) < 3:
            print("short command from " + self.address + ": " + cmd)
        elif cmd3 == "bye":
            print("player requests close: " + self.name + " at " + self.address)
            self.close()
        elif self.entity:
            self.entity.docmd(cmd)
        elif cmd3 in self.commands:
            (self.commands[cmd3])(self, cmd[4:])
        else:
            print("unknown command from " + self.address + ": " + cmd)

    def output(self, data_string):
        if not data_string.endswith("\n"):
            data_string += "\n"
        self.outputdata += data_string

    def close(self):
        global socks
        global clients
        print("Closing connection " + self.address)
        if self.entity:
            self.save_to_file()
            self.entity.die()
        socks.difference_update((self.sock,))
        del (clients[self.sock])
        self.sock.close()

    def save_to_file(self):
        try:
            if self.entity:
                self.userData["entityrep"] = self.entity.getrep()
            file = open("user/" + self.name + ".tmp", "wb")
            pickle.dump(self.userData, file)
            file.close()
            os.unlink("user/" + self.name)
            os.rename("user/" + self.name + ".tmp", "user/" + self.name)
        except Exception as x:
            print("Could not save user to file: user/" + self.name + ".tmp: " + str(x))

    def cmd_connect(self, args):
        global CURRENT_PROTOCOL_VERSION
        arguments = args.split(',')
        if len(arguments) != 3:
            print("mal-formatted connect command from " + self.address + ": " + args)
            return
        self.name = encoding.safefilename(encoding.dequote(arguments[0]))
        password = encoding.dequote(arguments[1])
        protocol = int(arguments[2])
        if protocol != CURRENT_PROTOCOL_VERSION:
            print("bad version in connect from " + self.address + ": " + arguments[2])
            return
        ok = 0
        try:
            file = None
            try:
                file = open("user/" + self.name, "rb")
            except:
                pass
            if not file:
                # look for a back-up file, if we died while trying a rename() operation
                file = open("user/" + self.name + ".tmp", "rb")
            self.userData = pickle.load(file)
            file.close()
            ok = (self.userData["password"] == password)
        except Exception as x:
            print("User file open exception " + str(x) + " on file " + self.name)
        if ok:
            self.entity = player.Player(self.userData["entityrep"])
            self.userData["lastlogin"] = time.strftime("%Y-%m-%d %H:%M:%S")
            self.output("ok! " + str(self.entity.id) + "\n")
            self.save_to_file()
            world.dumpentities(self)
        else:
            self.output("fai " + encoding.enquote(self.name) + "\n")

    def dump_entity(self, ent):
        cmd = "add " + str(ent.id) + "," + ent.getrep() + "\n"
        self.output(cmd)


def has_data(client):
    return client.outputdata


def get_sock(client):
    return client.sock


def main():
    global now
    global last
    global socks
    global clients
    global start

    os.chdir("data")

    while 1:
        #   poll 20 times a second
        try:
            client_socket_list = list(socks)
            wr = map(get_sock, filter(has_data, clients.values()))
            readable, writable, errors = select.select(client_socket_list, wr, client_socket_list, 0.05)
        except:
            print("select() exception, sockets " + str(socks))
            raise
        now = time.clock()
        delta = now - last

        #  deal with sending output queue
        for sock in writable:
            try:
                if sock in clients:
                    client = clients[sock]
                    if client.outputdata:
                        sent = sock.send(bytes(client.outputdata, 'ASCII'))
                        if sent == 0:
                            print("Nothing sent on socket " + str(sock))
                            errors.append(sock)
                        else:
                            client.outputdata = client.outputdata[sent:]
            except Exception as x:
                print("Socket write exception: " + str(x))
                errors.append(sock)

        # deal with reading input queue
        for sock in readable:
            try:
                if sock in clients:
                    client = clients[sock]
                    client.inputdata += str(sock.recv(2048))
                else:
                    a = sock.accept()[0]
                    client = Client(a)
            except Exception as x:
                print("Socket read exception: " + str(x))
                errors.append(sock)

        # deal with errors
        for sock in errors:
            try:
                client = clients[sock]
                if client:
                    client.close()
                else:
                    print("Accept socket failed: I'm screwed!")
                    os.abort()
            except:
                pass

        # step clients
        for client in list(clients.values()):
            if client:
                client.step()

        # step world 10 times a second
        while delta >= 0.1:
            world.step()
            delta -= 0.1
            last += 0.1


if __name__ == "__main__":
    main()
