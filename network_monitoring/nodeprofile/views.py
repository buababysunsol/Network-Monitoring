from django.http import HttpResponse
from django.shortcuts import render, redirect
from pysnmp.hlapi import *
from easysnmp import snmp_bulkwalk, snmp_get
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
import pprint
from discover.models import NodeIP


def view_all_node(request):
    result = NodeIP.objects.all()
    return render(request, 'node/All node.html', {'result': result})


# def node_detail():
#
def node_profile(request):
    profile = request.POST.get('profile')
    if profile == 'detail':
        return redirect('node-profile')


# View node by pysnmp
def view_node(request, node_id):
    print(node_id)
    engine = SnmpEngine()
    community = CommunityData('public', mpModel=0)
    host = UdpTransportTarget(('demo.snmplabs.com', 161))
    context_data = ContextData()
    var_binds = (
        ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.1')),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.2')),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.3')),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.4')),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.5')),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.6')),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.7')),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.8'))
    )
    text_output = ""
    for errorIndication, errorStatus, errorIndex, varBinds in bulkCmd(
            engine,
            community,
            host,
            context_data,
            0, 16,
            *var_binds,
            lexicographicMode=False
    ):
        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print('{} at {}'.format(errorStatus.prettyPrint(), errorIndex))
        else:
            for varBind in varBinds:
                text_output += ' = '.join([
                    x.prettyPrint() for x in varBind
                ])
                text_output += '</br>'

    return HttpResponse(text_output)


# View node by easysnmp
def view_node_easy(request, oid):
    print("Request view node easy <oid: {}>".format(oid))
    interface_oids = [
        # oid
        # '1.3.6.1.4.1.207.8.9.2.5.2.1', #vlan
        # '1.3.6.1.2.1.2.2.1'  # Interfaces
        # '1.3.6.1.2.1.4.20'  # Ip Addr
        # '1.3.6.1.2.1.1'  # System info
        '1.3.6.1.2.1.1.5'  # SysNAMe
        # '1.3.6.1.2.1.2.2.1.1',  # index
        # '1.3.6.1.2.1.2.2.1.2',  # description
        #  '1.3.6.1.2.1.2.2.1.5',  # speed
        # '1.3.6.1.2.1.1',  # des
        # '1.3.6.1.4.1.9.7.584', #LLDP
        # '1.3.6.1.2.1.2.2.1.10',  # in_octets
        # '1.3.6.1.2.1.2.2.1.16',  # out_octets
        # '1.3.6.1.2.1.2.2.1'
    ]

    hostname = 'demo.snmplabs.com'
    community = 'public'
    version = 2

    interface_fetch = snmp_get(
        interface_oids,
        0,
        100,
        hostname=hostname,
        community=community,
        version=version,
        use_numeric=False
    )

    ifs = {}
    oid_list = []
    for item in interface_fetch:
        oid = item.oid
        oid_index = item.oid_index

        # print(item.oid, item.value)
        # output_text += "{}.{} = {}</br>".format(item.oid, item.oid_index, item.value)
        oid_list.append(item)
        if oid == 'ifIndex':
            ifs[oid_index] = {}
        else:
            value = item.value
            if item.snmp_type in ('INTEGER', 'COUNTER'):
                value = int(value)

    return render(request, 'node/view_oid.html', {'oids': oid_list})


def view_all(request):
    data = {
        'nodes': [
            'a1',
            'a2',
            'a3'
        ]
    }
    return render(request, 'node/index.html', data)


def worker(name):
    print("Request view node easy <oid: {}>".format("1.3.6.1.2.1.1"))
    interface_oids = [
        # oid
        # '1.3.6.1.4.1.207.8.9.2.5.2.1', #vlan
        # '1.3.6.1.2.1.2.2.1'  # Interfaces
        # '1.3.6.1.2.1.4.20'  # Ip Addr
        # '1.3.6.1.2.1.1'  # System info
        # '1.3.6.1.2.1.2.2.1.1',  # index
        # '1.3.6.1.2.1.2.2.1.2',  # description
        #  '1.3.6.1.2.1.2.2.1.5',  # speed
        '1.3.6.1.2.1.1',  # des
        # '1.3.6.1.4.1.9.7.584', #LLDP
        # '1.3.6.1.2.1.2.2.1.10',  # in_octets
        # '1.3.6.1.2.1.2.2.1.16',  # out_octets
        # '1.3.6.1.2.1.2.2.1'
    ]

    hostname = 'demo.snmplabs.com'
    community = 'public'
    version = 2

    interface_fetch = snmp_bulkwalk(
        ["1.3.6.1.2.1.2.2.1"],
        0,
        100,
        hostname=hostname,
        community=community,
        version=version,
        use_numeric=False
    )

    ifs = {}
    oid_list = []
    for item in interface_fetch:
        oid = item.oid
        oid_index = item.oid_index

        # print(item.oid, item.value)
        # output_text += "{}.{} = {}</br>".format(item.oid, item.oid_index, item.value)
        oid_list.append(item)
        if oid == 'ifIndex':
            ifs[oid_index] = {}
        else:
            value = item.value
            if item.snmp_type in ('INTEGER', 'COUNTER'):
                value = int(value)

    return {'from': name, 'oids': oid_list}


def test_thread(request):
    workers = []
    pool = ThreadPoolExecutor(max_workers=4)
    for i in range(4):
        p = pool.submit(worker, "P-{}".format(i))
        workers.append(p)

    n = []
    for future in as_completed(workers):
        result = future.result()
        # Todo result...

        data = {
            'name': result['from'],
            'data': []
        }
        for oid in result['oids']:
            data['data'].append("{} = {}".format(oid.oid, oid.value))
        n.append(data)

    return HttpResponse("Success, <pre>" + pprint.pformat(n))

# def get_snmp(ip):
