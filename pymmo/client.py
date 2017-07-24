import select
import socket
import sys

from pymmo import encoding


class ClientNotConnected(Exception):
    def __init__(self):
        pass


class Client(object):

    sock = -1
    inputdata = ""
    outputdata = ""
    listener = None
    address = ""

    def __init__(self, name, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((name, port))
        self.address = str(self.sock.getpeername())

    def output(self, command):
        if not self.isopen():
            raise ClientNotConnected()
        if not command.endswith("\n"):
            command += "\n"
        self.outputdata += command

    def step(self):
        if not self.isopen():
            raise ClientNotConnected()
        socketlist = [self.sock]
        readable, writable, error = select.select(socketlist, socketlist, socketlist, 0)
        if readable:
            r = str(self.sock.recv(2048))
            self.inputdata += r
            if not len(r):
                error.append(socketlist)
        if writable:
            n = self.sock.send(bytes(self.outputdata, 'ASCII'))
            if n < 1:
                error.append(socketlist)
            else:
                self.outputdata = self.outputdata[n:]
        if error:
            self.sock.close()
            self.sock = -1
        while 1:
            x = self.inputdata.partition("\n")
            if x[1]:
                self.inputdata = x[2]
                if self.listener:
                    self.listener.do_command(x[0])
                else:
                    print("no listener, received command " + x[0])
            else:
                break
        return 1

    def isopen(self):
        return self.sock != -1

    def command(self, cmd):
        if not cmd.endswith("\n"):
            cmd += "\n"
        self.outputdata += cmd

    def close(self):
        if self.isopen():
            self.sock.close()
            self.sock = -1

    def moveto(self, pos):
        self.command("mov " + str(pos[0]) + "," + str(pos[1]) + "," + str(pos[2]))

    def connect(self, name, pw):
        self.command("con " + encoding.enquote(name) + "," + encoding.enquote(pw))

    def idle(self):
        self.command("idl")

    def say(self, text):
        self.command("say " + encoding.enquote(text))


def main(args=None):
    if args is None:
        args = sys.argv
    name = "localhost"
    port = "7755"
    if len(args) > 1:
        name = args[1]
    if len(args) > 2:
        port = args[2]
    if len(args) > 3:
        print("Warning: extra arguments ignored")
    port = int(port)
    if (port < 1) or (port > 65535):
        print("port " + str(port) + " out of range (1-65535)")
        return 1
    client = Client(name, port)
    while 1:
        line = input("> ")
        if not line:
            print("end of input")
            break
        if not client.isopen():
            print("connection closed")
            return 1
        client.output(line.strip())
        client.step()
    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

