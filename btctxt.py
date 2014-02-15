#!/usr/bin/python

#import libraries
import sys
import os
import getpass
import ConfigParser
import urllib2
from BeautifulSoup import BeautifulSoup
import time
from email.mime.text import MIMEText
import smtplib


def main(path, from_address, user, pw, smtp, port, to_address, ratio, exchange, currency, buy_sell):
        #get current price
        web = urllib2.urlopen("http://bitcoinity.org/markets/" + exchange + "/" + currency).read()
        soup = BeautifulSoup(''.join(web))
        last = float(soup.find('span', id="last_" + buy_sell).string)
        #check last price
        checkLogExistence(path)
        logP = getLog(path)
        change = abs((logP-last)/last)
        if change > ratio:
                notify(last, currency, exchange, path, from_address, user, pw, smtp, port, to_address)
        return None


def notify(last, currency, exchange, path, from_address, user, pw, smtp, port, to_address):
        sendEmail(last, currency, exchange, from_address, user, pw, smtp, port, to_address)
        writeLog(last, path)
        return None


def sendEmail(last, currency, exchange, from_address, user, pw, smtp, port, to_address):
        #Format email_content
        timestr = time.strftime("%H:%M", time.localtime())
        email_content = "The price of BTC is currently " + str(last) + currency + " as of " + timestr + " on " + exchange + "."
        #Create msg
        msg = MIMEText(email_content)
        msg['Subject'] = "BTCtxt"
        msg['To'] = to_address
        msg['From'] = from_address
        #start server
        server = smtplib.SMTP(smtp + ":" + port)
        server.ehlo()
        server.starttls()
        #login
        server.login(user, pw)
        #send msg
        server.sendmail(from_address, [to_address], msg.as_string())
        server.quit
        return None


def writeLog(last, path):
        f = open(path, 'w')
        f.write(str(last))
        f.close()
        return None


def getLog(path):
        f = open(path, 'r')
        price = float(f.read())
        f.close()
        return price


def checkLogExistence(path):
        if not os.path.exists(path):
                f = file(path, 'w')
                f.write("1")
                f.close()
        return None


def getConf(path):
        parser = ConfigParser.RawConfigParser()
        parser.read(path)
        necessary = ["path", "smtp", "port", "to", "from"]
        optional = ["exchange", "currency", "buy_sell", "sleeptime", "sleeptime"]
        #check necessary
        if len(set(parser.options("Necessary"))) == 5:
                for item in necessary:
                        if item not in parser.options("Necessary"):
                                return False
        else:
                print "You've provided too many parameters in the [Necessary] section. Please include an entry for all of the following: path, smtp, port, to, from."
        #check optional
        if len(set(parser.options("Optional"))) <= 3:
                for item in optional:
                        if item not in parser.options("Optional"):
                                if item is "exchange":
                                        parser.set("Optional", item, "bitstamp")
                                elif item is "currency":
                                        parser.set("Optional", item, "USD")
                                elif item is "buy_sell":
                                        parser.set("Optional", item, "sell")
                                elif item is "sleeptime":
                                        parser.set("Optional", item, "180")
                                else:
                                        parser.set("Optional", item, "0.075")
        else:
                print "You've provided too many parameters in the [Optional] section of your .conf . Please include any subset of the following: exchange (bitstamp), sleeptime (180), ratio (0.075). If any argument is not included, the paranthetical default value will be used."
        return parser

if len(sys.argv) == 2:
        #read .conf
        parser = getConf(sys.argv[1])
        path = os.path.expanduser(parser.get("Necessary", "path"))
        from_address = parser.get("Necessary", "from")
        smtp = parser.get("Necessary", "smtp")
        port = parser.get("Necessary", "port")
        to_address = parser.get("Necessary", "to")
        ratio = float(parser.get("Optional", "ratio"))
        sleepTime = float(parser.get("Optional", "sleeptime"))
        exchange = parser.get("Optional", "exchange")
        currency = parser.get("Optional", "currency")
        buy_sell = parser.get("Optional", "buy_sell")
        #get user and pw from stdin
        user = raw_input("Username: ")
        pw = getpass.getpass()
elif len(sys.argv) == 3 and sys.argv[2] is "c":
        #read .conf
        parser = getConf(sys.argv[1])
        path = os.path.expanduser(parser.get("Necessary", "path"))
        from_address = parser.get("Necessary", "from")
        smtp = parser.get("Necessary", "smtp")
        port = parser.get("Necessary", "port")
        to_address = parser.get("Necessary", "to")
        ratio = float(parser.get("Optional", "ratio"))
        sleepTime = float(parser.get("Optional", "sleeptime"))
        exchange = parser.get("Optional", "exchange")
        currency = parser.get("Optional", "currency")
        buy_sell = parser.get("Optional", "buy_sell")
        user = parser.get("Credentials", "user")
        pw = parser.get("Credentials", "pw")
else:
        #read stdin
        path = sys.argv[1]
        from_address = sys.argv[2]
        user = sys.argv[3]
        pw = sys.argv[4]
        smtp = sys.argv[5]
        port = sys.argv[6]
        to_address = sys.argv[7]
        ratio = float(sys.argv[8])
        sleepTime = float(sys.argv[9])
        exchange = sys.argv[10]
        currency = sys.argv[11]
        buy_sell = sys.argv[12]
while True:
        main(path, from_address, user, pw, smtp, port, to_address, ratio, exchange, currency, buy_sell)
        time.sleep(sleepTime)
