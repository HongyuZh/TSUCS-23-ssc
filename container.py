import time

import docker

client = docker.from_env()
cpu_per_mem = 1/512


def wait_complete():
    # attention: before the execution of a container, we should guarantee that there is no
    # other containers are running. otherwise, the time accuracy will be affected
    while True:
        active_containers = client.containers.list()

        if len(active_containers) == 0:
            break
        else:
            # sleep for 2 seconds
            time.sleep(2)


class Container:
    def __init__(self, image_id, mem_alloc):
        '''
            docker_id: the id of docker container
            mem_alloc: memory allocated to this container
        '''
        self.mem = mem_alloc
        self.rt = 0
        self.cost = 0
        self.image_id = image_id
        self.container_id = self._initContainer()

    def _initContainer(self):
        '''
            Create the container and return its id.
        '''
        container = client.containers.create(
            self.image_id,
            detach=True,
            mem_limit=f'{self.mem}M',
            cpu_period=100000,
            cpu_quota=int(
                self.mem * cpu_per_mem * 100000),
            memswap_limit=-1
        )
        print('Container-%s of image-%s is created (memory allocation: %d).'
              % (container.short_id, self.image_id, self.mem))
        return container.short_id

    def run(self):
        '''
            run the container and update its runtime and cost
        '''
        container = client.containers.get(self.container_id)
        wait_complete()
        container.restart()
        wait_complete()

        log = str(container.logs(), encoding='utf-8').strip()
        self.rt = int(log.split(':')[-1])
        self.cost = (self.mem * self.rt * 1.5 + 256) / 100000

    def updateRes(self, mem_alloc: int):
        '''
            mem_alloc: update the memory allocation of the container
        '''
        self.mem = mem_alloc
        container = client.containers.get(self.container_id)
        container.update(
            mem_limit=f'{self.mem}M',
            cpu_period=100000,
            cpu_quota=int(
                self.mem * cpu_per_mem * 100000),
            memswap_limit=-1
        )

    def __del__(self):
        container = client.containers.get(self.container_id)
        container.remove()
