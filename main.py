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
            print(f"Day {self.day}: Paid monthly rent/bills (-$1400)")
            
            if self.money < 0:
                debt = abs(self.money)
                interest = debt * 0.20
                self.money -= interest
                self.happiness -= 12
                print(f"Day {self.day}: Paid crushing debt interest (-${round(interest)})")
                
                if self.money < -40000 or random.random() < 0.4:
                    self.alive = False
                    self.cause_of_end = "Crushed by debt"
                    return
                    
            if self.has_job:
                actual_pay = self.monthly_income * (self.job_stability / 100.0)
                self.money += actual_pay
                print(f"Day {self.day}: Received paycheck (${round(actual_pay)})")
        
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
            print(f"Day {self.day}: Fell seriously ill")
        elif event < 0.05:
            if self.car_working:
                self.car_working = False
                self.car_repair_cost = random.uniform(1500, 8000)
                self.happiness -= 20
                print(f"Day {self.day}: Car broke down (repair cost ~${round(self.car_repair_cost)})")
        elif event < 0.07:
            self.health -= random.uniform(40, 80)
            self.money -= random.uniform(8000, 30000)
            self.happiness -= 45
            self.sick = True
            self.sick_days_remaining = random.randint(20, 90)
            print(f"Day {self.day}: Major accident/injury")
        elif event < 0.10:
            cost = random.uniform(800, 6000)
            self.money -= cost
            self.happiness -= 15
            print(f"Day {self.day}: Unexpected expense (-${round(cost)})")
        elif event < 0.13:
            loss = random.uniform(2000, 15000)
            self.money -= loss
            self.happiness -= 30
            print(f"Day {self.day}: Theft/robbery (-${round(loss)})")
        elif event < 0.15:
            cost = random.uniform(4000, 20000)
            self.money -= cost
            self.happiness -= 35
            print(f"Day {self.day}: Helped family/friend with emergency (-${round(cost)})")
        elif event < 0.17:
            cost = random.uniform(6000, 40000)
            self.money -= cost
            self.happiness -= 40
            if self.has_job and random.random() < 0.5:
                self.has_job = False
                self.happiness -= 25
                print(f"Day {self.day}: Legal trouble (-${round(cost)}, lost job)")
            else:
                print(f"Day {self.day}: Legal trouble (-${round(cost)})")
        elif event < 0.19:
            cost = random.uniform(12000, 60000)
            self.money -= cost
            self.happiness -= 45
            print(f"Day {self.day}: Major home damage (-${round(cost)})")
        elif event < 0.20:
            self.happiness -= random.uniform(40, 70)
            self.health -= 30
            self.money -= random.uniform(5000, 25000)
            self.sick = True
            self.sick_days_remaining = random.randint(30, 180)
            print(f"Day {self.day}: Mental health crisis")
        elif event < 0.205:
            gain = random.uniform(500, 3000)
            self.money += gain
            self.happiness += 10
            print(f"Day {self.day}: Small windfall (+${round(gain)})")
        elif event < 0.21:
            if self.has_job:
                raise_amt = random.randint(500, 1500)
                self.monthly_income += raise_amt
                self.happiness += 10
                print(f"Day {self.day}: Got a raise (+${raise_amt}/month)")
        
        # Car management (attempt repair outside of immediate work pressure)
        if not self.car_working and self.car_repair_cost > 0:
            repair_chance = 0.4
            if self.has_job:
                repair_chance += 0.4
            if self.money < 2000:
                repair_chance -= 0.3
            if self.money >= self.car_repair_cost + 1000 and random.random() < repair_chance:
                print(f"Day {self.day}: Decided to repair car (${round(self.car_repair_cost)})")
                self.money -= self.car_repair_cost
                self.car_working = True
                self.car_repair_cost = 0
                self.happiness += 10
        
        # Work and transport decisions
        if self.has_job:
            missed_work = self.sick
            if self.sick:
                print(f"Day {self.day}: Too sick to go to work")
            
            if not self.car_working and not self.sick:
                # Build available options
                options = ["skip"]
                weights = [1]
                
                if self.money >= 30:
                    options.append("rideshare")
                    weights.append(5)  # strongly prefer if affordable
                
                options.append("friend")
                weights.append(3)
                
                options.append("walk")
                weights.append(2 if self.energy > 50 else 1)  # less likely if tired
                
                choice = random.choices(options, weights=weights, k=1)[0]
                
                if choice == "rideshare":
                    cost = random.uniform(25, 55)
                    self.money -= cost
                    print(f"Day {self.day}: Took ride-share to work (-${round(cost)})")
                elif choice == "friend":
                    if random.random() < 0.65:
                        print(f"Day {self.day}: Got a ride from a friend")
                        self.happiness += 5
                    else:
                        print(f"Day {self.day}: Friend unavailable - skipped work")
                        missed_work = True
                elif choice == "walk":
                    print(f"Day {self.day}: Walked to work (tiring)")
                    self.energy -= 30
                    self.health -= 0.8
                    self.happiness -= 5
                elif choice == "skip":
                    missed_work = True
                    print(f"Day {self.day}: No viable transport - skipped work")
            
            if missed_work:
                self.job_stability -= random.uniform(12, 25)
                self.happiness -= 8
            else:
                self.energy -= 55
                self.happiness -= random.uniform(5, 15)
                self.job_stability += random.uniform(-2, 4)
        
        # Job search when unemployed
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
                    print(f"Day {self.day}: Landed a new job! (${self.monthly_income}/month)")
        
        # Gambling temptation
        gamble_chance = 0.04
        if self.happiness < 40:
            gamble_chance += 0.10
        if self.money < 3000:
            gamble_chance += 0.08
        if random.random() < gamble_chance and self.money > 400:
            bet = random.uniform(200, min(1500, self.money * 0.25))
            print(f"Day {self.day}: Feeling desperate/lucky - gambled ${round(bet)}")
            self.money -= bet
            if random.random() < 0.28:
                winnings = bet * random.uniform(2, 7)
                self.money += winnings
                print(f"Day {self.day}: Won ${round(winnings)}! Big mood boost")
                self.happiness += 30
            else:
                print(f"Day {self.day}: Lost the gamble")
                self.happiness -= 18
        
        # Business risk when unemployed and have capital
        if not self.has_job and self.money > 12000 and random.random() < 0.25:
            invest = random.uniform(8000, self.money * 0.6)
            print(f"Day {self.day}: Took a big risk - started a business (${round(invest)} invested)")
            self.money -= invest
            success_chance = 0.35
            if self.happiness > 60:
                success_chance += 0.15
            if random.random() < success_chance:
                profit = invest * random.uniform(1.8, 4.5)
                self.money += profit
                self.monthly_income += profit / 20
                print(f"Day {self.day}: Business is thriving! Profit ${round(profit)}")
                self.happiness += 40
            else:
                print(f"Day {self.day}: Business failed or stalled")
                self.happiness -= 35
        
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

def run_simulation(days=30, seed=12345):
    sim = LifeSimulation(seed=seed)
    
    print(f"Simulating 30 days of AI human life with daily decisions (seed {seed})")
    print("The AI will face challenges and make choices about transport, risks, gambling, business, etc.\n")
    
    while sim.day < days and sim.alive:
        sim.daily_routine()
    
    df = pd.DataFrame(sim.logs)
    
    # Plot results
    fig, axs = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle('AI Human Life Simulation - 30 Days with Decisions', fontsize=16)
    
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
    print("\n=== 30-DAY SIMULATION END ===")
    if final is not None:
        print(f"Ended on day {int(final['day'])} (age ~{final['age']})")
    if not sim.alive:
        print(f"CAUSE: {sim.cause_of_end}")
    else:
        print("Completed the 30-day period.")
    
    if final is not None:
        print(f"Final weight: {final['weight']} kg (BMI {final['bmi']})")
        print(f"Final money: ${final['money']}")
        print(f"Final health: {final['health']}/100")
        print(f"Final happiness: {final['happiness']}/100")
        print(f"Had job: {final['has_job']}")
        print(f"Car working: {final['car_working']}")

if __name__ == "__main__":
    run_simulation(days=30, seed=12345)