import random
import math
from config import *

class Individual:
    def __init__(self, x, y, state):
        self.x = x
        self.y = y
        self.state = state
        self.radius = 6
        
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 3.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.death_timer = 0
        self.initial_death_timer = 0
        self.reinfection_prob = 0.0

    def infect(self, death_timer_val):
        self.state = INFECTED
        self.death_timer = death_timer_val
        self.initial_death_timer = self.death_timer

    def move(self):
        if self.state == DEAD:
            return
            
        self.x += self.vx
        self.y += self.vy
        
        if self.x - self.radius < 0 or self.x + self.radius > SIM_WIDTH:
            self.vx *= -1
            self.x = max(self.radius, min(self.x, SIM_WIDTH - self.radius))
            
        if self.y - self.radius < 0 or self.y + self.radius > SIM_HEIGHT:
            self.vy *= -1
            self.y = max(self.radius, min(self.y, SIM_HEIGHT - self.radius))

    def update_infection(self, immunity_prob, inf_prob):
        if self.state == INFECTED:
            if random.random() < immunity_prob:
                self.state = IMMUNE
                self.reinfection_prob = inf_prob * (self.death_timer / max(1, self.initial_death_timer))
                return
                
            self.death_timer -= 1
            if self.death_timer <= 0:
                self.state = DEAD

class Simulation:
    def __init__(self):
        self.population = []
        self.history = {SUSCEPTIBLE: [], INFECTED: [], IMMUNE: [], DEAD: []}
        self.frames_passed = 0
        self.is_running = False
        
    def restart(self, num_individuals):
        self.population = []
        self.history = {SUSCEPTIBLE: [], INFECTED: [], IMMUNE: [], DEAD: []}
        self.frames_passed = 0
        self.is_running = True
        self.num_individuals = num_individuals
        
        for i in range(num_individuals):
            x = random.randint(20, SIM_WIDTH - 20)
            y = random.randint(20, SIM_HEIGHT - 20)
            state = INFECTED if i < INITIAL_INFECTED else SUSCEPTIBLE
            ind = Individual(x, y, state)
            self.population.append(ind)

    def step(self, radius, inf_prob, immunity_prob, death_timer_val, is_paused):
        if not self.is_running or is_paused:
            return self.get_stats()
            
        self.frames_passed += 1

        for p in self.population:
            p.move()
            p.update_infection(immunity_prob, inf_prob)
            
        infected_pop = [p for p in self.population if p.state == INFECTED]
        susceptible_pop = [p for p in self.population if p.state == SUSCEPTIBLE]
        immune_pop = [p for p in self.population if p.state == IMMUNE]
        
        radius_sq = radius * radius
        
        for inf in infected_pop:
            for sus in susceptible_pop:
                if abs(inf.x - sus.x) <= radius and abs(inf.y - sus.y) <= radius:
                    dx = inf.x - sus.x
                    dy = inf.y - sus.y
                    if (dx*dx + dy*dy) < radius_sq:
                        if random.random() < inf_prob:
                            sus.infect(death_timer_val)
                            susceptible_pop.remove(sus)
                            
            for imm in immune_pop:
                if abs(inf.x - imm.x) <= radius and abs(inf.y - imm.y) <= radius:
                    dx = inf.x - imm.x
                    dy = inf.y - imm.y
                    if (dx*dx + dy*dy) < radius_sq:
                        if random.random() < imm.reinfection_prob:
                            imm.infect(death_timer_val)
                            immune_pop.remove(imm)

        stats = self.get_stats()
        
        if stats[INFECTED] == 0:
            self.is_running = False
            
        for state in self.history:
            self.history[state].append(stats[state])
            if len(self.history[state]) > GRAPH_WIDTH:
                self.history[state].pop(0)
                
        return stats

    def get_stats(self):
        s_count = 0
        i_count = 0
        im_count = 0
        d_count = 0
        for p in self.population:
            if p.state == SUSCEPTIBLE: s_count += 1
            elif p.state == INFECTED: i_count += 1
            elif p.state == IMMUNE: im_count += 1
            elif p.state == DEAD: d_count += 1
            
        return {
            SUSCEPTIBLE: s_count,
            INFECTED: i_count,
            IMMUNE: im_count,
            DEAD: d_count
        }
