class StepContext:
    def __init__(self, first_step_func, init_state):
        self.first_step_func = first_step_func
        self.init_state = init_state
        self.state = init_state.copy()
        self.stack = [(self.first_step_func, init_state.copy())]

    def push(self, step_func):
        # Push the function and a copy of the current state
        state_snapshot = self.state.copy()
        self.stack.append((step_func, state_snapshot))

    def pop(self):
        if self.stack:
            return self.stack.pop()
        else:
            return None

    def can_go_back(self, step_count: int = 1):
        return len(self.stack) > step_count - 1

    def restart(self):
        self.state = self.init_state.copy()
        self.stack.clear()
        self.push(self.first_step_func)
