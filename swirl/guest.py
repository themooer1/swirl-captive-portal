from pyrad import dictionary, packet, server
from flask import Flask, render_template
from flask_ask import Ask, statement
from functools import reduce
import time
from threading import Thread
import random
import os


SHARED_SECRET = b"ol7t623m09ipN"
VOUCHER_LEN = 4
WIFI_SPOKEN_NAME = "Guest WiFi"

if 'radius_secret' in os.environ:
    SHARED_SECRET = os.environ['radius_secret'].encode()

if 'token_length' in os.environ:
    VOUCHER_LEN = int(os.environ['token_length'])

if 'network_name' in os.environ:
    WIFI_SPOKEN_NAME = os.environ['network_name']


with open("google-10000-english-no-swears.txt", 'r') as fp:
    words = fp.read().split("\n")

app = Flask(__name__)
ask = Ask(app, '/')

@app.route('/hello')
def hi():
    return "hello world"


class Voucher:
    def __init__(self, TTL = 1800, LENGTH = VOUCHER_LEN):
        self.genTime = int(time.time())
        self.TTL = TTL
        self.code = random.choice(words)
        if LENGTH > 1:
            self.code += " "
            for i in range(1, LENGTH - 1):
                self.code += random.choice(words) + " "
            self.code += random.choice(words)

    def expired(self):
        return (time.time() - self.genTime) > self.TTL

    def __str__(self):
        return self.code

    def __eq__(self, other):
        if self is other:
            return True
        elif type(self) != type(other):
            return False
        else:
            return self.genTime == other.genTime and self.TTL == other.TTL and self.code == other.code

    def authenticate(self, code:str):
        return self.code.lower() == code.lower()


class GuestServer(server.Server):
    t = Thread()
    vouchers = list()  # type: list[Voucher]

    @staticmethod
    def start():
        def runServer():
            srv = GuestServer(addresses=['0.0.0.0'], dict=dictionary.Dictionary("dictionary"))
            srv.hosts["127.0.0.1"] = server.RemoteHost("127.0.0.1", SHARED_SECRET, "localhost")
            srv.hosts["192.168.1.1"] = server.RemoteHost("192.168.1.1", SHARED_SECRET, "pfsense")
            srv.Run()


        GuestServer.t = Thread(target=runServer)
        GuestServer.t.start()
        print("RADIUS Server running.")

    @staticmethod
    def removeExpiredVouchers():
        for v in GuestServer.vouchers:
            if v.expired():
                GuestServer.vouchers.remove(v)


    def HandleAcctPacket(self, pkt:packet.AcctPacket):
        print("Acct request: ")
        print(pkt)
        for attr in pkt.keys():
            print("%s: %s" % (attr, pkt[attr]))

    def HandleAuthPacket(self:server.Server, pkt:packet.AuthPacket):
        print(vars())
        print("Auth request: ")
        print(pkt)
        reply = self.CreateReplyPacket(pkt, **{"Service-Type": "Framed-User", "Framed-IP-Address": pkt['Framed-IP-Address'][0]})  # type: packet.AuthPacket
        print(dir(reply))
        reply.code = packet.AccessReject
        for attr in pkt.keys():
            print("%s: %s" % (attr, pkt[attr]))
        if "User-Password" in pkt.keys():

            print("Checking Password")
            print(pkt.secret)
            pkt.dict
            passwd = pkt.PwDecrypt(pkt.get(2)[0])
            print(passwd)
            # Remove expired vouchers before authenticating
            GuestServer.removeExpiredVouchers()
            # Auth against current tokens
            print(list(map(lambda v: str(v), GuestServer.vouchers)))
            if GuestServer.vouchers and reduce(lambda a, b: a or b, map(lambda v: v.authenticate(passwd), GuestServer.vouchers)):
                print("Auth Success")
                reply.code = packet.AccessAccept
            else:
                print("Auth Failed")
        self.SendReplyPacket(pkt.fd, reply)


@ask.launch
def welcome():
    return statement(render_template('welcome', SSID=WIFI_SPOKEN_NAME))


@ask.intent('generateVoucherIntent')
def genVoucher():
    GuestServer.removeExpiredVouchers()
    v = Voucher(LENGTH=2)
    GuestServer.vouchers.append(v)
    return statement(render_template('voucher', SSID=WIFI_SPOKEN_NAME, voucher=v))

def testVoucher():
    GuestServer.removeExpiredVouchers()
    v = Voucher(LENGTH=1)
    GuestServer.vouchers.append(v)
    return v

def main():
    GuestServer.start()
    print(testVoucher())
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    main()