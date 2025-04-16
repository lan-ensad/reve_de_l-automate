import time

class SpeedCalculator:
    def __init__(self, sample_time, steps_per_cm):
        self.last_time = time.ticks_ms()  # ms
        self.last_flagA = 0
        self.last_flagB = 0
        self.sample_time = sample_time # ms
        self.steps_per_cm = steps_per_cm
        self.speed = 0.0
        
    def calc_speed(self, flagA, flagB):
        current_time = time.ticks_ms()
        elapsed_time = time.ticks_diff(current_time, self.last_time) / 1000  # ms → s
        
        if elapsed_time >= self.sample_time / 1000:
            delta_steps = (flagA - self.last_flagA) - (flagB - self.last_flagB)

            distance = delta_steps / self.steps_per_cm
            
            self.speed = distance / elapsed_time
            
            self.last_time = current_time
            self.last_flagA = flagA
            self.last_flagB = flagB

        return round(self.speed, 2)
