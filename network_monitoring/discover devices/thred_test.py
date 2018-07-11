from threading import Thread, current_thread
from multiprocessing import Process, current_process, Pool
from concurrent.futures import ProcessPoolExecutor, wait
import time
import ipaddress
import random
import os
import timeit

def couter_thread(ip):
    name = current_thread().getName()
    print("{}: {} START".format(name, ip))
    for i in range (10000000):
        x = i + 1 * 22 - 123 + 123 * 99
    print ("{}: {} END".format(name, ip))


def counter_mp(ip):
    name = current_process().name
    print("{}: {} START".format(name, ip))
    for i in range(10000000):
        x = i + 1 * 22 - 123 + 123 * 99
    print("{}: {} END".format(name, ip))


def run_thread_test(ip):
    threads = []
    for n in ip.hosts():
        t = Thread(target=counter_thread, args=(n,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


def run_mp_test(ip):
    threads = []
    for n in ip.hosts():
        t = Process(target=counter_mp, args=(n,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


def run_mp_pool_test(ip):
    with Pool(4) as pool:
        threads = []
        for n in ip.hosts():
            t = pool.apply_async(counter_mp, args=(n,))
            threads.append(t)

        for t in threads:
            t.get()


def run_mp_concurrent_pool_test(ip):
    with ProcessPoolExecutor(max_workers=4) as executor:
        threads = []
        for n in ip.hosts():
            t = executor.submit(counter_mp, n)
            threads.append(t)

        wait(threads)

def main():
    ip = ipaddress.IPv4Network("192.168.1.0/29")

    print("Run Threading")
    start_time = time.time()
    run_thread_test(ip)
    usage_time = time.time() - start_time
    print("Usage time: {:.3f}".format(usage_time))

    print("=" * 25)
    print("Run Multiprocessing")
    start_time = time.time()
    run_mp_test(ip)
    usage_time = time.time() - start_time
    print("Usage time: {:.3f}".format(usage_time))

    print("=" * 25)
    print("Run Multiprocessing pool")
    start_time = time.time()
    run_mp_pool_test(ip)
    usage_time = time.time() - start_time
    print("Usage time: {:.3f}".format(usage_time))

    print("=" * 25)
    print("Run Concurrent Multiprocessing pool")
    start_time = time.time()
    run_mp_concurrent_pool_test(ip)
    usage_time = time.time() - start_time
    print("Usage time: {:.3f}".format(usage_time))

if __name__ == '__main__':
    main()