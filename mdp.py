class MDP:
    def __init__(self, problem_spec):
        self.ps = problem_spec
        self.states = []

    def initiate_states(self):
        for t in self.ps.map.path:
            state = State(t, None, None, None)
            self.states.append(state)
        self.states[0].set_reward(-5, 0)
        self.states[0].i_reward = -5 #to tell the algorithm not going backward
        self.states[-1].set_reward(5, 0)
        self.states[-1].i_reward = 5 #to tell the algorithm going forward

    def reset_states_reward(self):
        for s in self.states:
            s.set_reward(-1, 0)
        self.states[-1].set_reward(5, 0)

    def value_iteration(self):
        self.initiate_states()
        self.iterate_value(self.ps.car_list, "car")
        self.reset_states_reward()
        self.iterate_value(self.ps.driver_list, "driver")
        self.reset_states_reward()
        self.iterate_value(self.ps.tire_list, "tire")
        self.reset_states_reward()
        self.decide_pressure([50, 75, 100])
        return self.states

    def iterate_value(self, objects, obj_type):
        move_sample = [n for n in range(-4, 6)]
        while not self.states_are_converged():
            for current in self.states:
                reward_per_object = []
                for obj in objects:
                    prob_list = []
                    for i in range(len(obj.prob)):
                        if i == 10:
                            tmp = obj.prob[i] * -(self.ps.slip_time**2)
                        elif i == 11:
                            tmp = obj.prob[i] * -(self.ps.breakdown_time**2)
                        else:
                            if current.pos.num + move_sample[i] < 0:
                                tmp = obj.prob[i] * self.states[0].reward
                            elif current.pos.num + move_sample[i] >= self.ps.map.length:
                                tmp = obj.prob[i] * self.states[-1].reward
                            else:
                                tmp = obj.prob[i] * self.states[current.pos.num+move_sample[i]].reward
                        prob_list.append(tmp)
                    total = current.i_reward + self.ps.discount * sum(prob_list)
                    reward_per_object.append(total)
                max_reward = max(reward_per_object)
                selected_obj = objects[reward_per_object.index(max_reward)]
                current.set_reward(max_reward, current.reward)
                if obj_type == "car":
                    current.car = selected_obj
                elif obj_type == "driver":
                    current.driver = selected_obj
                elif obj_type == "tire":
                    current.tire = selected_obj
        #print("Converged. Total loop:", c)
        #print("Final reward:", reward_per_object)

    def states_are_converged(self):
        for s in self.states:
            if not s.is_converged():
                return False
        return True

    def decide_pressure(self, pressure_list):
        for current in self.states:
            reward_per_object = []
            fuel = current.car.consumptions[current.pos.type]
            slip_prob = current.pos.slip_prob
            for pressure in pressure_list:
                prob_list = []
                if pressure == 50:
                    current_fuel = fuel * 3
                    current_slip = slip_prob
                elif pressure == 75:
                    current_fuel = fuel * 2
                    current_slip = slip_prob * 2
                elif pressure == 100:
                    current_fuel = fuel
                    current_slip = slip_prob * 3
                obj_prob = []
                other_prob = (1 - current_slip)/11
                for i in range(12): #distribute prob for pressure
                    if i == 10:
                        obj_prob.append(current_slip)
                    else:
                        obj_prob.append(other_prob)
                fuel_reward = [-current_fuel for i in range(12)] #distribute reward based on fuel
                fuel_reward[10] = -(self.ps.slip_time**2)
                prob_list = [obj_prob[i] * fuel_reward[i] for i in range(len(obj_prob))]
                total = current.i_reward + self.ps.discount * sum(prob_list)
                reward_per_object.append(total)
            max_reward = max(reward_per_object)
            selected_obj = pressure_list[reward_per_object.index(max_reward)]
            current.pressure = selected_obj

class State:
    def __init__(self, pos, car, tire, driver):
        self.pos = pos
        self.is_slip = False
        self.is_breakdown = False
        self.car = car
        self.tire = tire
        self.pressure = 100
        self.driver = driver
        self.reward = -1
        self.i_reward = -1
        self.prev_reward = 0

    def set_reward(self, r, p_r):
        self.prev_reward = p_r
        self.reward = r

    def is_converged(self):
        return self.prev_reward == self.reward
