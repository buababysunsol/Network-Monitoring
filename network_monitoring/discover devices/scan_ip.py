from socket import *
from netaddr import *
import pprint

#port scanner

def port_scan(port, host)
    s = socket(AF_INET, SOCK_STREAM)
    try:
        s = s.connect((host, port))
        print "Port : ", port, "is open"
    except Exception, e:
        pass



    #get user input for range in form xxx.xxx.xxx.xxx
    ipStart, ipEnd = raw_input ("Enter_ip : ").split("-")
    portStart, portEnd = raw_input ("Enter port-port: ").split("-")

    # cast port string to int
    portStart, portEnd = [int(portStart), int(portEnd)]

    # define IP range
    iprange = IPRange(ipStart, ipEnd)

    # this is where my problem is
    for ip in iprange:
        host = ip
        for port in range(startPort, endPort + 1)
            port_scan(port, host)

    host = ip
    print(host)  # added

