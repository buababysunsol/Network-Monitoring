import ipaddress
import os
import queue
import netaddr
from threading import Thread
from easysnmp import snmp_get, snmp_get_bulk, snmp_bulkwalk, EasySNMPTimeoutError, EasySNMPConnectionError
import pprint
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import NodeIP
from concurrent.futures import ThreadPoolExecutor, wait


def ping(ip):
    return os.system("ping -c 1 -W 5 {} >/dev/null".format(ip)) == 0


def pingv4(ip: ipaddress.IPv4Address):
    if os.name == 'posix':
        return os.system("ping -c 1 -W 1 {ip} > /dev/null".format(ip=str(ip))) == 0
    return False


def main(request):
    network = request.GET.get('network')
    if not network:
        success = request.GET.get('success')
        return render(request, 'discover/add_discover.html', {'success': success})
    if "-" in network:
        ips = network.split("-")
        ip_start, ip_end = ips[0], ips[1]
        result = scanning_ip(ip_start, ip_end)
        return render(request, 'discover/add_discover.html', {'result': result})
    try:
        result = scan_network(netaddr.IPNetwork(network))
        return render(request, 'discover/add_discover.html', {'result': result})
    except:
        return None


# def main(request):
#     network = request.GET.get('network')
#     community = request.GET.get('community')
#     snmp_version = request.GET.get('snmp_version')
#
#     if not network:
#         success = request.GET.get('success')
#         return render(request, 'discover/discover.html', {'success': success})
#     if "-" in network:
#         ip_start, ip_end = [x.strip for x in network.split("-")]
#         result = scanning_ip(ip_start, ip_end)
#         return render(request, 'discover/discover.html',
#                       {"result": result, 'community': community, 'snmp_version': snmp_version})
#
#     try:
#         result = scan_network(netaddr.IPNetwork(network))
#         return render(request, 'discover/discover.html',
#                       {"result": result, 'community': community, 'snmp_version': snmp_version})
#     except:
#         return None


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


def scanning_ip(start_ip, end_ip):
    result = {}

    if start_ip and end_ip:
        ip_range = netaddr.IPRange(start_ip, end_ip)
        print(ip_range)
        result = scan_network(ip_range)
        print(result)

    return render({
        'result': result,
    })


def add_database(ip, community, ver):
    # add_node_ip_to_db(ip)
    if ip:
        NodeIP.objects.update_or_create(ip=ip, defaults={'alive': True, 'community': community, 'version': ver})
    # return ('Already')


def manual(request):
    network_manual = request.GET.get('network_manual')
    version = request.GET.get('version')

    # if version == "v1":



def add_ip(request):
    add_type = request.POST.get('add_type')
    if add_type == 'single':
        ip = request.POST.get('ip')
        community = request.POST.get('community')
        snmp_version = request.POST.get('snmp_version')
        alive = request.POST.get('alive')

        result = {
            ip: {
                'alive': bool(alive),
                'community': community,
                'snmp_version': int(snmp_version)
            }
        }
        add_node_ip_to_db(result)
    elif add_type == 'all':
        ips = request.POST.getlist('ip')
        community = request.POST.getlist('community')
        snmp_version = request.POST.getlist('snmp_version')
        alive = request.POST.getlist('alive')
        result = {}

        for i in range(len(ips)):
            ip = ips[i]
            _community = community[i]
            _alive = alive[i]
            result[ip] = {
                'alive': _alive,
                'community': _community,
                'snmp_version': int(snmp_version[i])
            }
        add_node_ip_to_db(result)
    response = redirect('add-devices')
    response['Location'] += '?success=true'
    return response


def add_node_ip_to_db(ips: dict):
    for ip, data in ips.items():
        NodeIP.objects.update_or_create(ip=ip, defaults={'alive': data['alive'], 'community': data['community'],
                                                         'snmp_version': data['snmp_version'],
                                                         'interfaces': []})


def views_ip(request):
    nodes = NodeIP.objects.all()
    refresh = request.POST.get('refresh')
    if refresh:
        nodes = scan_snmp(nodes)
        for node in nodes:
            node.save()
    return render(request, "discover/view-manage-ip.html", {'result': nodes})


def remove_ip(request):
    ip = request.POST.get('ip')
    if ip:
        ip_obj = NodeIP.objects.get(ip=ip)
        ip_obj.delete()

    return redirect('view_all_ip')


def get_basic_info_snmp_v2(hostname, community, version):
    # interface_oid = '1.3.6.1.4.1.16344.1.1.0'  # hostname
    oid_name = [
        'hostname',
        'software_image',
        'location',
        'uptime',
        'dns'
    ]
    oids = [
        # '1.3.6.1.4.1.9.2.1.3' #cisco hostname
        # '1.3.6.1.2.1.1.6' #Location oid
        # '1.3.6.1.4.1.9.9.91.1.1.1' #cisco-entity-sensor
        # '1.3.6.1.2.1.2.2.1.8' #interface status
        'sysName.0',  # Hostname
        '1.3.6.1.2.1.47.1.1.1.1.9.0',  # Software version
        'sysLocation.0',  # Location
        'sysUpTime.0',  # sysUpTime
        '1.3.6.1.2.1.32',  # DNS
    ]
    data = snmp_get(oids=oids,
                    hostname=hostname,
                    community=community,
                    version=version,
                    # use_numeric=False
                    )
    return dict(zip(oid_name, data))


def get_interface_snmp_v2(hostname, community, version):
    oids = '.1.3.6.1.2.1.2.2'
    data = snmp_bulkwalk(oids=oids,
                         hostname=hostname,
                         community=community,
                         version=version,
                         # use_numeric=False
                         )
    return data


def update_snmp_node(node):
    if node.snmp_version == "2c":
        version = 2
    else:
        version = int(node.snmp_version)
    try:
        basic_data = get_basic_info_snmp_v2(node.ip, node.community, version)
        # node.hostname = basic_data['hostname']
        # node.software_version = basic_data['software_version']
        # node.location = basic_data['location']
        # node.uptime = basic_data['uptime']
        # node.dns = basic_data['dns']
        for name, data in basic_data.items():
            setattr(node, name, data.value)

        # Interface data
        if_data = get_interface_snmp_v2(node.ip, node.community, version)
        interfaces = {}
        for data in if_data:
            if not interfaces.get(data.oid_index):
                interfaces[data.oid_index] = {}
            interfaces[data.oid_index][data.oid] = data.value

        # Todo ifPhysAddress decode

        # Add to interfaces
        node.interfaces = list(interfaces.values())

        node.alive = True
    except (EasySNMPTimeoutError, EasySNMPConnectionError):
        pprint.pprint("SNMP: Can't connect to host {}".format(node.ip))
        node.alive = False
    return node


def scan_snmp(nodes):
    nodes_future = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for node in nodes:
            nodes_future.append(executor.submit(update_snmp_node, node))
        wait(nodes_future)
    return [node_future.result() for node_future in nodes_future]
