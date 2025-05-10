class OperationFlow:
    class Node:
        def __init__(self, prev=None, next=None):
            self.prev = prev
            self.next = next
            self.participant = None
            self.team = None
            self.op_func = None

    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def append_tail(self, participant, team, op_func):
        new_node = OperationFlow.Node(participant, team, op_func)
        if self.head == None:
            self.head = new_node
            self.tail = new_node
            self.length = 1
            return

        new_node.prev = self.tail
        self.tail.next = new_node
        self.tail = new_node
        self.length += 1

    def remove_tail(self):
        if self.head == self.tail:
            self.head = None
            self.tail = None
            self.length = 0
            return

        prev = self.tail.prev
        prev.next = None
        self.tail = prev
        self.length -= 1
