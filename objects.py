class Problem:
    def __init__(self, problem_string):
        self.problem_string = problem_string
        self.level = 0
        self.discount = 0
        self.slip_time = 0
        self.breakdown_time = 0
        self.steps_limit = 0
        self.map = None
        self.car_list = []
        self.driver_list = []
        self.tire_list = []
        self.total_terrain = 0

    def parse(self):
        p_lines = self.problem_string.split("\n")
        self.level = int(p_lines[0])
        p_lines[1] = p_lines[1].split()
        self.discount = float(p_lines[1][0])
        self.slip_time = int(p_lines[1][1])
        self.breakdown_time = int(p_lines[1][1])
        p_lines[2] = p_lines[2].split()
        self.steps_limit = int(p_lines[2][1])
        i = 3
        while ":" in p_lines[i]: #for parsing terrains
            i += 1
        self.map = Map(int(p_lines[2][0]))
        self.map.populate(p_lines[3:i], p_lines[-1])
        j = 0
        for idx in range(1, int(p_lines[i])+1): #for parsing cars
            p_lines[i+idx] = p_lines[i+idx].split(":")
            c = Car(p_lines[i+idx][0])
            c.populate_prob(p_lines[i+idx][1])
            self.car_list.append(c)
            j = i+idx
        j += 1
        k = 0
        for idx in range(1, int(p_lines[j])+1): #for parsing drivers
            p_lines[j+idx] = p_lines[j+idx].split(":")
            d = Driver(p_lines[j+idx][0])
            d.populate_prob(p_lines[j+idx][1])
            self.driver_list.append(d)
            k = j+idx
        for idx in range(1, 5): #for parsing tires
            p_lines[k+idx] = p_lines[k+idx].split(":")
            t = Tire(p_lines[k+idx][0])
            t.populate_prob(p_lines[k+idx][1])
            self.tire_list.append(t)
        terr = []
        for idx in range(3, i): #for distributing fuel
            terr.append(p_lines[idx].split(":")[0])
        self.total_terrain = len(terr)
        total_car = int(p_lines[i])
        fuel = p_lines[-2].split()
        fuel_idx = 0
        for t in terr:
            for car in self.car_list:
                car.distribute_consumptions(int(fuel[fuel_idx]), t)
                fuel_idx += 1

class Terrain:
    def __init__(self, terrain_type, slip_prob):
        self.type = terrain_type
        self.slip_prob = slip_prob
        self.num = 0

class Map:
    def __init__(self, length):
        self.length = length
        self.path = [None for i in range(self.length)]

    def populate(self, terrains, slip_prob_str):
        slip_prob_list = slip_prob_str.split()
        idx = 0
        for terrain in terrains:
            t_types, t_num = terrain.split(":")
            for num in t_num.split(","):
                if len(num.split("-")) != 2:
                    path = Terrain(t_types, float(slip_prob_list[idx]))
                    path.num = int(num)-1
                    self.path[int(num)-1] = path
                else:
                    tmp = num.split("-")
                    for i in range(int(tmp[0]), int(tmp[1])+1):
                        path = Terrain(t_types, float(slip_prob_list[idx]))
                        path.num = i-1
                        self.path[i-1] = path
            idx += 1

class Component:
    def __init__(self, name):
        self.name = name
        self.prob = []

    def populate_prob(self, prob_string):
        prob_list = prob_string.split()
        for p in prob_list:
            self.prob.append(float(p))

class Car(Component):
    def __init__(self, name):
        super().__init__(name)
        self.fuel = 50
        self.consumptions = {}

    def distribute_consumptions(self, fuel, terrain):
        self.consumptions[terrain] = int(fuel)

class Driver(Component):
    def __init__(self, name):
        super().__init__(name)

class Tire(Component):
    def __init__(self, name):
        super().__init__(name)
        self.pressure = 100
