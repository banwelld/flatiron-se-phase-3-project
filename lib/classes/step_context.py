class StepContext:
    def __init__(self, first_step_func):
        self.first_step_func = first_step_func
        self.init_state = {
            "sel_team": None,
            "sel_operation": None,
            "sel_participant": None,
            "comp_teams": None,
            "free_agent_team": None,
            "sel_team_participants": None,
            "free_agents": None,
            "save_prompt": None,
            "exec_func": None,
        }
        self.state = self.init_state.copy()
        self.stack = [self.first_step_func]

    def push(self, step_func):
        # Push the function and a copy of the current state
        state_snapshot = self.state.copy()
        self.stack.append((step_func, state_snapshot))

    def pop(self):
        if self.stack:
            return self.stack.pop()
        else:
            return None

    def can_go_back(self):
        return len(self.stack) > 0

    def restart(self):
        self.state = self.init_state.copy()
        self.stack.clear()
        self.push(self.first_step_func)
