END = "END"

class StateGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.entry_point = None

    def add_node(self, name, func):
        self.nodes[name] = func

    def set_entry_point(self, name):
        self.entry_point = name

    def add_edge(self, from_node, to_node):
        self.edges[from_node] = to_node

    def compile(self):
        return self

    def invoke(self, state):
        current = self.entry_point
        while current != END:
            node_func = self.nodes[current]
            updates = node_func(state)
            for k, v in updates.items():
                setattr(state, k, v)
            current = self.edges.get(current, END)
        return state
