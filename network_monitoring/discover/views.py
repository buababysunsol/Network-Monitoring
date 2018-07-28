import ipaddress
import os
import queue
from threading import Thread

from django.shortcuts import render


def ping(ip):
    return os.system("ping -c 1 -W 5 {} >/dev/null".format(ip)) == 0


def ping_all(ips):
    q = queue.Queue()
    result = {}

    class PingThread(Thread):
        def __init__(self, input_queue, result):
            super().__init__()
            self.input_queue = input_queue
            self.result = result

        def run(self):
            while True:
                _ip = self.input_queue.get()
                is_alive = ping(_ip)
                self.result[_ip] = is_alive
                # print("IP {} is {}".format(_ip, is_alive))
                self.input_queue.task_done()

    for i in range(50):
        t = PingThread(q, result)
        t.setDaemon(True)
        t.start()

    for ip in ips.hosts():
        q.put(str(ip))

    q.join()
    return result


#discover main function ip from network addr and subnet mask
def discover_network(request):
    network = request.GET.get('network')
    if network:
        print("Discover network: {}".format(network))
        result = ping_all(ipaddress.IPv4Network(network))
        # Add to mongodb
    else:
        result = {}
    # Render
    return render(request, "discover/test_discover.html", {"result": result})


#scan ip main function for ip range
def scan_network(request):

    start_ip = request.GET.get('start_')
    end_ip = request.GET.get('end_')
    if start_ip:
        print("Start ip : {}".format(start_ip))
        print("End ip : {}".format(end_ip))
    else:
        pass
    return render(request, "discover/scan_ip_range.html")


# def add_database(request):
#
#     submit = request.GET.get('add')
#
#
#     return render(request, "discover/test_discover.html")