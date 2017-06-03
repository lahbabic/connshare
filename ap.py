#!/usr/bin/env python
#-*- coding: utf-8 -*-


#################[Libs]#################

from __future__ import print_function
import os, sys, subprocess



	
#################[Vars]#################

needed_binarys = [
                    ['hostapd',False],
                    ['iptables-persistent',False],
                    ['isc-dhcp-server',False],
                 ]
ipv4forward = "/proc/sys/net/ipv4/ip_forward"



#################[Colors]#################

W = '\033[0m'   # white 
R = '\033[31m'  # red
G = '\033[32m'  # green













def print_ok():
    print(W+"["+G+"OK"+W+"]")
def print_err():
    print(W+"["+R+"error"+W+"]")


