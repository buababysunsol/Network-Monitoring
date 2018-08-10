import ipaddress
import os
import pprint
import queue
import netaddr
from threading import Thread

from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import NodeIP


def ping(ip):
    return os.system("ping -c 1 -W 5 {} >/dev/null".format(ip)) == 0


# def ping_all(ips):
#     q = queue.Queue()
#     result = {}
#
#     class PingThread(Thread):
#         def __init__(self, input_queue, result):
#             super().__init__()
#             self.input_queue = input_queue
#             self.result = result
#
#         def run(self):
#             while True:
#                 _ip = self.input_queue.get()
#                 is_alive = ping(_ip)
#                 self.result[_ip] = is_alive
#                 # print("IP {} is {}".format(_ip, is_alive))
#                 self.input_queue.task_done()
#
#     for i in range(50):
#         t = PingThread(q, result)
#         t.setDaemon(True)
#         t.start()
#
#     for ip in ips.hosts():
#         q.put(str(ip))
#
#     q.join()
#     return result

def pingv4(ip: ipaddress.IPv4Address):
    if os.name == 'posix':
        return os.system("ping -c 1 -W 1 {ip} > /dev/null".format(ip=str(ip))) == 0
    return False


def scan_network(network: iter):
    result = {}
    input_queue = queue.Queue()

    class PingWorker(Thread):
        def __init__(self, input_queue, result):
            super().__init__()
            self.input_queue = input_queue
            self.result = result

        def run(self):
            while True:
                ip = self.input_queue.get()
                isalive = pingv4(ip)
                result[str(ip)] = isalive
                self.input_queue.task_done()

    max_worker = 70
    num_worker = min(len(network), max_worker);
    print("Using worker : {}".format(num_worker))

    for _ in range(num_worker):
        p = PingWorker(input_queue, result)
        p.setDaemon(True)
        p.start()

    for ip in network:
        result[str(ip)] = False
        input_queue.put(ip)
    input_queue.join()
    return result


def discover_network(request):
    # discover ip submask
    network = request.GET.get('network')
    community = request.GET.get('community')
    if network:
        print("Discover network: {}".format(network))
        result = scan_network(netaddr.IPNetwork(network))
        # add_node_ip(result)
    else:
        result = {}

    return render(request, "discover/test_discover.html", {"result": result, 'community': community
                                                           })


def scanning_ip(request):
    start_ip = request.GET.get("start_ip")
    end_ip = request.GET.get("end_ip")

    result = {}

    if start_ip and end_ip:
        ip_range = netaddr.IPRange(start_ip, end_ip)
        print(ip_range)
        result = scan_network(ip_range)
        print(result)

    return render(request, "discover/scan_ip_range.html", {
        'result': result,
        'start_ip': start_ip,
        'end_ip': end_ip
    })


def add_database(request):
    ip = request.GET.get('ip_manual')
    community = request.GET.get('community')
    # add_node_ip_to_db(ip)
    if ip:
        NodeIP.objects.update_or_create(ip=ip, defaults={'alive': True, 'community': community})
    return render(request, "discover/add_manual.html")


def add_ip(request):
    add_type = request.POST.get('add_type')
    if add_type == 'single':
        ip = request.POST.get('ip')
        community = request.POST.get('community')
        alive = request.POST.get('alive')
        # Add to DB
        result = {}
        result[ip] = {
            'alive': alive,
            'community': community
        }
        add_node_ip_to_db(result)
    elif add_type == 'all':
        ips = request.POST.getlist('ips')
        community = request.POST.getlist('community')
        alive = request.POST.getlist('alive')
        result = {}

        for i in range(len(ips)):
            ip = ips[i]
            _community = community[i]
            _alive = alive[i]
            result[ip] = {
                'alive': _alive,
                'community': _community
            }
        # result = dict(zip(ips, alive))
        # # print(dict(result))
        add_node_ip_to_db(result)
    return HttpResponse("Ok")


def add_node_ip_to_db(ips: dict):
    # NodeIP.objects.bulk_create(
    #     [NodeIP(ip=ip, alive=alive) for ip, alive in ips.items()]
    # )
    for ip, data in ips.items():
        NodeIP.objects.update_or_create(ip=ip, defaults={'alive': data['alive'], 'community': data['community']})


def views_ip(request):
    result = NodeIP.objects.all()
    return render(request, "discover/view-manage-ip.html", {'result': result})


def remove_Ip(request):
    ip = request.POST.get('ip')
    if ip:
        ip_obj = NodeIP.objects.get(ip=ip)
        ip_obj.delete()

    return redirect('view_all_ip')
