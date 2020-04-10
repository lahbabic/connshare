#!/usr/bin/env python
#-*- coding: utf-8 -*-


#################[Libs]#################

from __future__ import print_function
import os, sys, subprocess, re, time



	
#################[Vars]#################

needed_binarys = [
                    ['hostapd',False],
                    ['netfilter-persistent',False],
                    ['rfkill',False]
          	 ]
needed_deamons = [
		    ['isc-dhcp-server',False]		    
		 ]
ipv4forward = "/proc/sys/net/ipv4/ip_forward"



#################[Colors]#################

W = '\033[0m'   # white 
R = '\033[31m'  # red
G = '\033[32m'  # green
B = '\033[34m'  # blue
GR = '\033[37m' # gray



def check_for_strings_value(list_of_value=[]):
    for elem in list_of_value:
        if not isinstance(elem, str):
            return False
    return True 

def print_ok():
    print(W+"["+G+"OK"+W+"]")
def print_no():
     print(W+"["+B+"NO"+W+"]")
def print_err():
    print(W+"["+R+"error"+W+"]")
def print_timeout():
    print(W+"["+O+"Timeout"+W+"]")
def print_info(string):
    formated_print(string,align="^",fchar="\n",lchar="\n\n")

def formated_print(string='',length='60',char='.',lchar='\n',fchar="",color=GR,align="<"):
    if not check_for_strings_value([string,length,char,lchar]):
        sys.exit("\n\n"+R+"formated_print should only get strings as input!"+W)
    the_format = "{0:%s%s%s.%s}" % (char,align,length,length)
    print(color+fchar+the_format.format(string)+W,end=lchar)

def check_for_linux():
    formated_print('cheking if it is run on linux',lchar="")
    if sys.platform == "linux" or sys.platform == "linux2":
        print_ok()
    else:
        print_err()
        sys.exit(1)
        

def check_for_root():
	formated_print('cheking if it is run as root',lchar="")
	if not os.geteuid() == 0:
	    print_err()
	    sys.exit(1)
	print_ok()

def check_for_binarys(binarys_array=[]):
    if not isinstance(binarys_array,list):
        sys.exit("\n\n"+R+"binary array should only be a list"+W)
    paths = os.environ["PATH"].split(':') #Tous les répertoires contenant des executables.
    for needed_binary in binarys_array:
        for path in paths:
            if os.path.isfile(path+'/'+needed_binary[0]):
                needed_binary[1] = True

    for needed_binary in binarys_array:
        formated_print('cheking if '+needed_binary[0]+" is installed",lchar="")
        if not needed_binary[1]:
            print(W+"["+R+"NO"+W+"]")
            sys.exit(1)
        print_ok()

def check_for_deamons(deamons_array=[]):
    if not isinstance(deamons_array,list):
	   sys.exit("\n\n"+R+"deamon array should only be a list"+W)

    for needed_deamon in deamons_array:
        stdout1, stderr, rcode = runcommand_with_timeout(["systemctl","status", needed_deamon[0]])
        stdout, stderr, rcode = runcommand_with_timeout(["grep", "-u", "-w", "Loaded:"],"3", stdout1)
        stdout, stderr, rcode = runcommand_with_timeout(["cut", "-d"," ", "-f", "5"], "3", stdout)
        formated_print('cheking if '+needed_deamon[0]+" is installed and running",lchar="")
        if(stdout == "loaded\n"):
            needed_deamon[1] = True
            print_ok()
        elif(stdout == "not-found\n"):
            print_err()
            sys.exit(1)



def check_file_exist_and_is_writeateble(file_path=""):
    name = file_path.split('/')[-1] #getting the last element of the file_path
    formated_print('cheking if '+name+' exist',lchar="")
    if not os.path.isfile(file_path):
        print_err()
        sys.exit(1)
    print_ok()
    try:
        formated_print('cheking if '+name+' is writeable',lchar="")
        file = open(file_path, "w")
        file.close()
        print_ok()
    except:
        print_err()
        sys.exit(1)


def runcommand_with_timeout(command=[],timeout="3",stdIN=""):
    if not isinstance(command,list):
        sys.exit("\n\n"+R+"comands are ment to be a list"+W)
    formated_print('running '+' '.join(command)+" ",lchar="",color=B)
    command[:0] = ["timeout",timeout]
    proc = subprocess.Popen(command, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate(input=b''+stdIN)
    if proc.returncode == 124:
        print_timeout()
    elif proc.returncode == 0:
        print_ok()
    elif proc.returncode == 3:
        print_ok()
    else:
    	print(proc.returncode)
        print_err()
        sys.exit()
    return stdout, stderr, proc.returncode

def get_gateways():
    print_info("Gathering network info")
    stdout, stderr, rcode = runcommand_with_timeout(["hostname", "-I"])
    if rcode != 0:
        sys.exit("\n\n"+R+"Warning! could not run netstat, exiting..."+W)
    ip_patern = re.compile(ipv4_regex)
    for elem in stdout.split("\n"):
        if len(elem) == 0: continue
        tmp = elem.strip()
        test = ip_patern.match(tmp.strip())
        if test:
           print("Acceptable ip address")
        else:
           print("Unacceptable ip address")
        
def get_interfaces():
    interfaces = []
    print_info("Getting available interfaces")
    stdout, stderr, rcode = runcommand_with_timeout(["ip", "link", "show"])
    stdout, stderr, rcode = runcommand_with_timeout(["grep", " "], "3", stdout)
    stdout, stderr, rcode = runcommand_with_timeout(["sort"], "3", stdout)
    lines = stdout.split('\n')
    for line in lines:
        pattern = line.split(': ')
        if pattern[0].isdigit() and pattern[1] != "lo":
            interfaces.append(pattern[1])
    return interfaces

def get_int(tmp):
	valid = 0
	while not valid:
		try:
			choice = int( raw_input(tmp) 	)
			valid = 1
		except ValueError, e:
			print("%s is not valid integer" % e.args[0].split(": ")[1])
		except EOFError, e:
			sys.exit("\nExiting ...")
	return choice

def checking_functions():
    print("Cheking for requirements")
    check_for_linux()
    check_for_root()
    check_for_binarys(needed_binarys)
    check_for_deamons(needed_deamons)
    check_file_exist_and_is_writeateble(ipv4forward)

def setup_dhcp_ap(inter):
	print("\n\nNext, to setup the dhcp server, you need to edit as root the file /etc/dhcp/dhcpd.conf\n")
	print("Find the lines that say:\n")
	print("\toption domain-name \"example.org\";")
	print("\toption domain-name-servers ns1.example.org, ns2.example.org;\n")
	print("and comment them with # in the beginning of each line\n")
	raw_input('Press enter to continue: \n')

	print("now you have to find out the one that say: #authoritative;\n")
	print("\t and remove the # from the beginning of the line\n")
	raw_input('Press enter to continue: \n')

	print("next append to the end of the file the following: \n")
	print("subnet 192.168.1.0 netmask 255.255.255.0 {\n\
range 192.168.1.10 192.168.1.50;\n\
option broadcast-address 192.168.1.255;\n\
option routers 192.168.1.1;\n\
default-lease-time 600;\n\
max-lease-time 7200;\n\
option domain-name \"local\";\n\
option domain-name-servers 8.8.8.8, 8.8.4.4;\n\
}")
	raw_input('Press enter to continue: \n')

	print(G+"Save the file"+W)
	print("Edit as root the file /etc/default/isc-dhcp-server")
	print("Find out the line that say: INTERFACES=\"\" ")

	print("change it to INTERFACES=\""+inter[1]+"\"")

	print("Next we have to setup the destination interface to static ip address:")
	stdout, stderr, rcode = runcommand_with_timeout(["ip", "link", "set", "dev", inter[1], "down"])
	if rcode != 0:
		sys.exit("\n\n"+R+"Error, could not set interface down"+W)

	print("Edit as root the file /etc/network/interfaces\n")
	print("Find the line auto wlan0 and add a # in front of it\n")
	print("Add the following :\n")
	print("allow-hotplug "+inter[1]+"\n"\
"iface "+inter[1]+" inet static\n\
address 192.168.1.1\n\
netmask 255.255.255.0\n")
	raw_input('Press enter to continue: \n')

	stdout, stderr, rcode = runcommand_with_timeout(["nmcli", "radio", "wifi", "off"])

	stdout, stderr, rcode = runcommand_with_timeout(["rfkill", "unblock", "all"])
	#Error, could unblock interface

	stdout, stderr, rcode = runcommand_with_timeout(["ip", "a", "f", "dev", inter[1]])
	#Error, could not flush the interface

	stdout, stderr, rcode = runcommand_with_timeout(["ip", "a", "a", "192.168.1.1/24", "dev", inter[1]])
	#Error, could not setup the interface ip


	print("Next we have to configure the access point: \n")
	print("Edit as root the file /etc/hostapd/hostapd.conf")
	print("interface="+inter[1]+"\n\
driver=nl80211\n\
ssid=AP\n\
country_code=FR\n\
hw_mode=g\n\
channel=11\n\
macaddr_acl=0\n\
auth_algs=1\n\
ignore_broadcast_ssid=0\n\
wpa=3\n\
wpa_passphrase=test1234\n\
wpa_key_mgmt=WPA-PSK\n\
rsn_pairwise=CCMP\n\
wpa_pairwise=TKIP\n\
wpa_group_rekey=86400\n\
ieee80211n=1\n\
wme_enabled=1\n")

	raw_input('Press enter to continue: \n')

	print("Next we have to specify to hostapd where is the configuration file: \n")
	print("Edit as root the file /etc/default/hostapd\n")
	print("Find the line that say #DAEMON_CONF=\"\"")
	print("Edit it to DAEMON_CONF=\"/etc/hostapd/hostapd.conf\"")

	raw_input('Press enter to continue: \n')

	print("\nEnable ip forward for ipv4: \n")
	print("Edit the file /etc/sysctl.conf and add at the bottom: \n")
	print("net.ipv4.ip_forward=1")

	raw_input('Press enter to continue: \n')


	stdout, stderr, rcode = runcommand_with_timeout(["echo", "1", ">", "/proc/sys/net/ipv4/ip_forward"])
	if rcode != 0:
		sys.exit("\n\n"+R+"Error, could not set interface up"+W)

def create_iptables_rules(inter):
	stdout, stderr, rcode = runcommand_with_timeout(["iptables", "-F"])
	if rcode != 0:
		sys.exit("\n\n"+R+"Error, could not flush iptables rules"+W)

	stdout, stderr, rcode = runcommand_with_timeout(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", inter[0], "-j", "MASQUERADE"])
	if rcode != 0:
		sys.exit("\n\n"+R+"Error, could not set iptables rule"+W)

	stdout, stderr, rcode = runcommand_with_timeout(["iptables", "-A", "FORWARD", "-i", inter[0], "-o", inter[1], "-m", "state", "--state",\
		"RELATED,ESTABLISHED", "-j", "ACCEPT"])
	if rcode != 0:
		sys.exit("\n\n"+R+"Error, could not set iptables rule"+W)

	stdout, stderr, rcode = runcommand_with_timeout(["iptables", "-A", "FORWARD", "-i", inter[1], "-o", inter[0], "-j", "ACCEPT"])
	if rcode != 0:
		sys.exit("\n\n"+R+"Error, could not set iptables rule"+W)

	stdout, stderr, rcode = runcommand_with_timeout(["ip", "link", "set", "dev", inter[1], "up"])
	#Error, could not set interface up
	time.sleep(2)

def run_hostapd():

	stdout, stderr, rcode = runcommand_with_timeout(["systemctl", "start", "isc-dhcp-server"])
	if rcode != 0:
		sys.exit("\n\n"+R+"Error, could not restart dhcp server"+W)
	
	print("run the following command to checkout if isc-dhcp-server is running:\n\n\t systemctl status isc-dhcp-server\n")
	print("if your isc-dhcp-server doesn't start run this command :\n\
		\n\t rm /var/run/dhcpd.pid \n")

	print("\n\nRun this command to start your access point:\n\n\thostapd /etc/hostapd/hostapd.conf\n\n")
	print("if hostapd doesn't start try to reload your wireless driver.\n")
if __name__ == "__main__":
	inter = []
	checking_functions()
	interfaces = get_interfaces()
	print("Available interfaces: ", end="\n")
	i = 0
	for interface in interfaces:
		i = i+1
		print("\t"+ str(i) +"- "+B+" "+interface+W+"\n")     

	choice = get_int("Choose source interface [1-"+str(len(interfaces))+"] : ")
	inter.append(interfaces[choice-1])
	print("The source interface to share connection is: "+G+inter[0]+W)
	choice = get_int("Choose destination interface [1-"+str(len(interfaces))+"] : ")
	inter.append(interfaces[choice-1])
	if inter[0] == inter[1]:
		print(R+"Can't use the same interface"+W)
		sys.exit()
	print("The destination interface to share connection is: "+G+inter[1]+W)
	setup_dhcp_ap(inter)
	create_iptables_rules(inter)
	run_hostapd()