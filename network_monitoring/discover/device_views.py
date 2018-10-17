from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect

from .models import NodeIP


def view(request, node_ip):
    node_ip = NodeIP.objects.filter(ip=node_ip).first()

    return render(request, "discover/node_info.html", {'node_ip': node_ip})


def destroy(request, node_ip):
    if request.method == 'POST':
        node = NodeIP.objects.filter(ip=node_ip).first()
        if node:
            node.delete()
            messages.success(request, 'Node deleted')
    return redirect('view_all_ip')


def edit(request, node_ip):
    if request.method == 'POST':
        ip = request.POST.get('ip')
        community = request.POST.get('community')
        sitename = request.POST.get('sitename')
        node = NodeIP.objects.filter(ip=node_ip).first()
        if node:
            node.ip = ip
            node.community = community
            node.site_name = sitename
            node.save()
            messages.success(request, 'Node updated')
    return redirect('view_all_ip')
