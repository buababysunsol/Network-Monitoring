from threading import Thread, current_thread
from multiprocessing import Process, current_process, Pool
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait
import time
import ipaddress
import random
import os
import timeit
import queue


def ping(ip):
    return os.system("ping -c 1 -W 1 {} >/dev/null".format(ip)) == 0


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
                self.result[ip] = is_alive
                print("IP {} is {}".format(_ip, is_alive))
                self.input_queue.task_done()

    for i in range(100):
        t = PingThread(q, result)
        t.setDaemon(True)
        t.start()

    for ip in ips.hosts():
        q.put(str(ip))

    q.join()
    return result


def counter_thread(ip):
    pass


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
    ips = ipaddress.IPv4Network("103.253.72.0/23")

    print("Run ping thread")
    a = ping_all(ips)
    # print(a)
    # print("Run Threading")
    # start_time = time.time()
    # run_thread_test(ip)
    # usage_time = time.time() - start_time
    # print("Usage time: {:.3f}".format(usage_time))
    #
    # print("=" * 25)
    # print("Run Multiprocessing")
    # start_time = time.time()
    # run_mp_test(ip)
    # usage_time = time.time() - start_time
    # print("Usage time: {:.3f}".format(usage_time))
    #
    # print("=" * 25)
    # print("Run Multiprocessing pool")
    # start_time = time.time()
    # run_mp_pool_test(ip)
    # usage_time = time.time() - start_time
    # print("Usage time: {:.3f}".format(usage_time))
    #
    # print("=" * 25)
    # print("Run Concurrent Multiprocessing pool")
    # start_time = time.time()
    # run_mp_concurrent_pool_test(ip)
    # usage_time = time.time() - start_time
    # print("Usage time: {:.3f}".format(usage_time))


if __name__ == '__main__':
    main()
