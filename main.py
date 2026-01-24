import random
import matplotlib.pyplot as plt
import pandas as pd

class LifeSimulation:
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
        
        # Starting state
        self.day = 0
        self.age = 25.0
        self.weight = 75.0
        self.height = 1.75
        self.health = 100.0
        self.energy = 100.0
        self.happiness = 50.0
        self.money = 15000.0
        self.monthly_income = 4500 if random.random() > 0.15 else 0
        self.has_job = self.monthly_income > 0
        self.job_stability = 100.0
        self.car_working = True
        self.car_repair_cost = 0
        self.sick = False
        self.sick_days_remaining = 0
        self.sickness_severity = 0
        self.alive = True
        self.cause_of_end = None
        
        self.logs = []
        
    def bmi(self):
        return round(self.weight / (self.height ** 2), 1)
        
    def log_day(self):
        self.logs.append({
            'day': self.day,
            'age': round(self.age, 1),
            'weight': round(self.weight, 1),
            'bmi': self.bmi(),
            'health': round(self.health),
            'energy': round(self.energy),
            'happiness': round(self.happiness),
            'money': round(self.money, 2),
            'has_job': self.has_job,
            'car_working': self.car_working,
            'sick': self.sick
        })
        
    def daily_routine(self):
        if not self.alive:
            return
            
        # Advance time
        self.day += 1
        self.age += 1/365.0
        
        # Daily living costs
        daily_cost = random.uniform(50, 90)
        if self.money < 1000:
            daily_cost = random.uniform(30, 60)
        self.money -= daily_cost
        
        # Poverty penalties
        if self.money < 500:
            self.health -= 0.5
            self.happiness -= 1
        if self.money < 0:
            self.health -= 0.8
            self.happiness -= 3
        
        # Monthly bills and debt
        if self.day % 30 == 1:
            self.money -= 1400
            
            if self.money < 0:
                debt = abs(self.money)
                interest = debt * 0.20
                self.money -= interest
                self.happiness -= 12
                
                if self.money < -40000 or random.random() < 0.4:
                    self.alive = False
                    self.cause_of_end = "Crushed by debt"
                    return
        
        # Natural decline
        self.health -= 0.03
        self.happiness -= 0.15
        
        # Energy recovery
        self.energy = min(100.0, self.energy + 45.0)
        
        # Food intake and weight change
        target_weight = 75.0
        bmi_current = self.bmi()
        
        base_calories = random.randint(2200, 2800)
        if self.weight > target_weight + 10:
            base_calories = random.randint(1500, 2200)
        elif self.weight < target_weight - 10:
            base_calories = random.randint(2800, 3600)
            
        if self.happiness < 40:
            base_calories += random.randint(400, 1000)
        if self.happiness < 20:
            base_calories += random.randint(600, 1400)
            
        if self.money < 500:
            base_calories = random.randint(1200, 2000)
            
        if self.sick:
            base_calories = int(base_calories * 0.5)
            
        net_calories = base_calories - 2500
        self.weight += net_calories / 7700.0
        
        # Exercise decision
        exercise_chance = 0.1
        if bmi_current > 28:
            exercise_chance += 0.4
        if self.happiness < 40:
            exercise_chance -= 0.3
        if self.happiness < 20:
            exercise_chance = 0
        if self.money < 500:
            exercise_chance -= 0.2
            
        if random.random() < exercise_chance and self.energy > 40 and not self.sick:
            self.weight -= random.uniform(0.3, 0.7)
            self.health += 1.0
            self.energy -= 40
            self.happiness += 2
        
        # Work and job mechanics
        if self.has_job:
            if self.sick or (not self.car_working and random.random() < 0.6):
                self.job_stability -= random.uniform(12, 25)
                self.happiness -= 8
            else:
                self.energy -= 55
                self.happiness -= random.uniform(5, 15)
                self.job_stability += random.uniform(-2, 4)
                
            if self.day % 30 == 1:
                actual_pay = self.monthly_income * (self.job_stability / 100.0)
                self.money += actual_pay
                
            if self.job_stability < 20 and random.random() < 0.5:
                self.has_job = False
                self.monthly_income = 0
                self.job_stability = 0
                self.happiness -= 30
        else:
            search_chance = 0.3
            if self.money < 2000:
                search_chance = 0.7
            if self.happiness < 30:
                search_chance *= 0.4
            if random.random() < search_chance:
                if random.random() < 0.1:
                    self.has_job = True
                    self.monthly_income = random.randint(3000, 6000)
                    self.job_stability = 70
                    self.happiness += 20
        
        # Illness progression
        if self.sick:
            self.sick_days_remaining -= 1
            self.health -= self.sickness_severity * 2.0
            self.energy -= 40
            self.happiness -= 15
            if random.random() < 0.4:
                self.money -= random.uniform(300, 1200)
            if self.sick_days_remaining <= 0:
                self.sick = False
                
        # Random events (mostly negative)
        event = random.random()
        if event < 0.025:
            self.sick = True
            self.sick_days_remaining = random.randint(4, 25)
            self.sickness_severity = random.uniform(4, 12)
            if self.bmi() > 30:
                self.sickness_severity += 4
            if self.health < 50:
                self.sickness_severity += 3
            self.happiness -= 25
        elif event < 0.05:
            if self.car_working:
                self.car_working = False
                self.car_repair_cost = random.uniform(1500, 8000)
                self.happiness -= 20
        elif event < 0.07:
            self.health -= random.uniform(40, 80)
            self.money -= random.uniform(8000, 30000)
            self.happiness -= 45
            self.sick = True
            self.sick_days_remaining = random.randint(20, 90)
        elif event < 0.10:
            self.money -= random.uniform(800, 6000)
            self.happiness -= 15
        elif event < 0.13:
            self.money -= random.uniform(2000, 15000)
            self.happiness -= 30
        elif event < 0.15:
            self.money -= random.uniform(4000, 20000)
            self.happiness -= 35
        elif event < 0.17:
            self.money -= random.uniform(6000, 40000)
            self.happiness -= 40
            if self.has_job and random.random() < 0.5:
                self.has_job = False
                self.happiness -= 25
        elif event < 0.19:
            self.money -= random.uniform(12000, 60000)
            self.happiness -= 45
        elif event < 0.20:
            self.happiness -= random.uniform(40, 70)
            self.health -= 30
            self.money -= random.uniform(5000, 25000)
            self.sick = True
            self.sick_days_remaining = random.randint(30, 180)
        elif event < 0.202:
            self.money += random.uniform(500, 3000)
            self.happiness += 10
        elif event < 0.203:
            if self.has_job:
                self.monthly_income += random.randint(500, 1500)
                self.happiness += 10
        
        # Car repair attempt
        if not self.car_working:
            if self.money > self.car_repair_cost + 3000 and random.random() < 0.3:
                self.money -= self.car_repair_cost
                self.car_working = True
        
        # Death check
        if self.health <= 0:
            self.alive = False
            self.cause_of_end = "Death from poor health"
        
        # Clamp values
        self.health = max(0.0, min(100.0, self.health))
        self.energy = max(0.0, min(100.0, self.energy))
        self.happiness = max(0.0, min(100.0, self.happiness))
        self.job_stability = max(0.0, min(100.0, self.job_stability))
        
        self.log_day()

def run_simulation(days=3650, seed=42):
    sim = LifeSimulation(seed=seed)
    
    print(f"Ultra-Ruthless Life Simulation (seed {seed}) - {days} days")
    print("Negative events are frequent. Debt snowballs. Survival is rare.\n")
    
    while sim.day < days and sim.alive:
        sim.daily_routine()
    
    df = pd.DataFrame(sim.logs)
    
    # Plot results
    fig, axs = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle('Ultra-Ruthless AI Human Life Simulation', fontsize=16)
    
    axs[0,0].plot(df['day'], df['weight'], color='blue')
    axs[0,0].set_title('Weight (kg)')
    
    axs[0,1].plot(df['day'], df['money'], color='green')
    axs[0,1].set_title('Bank Balance ($)')
    
    axs[1,0].plot(df['day'], df['health'], color='red')
    axs[1,0].set_title('Health')
    
    axs[1,1].plot(df['day'], df['happiness'], color='orange')
    axs[1,1].set_title('Happiness')
    
    axs[2,0].plot(df['day'], df['bmi'], color='purple')
    axs[2,0].set_title('BMI')
    axs[2,0].set_xlabel('Day')
    
    axs[2,1].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    # Final summary
    final = df.iloc[-1] if not df.empty else None
    print("\n=== SIMULATION END ===")
    if final is not None:
        print(f"Ended on day {int(final['day'])} (age ~{final['age']})")
    if not sim.alive:
        print(f"CAUSE: {sim.cause_of_end}")
    else:
        print("Miraculously survived the full period.")
    
    if final is not None:
        print(f"Final weight: {final['weight']} kg (BMI {final['bmi']})")
        print(f"Final money: ${final['money']}")
        print(f"Final health: {final['health']}/100")
        print(f"Final happiness: {final['happiness']}/100")
        print(f"Had job: {final['has_job']}")
        print(f"Car working: {final['car_working']}")

if __name__ == "__main__":
    run_simulation(days=3650, seed=12345)