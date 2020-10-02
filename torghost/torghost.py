#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import getopt
from requests import get
import subprocess
import time
import signal
from stem import Signal
from stem.control import Controller
from packaging import version

VERSION = "3.1.1"

IP_API = "https://api.ipify.org/?format=json"

LATEST_RELEASE_API = "https://api.github.com/repos/SusmithKrishnan/torghost/releases/latest"


class bcolors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[31m'
    YELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BGRED = '\033[41m'
    WHITE = '\033[37m'


def t():
    current_time = time.localtime()
    ctime = time.strftime('%H:%M:%S', current_time)
    return '[' + ctime + ']'


def sigint_handler(signum, frame):
    stop_torghost()


def ip():
    while True:
        try:
            jsonRes = get(IP_API).json()
            ipTxt = jsonRes["ip"]
        except:
            continue
        break
    return ipTxt



signal.signal(signal.SIGINT, sigint_handler)

TorrcCfgString = \
    """
VirtualAddrNetwork 10.0.0.0/10
AutomapHostsOnResolve 1
TransPort 9040
DNSPort 5353
ControlPort 9051
RunAsDaemon 1
"""

resolvString = 'nameserver 127.0.0.1'

Torrc = '/etc/tor/torghostrc'
resolv = '/etc/resolv.conf'


def start_torghost():
    os.system('sudo cp /etc/resolv.conf /etc/resolv.conf.bak')
    if os.path.exists(Torrc) and TorrcCfgString in open(Torrc).read():
        pass
    else:
        with open(Torrc, 'w') as myfile:
            myfile.write(TorrcCfgString)
    if resolvString in open(resolv).read():
        pass
    else:
        with open(resolv, 'w') as myfile:
            myfile.write(resolvString)

    os.system('sudo service tor stop')
    os.system('sudo fuser -k 9051/tcp > /dev/null 2>&1')
    os.system('sudo -u debian-tor tor -f /etc/tor/torghostrc > /dev/null'
              )

    iptables_rules = \
        """
	NON_TOR="192.168.1.0/24 192.168.0.0/24"
	TOR_UID=%s
	TRANS_PORT="9040"

	iptables -F
	iptables -t nat -F

	iptables -t nat -A OUTPUT -m owner --uid-owner $TOR_UID -j RETURN
	iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports 5353
	for NET in $NON_TOR 127.0.0.0/9 127.128.0.0/10; do
	 iptables -t nat -A OUTPUT -d $NET -j RETURN
	done
	iptables -t nat -A OUTPUT -p tcp --syn -j REDIRECT --to-ports $TRANS_PORT

	iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
	for NET in $NON_TOR 127.0.0.0/8; do
	 iptables -A OUTPUT -d $NET -j ACCEPT
	done
	iptables -A OUTPUT -m owner --uid-owner $TOR_UID -j ACCEPT
	iptables -A OUTPUT -j REJECT
	""" \
        % subprocess.getoutput('id -ur debian-tor')

    os.system(iptables_rules)
    print(t() + ' CURRENT IP : ' + bcolors.GREEN + ip() + bcolors.ENDC)


def stop_torghost():
    os.system('mv /etc/resolv.conf.bak /etc/resolv.conf')
    IpFlush = \
        """
	iptables -P INPUT ACCEPT
	iptables -P FORWARD ACCEPT
	iptables -P OUTPUT ACCEPT
	iptables -t nat -F
	iptables -t mangle -F
	iptables -F
	iptables -X
	"""
    os.system(IpFlush)
    os.system('sudo fuser -k 9051/tcp > /dev/null 2>&1')
    os.system('service network-manager restart')
    time.sleep(3)
    print(t() + ' CURRENT IP : ' + bcolors.GREEN + ip() + bcolors.ENDC)


def switch_tor():
    time.sleep(7)
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
    print(t() + ' CURRENT IP : ' + bcolors.GREEN + ip() + bcolors.ENDC)


def main():
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'srxhu', [
            'start', 'stop', 'switch', 'help'])
    except (getopt.GetoptError):
        sys.exit(2)
    for (o, a) in opts:
        if o in ('-s', '--start'):
            start_torghost()
        elif o in ('-x', '--stop'):
            stop_torghost()
        elif o in ('-r', '--switch'):
            switch_tor()


if __name__ == '__main__':
    main()
