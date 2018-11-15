from objects import *
from mdp import *
import random, math

class Simulator:
    def __init__(self, problem_spec, output_file):
        self.ps = problem_spec
        self.current = State(
            self.ps.map.path[0],
            self.ps.car_list[0], 
            self.ps.tire_list[0], 
            self.ps.driver_list[0]
            )
        self.steps_limit = self.ps.steps_limit
        self.states = [] #list of states
        self.output = output_file

    def reset_output_file(self):
        file = open(self.output, "w")
        file.close()

    def write_on_file(self, string):
        file = open(self.output, "a+")
        file.write(string)
        file.close()

    def solve(self):
        self.reset_output_file()
        mdp = MDP(self.ps)
        self.states = mdp.value_iteration()

    def print_step(self, step, act):
        pos_comb = str(self.current.pos.num+1)+","
        s_flag = "1" if self.current.is_slip else "0"
        b_flag = "1" if self.current.is_breakdown else "0"
        pos_comb += (s_flag+","+b_flag+",")
        pos_comb += (self.current.car.name+","+self.current.driver.name+","+self.current.tire.name+",")
        pos_comb += (str(self.current.car.fuel)+","+str(self.current.pressure)+"%,")
        self.write_on_file(str(step)+";("+pos_comb+");("+act+")\n")

    def simulate(self):
        step_num = 0
        act = ""
        self.print_step("start", "n.a.")
        while step_num <= self.steps_limit and self.current.pos.num < self.ps.map.length - 1:
            step = 1
            if self.is_all_match() and not self.is_fuel_empty():
                self.perform_a1()
                act = "A1"
            elif self.ps.level > 3 and not self.is_car_match() and not self.is_driver_match():
                self.perform_a7()
                act = "A7:"+self.current.car.name+":"+self.current.driver.name
            elif not self.is_car_match():
                self.perform_a2()
                act = "A2:"+self.current.car.name
            elif not self.is_driver_match():
                self.perform_a3()
                act = "A3:"+self.current.driver.name
            elif not self.is_tire_match():
                self.perform_a4()
                act = "A4:"+self.current.tire.name
            elif self.is_fuel_empty():
                step = self.perform_a5()
                act = "A5:"+str(max(list(self.current.car.consumptions.values())))
            elif self.is_pressure_change():
                self.perform_a6()
                act = "A6:"+str(self.current.pressure)
            self.print_step(step_num,act)
            if not self.current.is_slip and not self.current.is_breakdown:
                step_num += step
            elif self.current.is_slip:
                step_num += self.ps.slip_time
                self.current.is_slip = False
            elif self.current.is_breakdown:
                step_num += self.ps.breakdown_time
                self.current.is_breakdown = False
        if self.current.pos.num == self.ps.map.length - 1:
            self.write_on_file("Goal reached!")
        else:
            self.write_on_file("Computer says no. Max steps reached: max steps ="+str(self.steps_limit))

    def get_move_prob(self):
        p_k = 1/12
        p_car = 1/len(self.ps.car_list)
        p_driver = 1/len(self.ps.driver_list)
        p_tire = 1/len(self.ps.tire_list)
        p_terrain = 1/self.ps.total_terrain
        p_pressure = 1/3
        p_k_given_pressure = self.convert_slip_prob(self.current.pos.slip_prob)
        p_car_given_k = self.bayes_rule(self.current.car.prob, p_car, p_k)
        p_driver_given_k = self.bayes_rule(self.current.driver.prob, p_car, p_k)
        p_tire_given_k = self.bayes_rule(self.current.tire.prob, p_car, p_k)
        p_pressure_given_k = self.bayes_rule(p_k_given_pressure, p_terrain*p_pressure, p_k)
        k_probs = []
        p_sum = 0
        for k in range(12):
            k_prob = self.magic_formula(p_car_given_k[k], p_driver_given_k[k],
                                        p_tire_given_k[k],p_pressure_given_k[k], p_k)
            p_sum += k_prob
            k_probs.append(k_prob)
        for k in range(12):
            k_probs[k] /= p_sum
        return k_probs

    def bayes_rule(self, c_prob, a, b):
        res = []
        for c in c_prob:
            res.append((c*a)/b)
        return res

    def magic_formula(self, c_prob1, c_prob2, c_prob3, c_prob4, p):
        return c_prob1 * c_prob2 * c_prob3 * c_prob4 * p

    def convert_slip_prob(self, slip_prob):
        tmp_prob = slip_prob
        if self.current.pressure == 75:
            tmp_prob = slip_prob * 2
        elif self.current.pressure == 100:
            tmp_prob = slip_prob * 3
        k_probs = []
        other_prob = (1 - tmp_prob)/11
        for i in range(12):
            if i == 10:
                k_probs.append(tmp_prob)
            else:
                k_probs.append(other_prob)
        return k_probs

    def perform_a1(self):
        move_probs = self.get_move_prob()
        p = random.random()
        p_sum = 0
        move = -4
        if self.ps.level > 1:
            fuel = self.current.car.consumptions[self.current.pos.type]
            if self.current.pressure == 50:
                fuel_usage = fuel * 3
            elif self.current.pressure == 75:
                fuel_usage = fuel * 2
            elif self.current.pressure == 100:
                fuel_usage = fuel
            self.current.car.fuel -= fuel_usage
        for k in range(12):
            p_sum += move_probs[k]
            if p <= p_sum:
                if move < 6:
                    next_pos = self.current.pos.num + move
                    if next_pos < 0:
                        next_pos = 0
                    elif next_pos >= self.ps.map.length - 1:
                        next_pos = self.ps.map.length - 1
                    self.current.pos = self.ps.map.path[next_pos]
                elif move == 6:
                    self.current.is_slip = True
                elif move == 7:
                    self.current.is_breakdown = True
                break
            move += 1
    
    def perform_a2(self):
        for car in self.ps.car_list:
            if car.name == self.states[self.current.pos.num].car.name:
                self.current.car = car
                self.current.car.fuel = 50
                self.current.pressure = 100
    
    def perform_a3(self):
        for driver in self.ps.driver_list:
            if driver.name == self.states[self.current.pos.num].driver.name:
                self.current.driver = driver
    
    def perform_a4(self):
        for tire in self.ps.tire_list:
            if tire.name == self.states[self.current.pos.num].tire.name:
                self.current.tire = tire
                self.current.pressure = 100
    
    def perform_a5(self):
        f = max(list(self.current.car.consumptions.values()))
        self.current.car.fuel += f
        return math.ceil(f/10)
    
    def perform_a6(self):
        self.current.pressure = self.states[self.current.pos.num].pressure

    def perform_a7(self):
        self.perform_a2()
        self.perform_a3()

    def is_all_match(self):
        return self.is_car_match() and self.is_driver_match() and \
               self.is_tire_match() and not self.is_fuel_empty() and \
               not self.is_pressure_change()

    def is_car_match(self):
        return self.current.car == self.states[self.current.pos.num].car

    def is_driver_match(self):
        return self.current.driver == self.states[self.current.pos.num].driver

    def is_tire_match(self):
        return self.current.tire == self.states[self.current.pos.num].tire

    def is_fuel_empty(self):
        return self.current.car.fuel < max(list(self.current.car.consumptions.values()))

    def is_pressure_change(self):
        if self.ps.level == 1:
            return False
        return self.current.pressure != self.states[self.current.pos.num].pressure
