import container
import priority_queue

import random
import math

time_limit = 15000


class node:
    def __init__(self, image_id: str, index: int):
        self.container = container.Container(image_id, 768)
        self.priority = math.inf
        self.index = index
        self.trial = 3


def updateRtAndCost(branchChoose: int, workflow: list):
    runtime = 0
    cost = 0
    runtime += workflow[0].container.rt
    if branchChoose > 0.2:
        if workflow[2].container.rt+workflow[4].container.rt > workflow[1].container.rt:
            runtime += workflow[2].container.rt+workflow[4].container.rt
        else:
            runtime += workflow[1].container.rt
        cost += workflow[0].container.cost + workflow[1].container.cost + \
            workflow[2].container.cost + \
            workflow[4].container.cost + workflow[5].container.cost
    else:
        if workflow[2].container.rt+workflow[3].container.rt > workflow[1].container.rt:
            runtime += workflow[2].container.rt+workflow[3].container.rt
        else:
            runtime += workflow[1].container.rt
        cost += workflow[0].container.cost + workflow[1].container.cost + \
            workflow[2].container.cost + \
            workflow[3].container.cost + workflow[5].container.cost
    runtime += workflow[5].container.rt

    return (runtime, cost)


def setUpPQ(branchChoose: int, workflow: list, pq: priority_queue.PriorityQueue):
    while pq.notEmpty():
        pq.pop()
    pq.push(workflow[0], workflow[0].priority)
    if branchChoose > 0.2:
        if workflow[2].container.rt+workflow[4].container.rt > workflow[1].container.rt:
            pq.push(workflow[2], workflow[2].priority)
            pq.push(workflow[4], workflow[4].priority)
        else:
            pq.push(workflow[1], workflow[1].priority)
    else:
        if workflow[2].container.rt+workflow[3].container.rt > workflow[1].container.rt:
            pq.push(workflow[2], workflow[2].priority)
            pq.push(workflow[3], workflow[3].priority)
        else:
            pq.push(workflow[1], workflow[1].priority)
    pq.push(workflow[5], workflow[5].priority)


if __name__ == '__main__':
    workflow = []
    index = 1
    for id in ['chameleon:v1', 'chameleon:v1', 'matmul:v1',
               'float_operation:v1', 'chameleon:v1', 'pyaes:v1']:
        workflow.append(node(id, index))
        index += 1
    pq = priority_queue.PriorityQueue()

    for func in workflow:
        container = func.container
        container.run()
        print(
            f'fun:{func.index}, runtime:{container.rt}, cost:{container.cost}')

    branchChoose = random.random()
    setUpPQ(branchChoose, workflow, pq)

    index = 1
    while pq.notEmpty():
        print(f'index:{index}')
        for item in pq._queue:
            print(f'{item[2].index}:{item[0]}')
        currNode = pq.pop()
        currNode.container.updateRes(max(currNode.container.mem - 32, 128))
        rt_old, cost_old = updateRtAndCost(branchChoose, workflow)
        currNode.container.run()

        for func in workflow:
            container = func.container
            print(
                f'fun:{func.index}, runtime:{container.rt}, cost:{container.cost}, mem:{container.mem}')
        rt_new, cost_new = updateRtAndCost(branchChoose, workflow)

        if rt_new > time_limit:
            print(f'timeout({rt_new})')
            if rt_new > time_limit + 1000:
                break

            cnt = 3
            while rt_new > time_limit and cnt > 0:
                currNode.container.updateRes(currNode.container.mem + 32)
                currNode.container.run()
                rt_new, cost_new = updateRtAndCost(branchChoose, workflow)
                cnt -= 1
            print(f'runtime:{rt_new}, cost:{cost_new}')

            if currNode.trial > 0:
                currNode.trial -= 1
                pq.push(currNode, 0)

        elif cost_new > cost_old*1.05:
            print(f'overcost({cost_new})')
            currNode.container.updateRes(currNode.container.mem + 32)
            currNode.container.run()
            rt_new, cost_new = updateRtAndCost(branchChoose, workflow)
            print(f'runtime:{rt_new}, cost:{cost_new}')

            if currNode.trial > 0:
                currNode.trial -= 1
                pq.push(currNode, 0)
        else:
            print(f'runtime:{rt_new}, cost:{cost_new}')
            currNode.trial = 3
            currNode.priority = max(cost_old-cost_new, 0)

        branchChoose = random.random()
        setUpPQ(branchChoose, workflow, pq)
        index += 1
