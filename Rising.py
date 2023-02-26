
import threading

import time

from threading import Timer

from flask import Flask

import requests

IDLE = 0
RUNNING = 1
TERMINATED = 2

container_id = 0
request_id = 0

alive_time = 12
running_time = 1

former = 0
latter = 0


class Container:
    def __init__(self, alive_time, running_time):
        global container_id

        self.id = container_id
        container_id += 1
        self.list = container_id

        self.alive_time = alive_time
        self.running_time = running_time
        self.state = IDLE

    def terimate(self):
        self.state = TERMINATED

    def idle(self):
        if self.state != TERMINATED :
            self.state = IDLE

        

    def running(self):
        self.state = RUNNING


class Proxy:
    def __init__(self):
        self.containers: list[Container] = []

    def find_invoker(self, request_id):
        for c in self.containers:
            # find an available container
            if c.state == IDLE:
                c.running()
                Timer(c.running_time, c.idle).start()
                print(f'execute request {request_id} in container {c.list}')
                return True

            # if container become terminated
            if c.state == TERMINATED:
                print(f'remove terminated container {c.list}')
                self.containers.remove(c)

        # not find an available container
        return False

    def create_invoker(self, alive_time, running_time): 
        c = Container(alive_time, running_time)
        Timer(alive_time, c.terimate).start()

        self.containers.append(c)

    def prewarm_invoker(self, alive_time, running_time):
        global container_id
        container_id -= 1
        c = Container(alive_time, running_time)
        c.list = 'a'
        Timer(alive_time, c.terimate).start()

        self.containers.append(c)


def prewarm(request_id):
    global former
    global latter
    former = latter
    latter = request_id - former
    num = latter - former 
    fore = latter + num
    print(num)
    if fore > proxy.containers.len() :
        for i in range(num):
            proxy.prewarm_invoker(alive_time, running_time)
 
def terminate(request_id):  
    global former
    global latter
    former = latter
    latter = request_id - former
    num = former - latter
    for i in range(num):
        proxy.containers.pop()



app = Flask(__name__)
proxy = Proxy()


@app.route("/")
def a():
    return {'hello': 'world'}

@app.route("/test1")
def handle_request():
    global request_id
    request_id += 1
    while not proxy.find_invoker(request_id):
        proxy.create_invoker(alive_time, running_time)
    return {'hello': 'world'}

@app.route("/test2")
def pre():
    prewarm(request_id)
    return {'hello': 'world'}



if __name__ == '__main__':
    app.run()
