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
        self.low_happiness_streak = 0
        self.transport_today = "home"
        
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
        self.transport_today = "home"
        
        print(f"\n--- Day {self.day} ---")
        
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
        
        # Monthly bills and paycheck
        if self.day % 30 == 1:
            self.money -= 1400
            print(f"Paid monthly rent/bills (-$1400)")
            
            if self.money < 0:
                debt = abs(self.money)
                interest = debt * 0.20
                self.money -= interest
                self.happiness -= 12
                print(f"Paid crushing debt interest (-${round(interest)})")
                
                if self.money < -40000 or random.random() < 0.4:
                    self.alive = False
                    self.cause_of_end = "Crushed by debt"
                    return
            
            if self.has_job:
                actual_pay = self.monthly_income * (self.job_stability / 100.0)
                self.money += actual_pay
                print(f"Received paycheck (${round(actual_pay)})")
        
        # Natural decline
        self.health -= 0.03
        self.happiness -= 0.15
        
        # Energy recovery from sleep
        self.energy = min(100.0, self.energy + 45.0)
        
        # AI makes 5+ major decisions each day based on current state
        # Decision 1: Eating plan
        eating_options = ["strict_diet", "balanced", "comfort_eating", "skip_meals"]
        eating_weights = [15, 50, 20, 15]
        if self.bmi() > 28:
            eating_weights[0] += 40
        if self.happiness < 40:
            eating_weights[2] += 50
        if self.money < 800:
            eating_weights[3] += 40
        eating_choice = random.choices(eating_options, weights=eating_weights, k=1)[0]
        print(f"Decision 1 - Eating: {eating_choice.replace('_', ' ')}")
        
        if eating_choice == "strict_diet":
            calories = random.randint(1400, 2000)
        elif eating_choice == "balanced":
            calories = random.randint(2000, 2800)
        elif eating_choice == "comfort_eating":
            calories = random.randint(2800, 3800)
            self.happiness += 12
        else:  # skip_meals
            calories = random.randint(800, 1600)
            self.health -= 1.5
            
        net_calories = calories - 2500
        self.weight += net_calories / 7700.0
        
        # Decision 2: Physical activity
        activity_options = ["intense_workout", "moderate_exercise", "light_walk", "rest"]
        activity_weights = [10, 25, 40, 25]
        if self.bmi() > 27:
            activity_weights[0] += 25
            activity_weights[1] += 20
        if self.energy < 50 or self.sick:
            activity_weights[0] = 0
            activity_weights[1] = 0
            activity_weights[3] += 50
        if self.happiness < 30:
            activity_weights[0:3] = [0, 0, 10]
        activity_choice = random.choices(activity_options, weights=activity_weights, k=1)[0]
        print(f"Decision 2 - Activity: {activity_choice.replace('_', ' ')}")
        
        if activity_choice == "intense_workout":
            self.weight -= random.uniform(0.5, 1.0)
            self.health += 2.0
            self.energy -= 50
            self.happiness += 8
        elif activity_choice == "moderate_exercise":
            self.weight -= random.uniform(0.3, 0.6)
            self.health += 1.2
            self.energy -= 35
            self.happiness += 5
        elif activity_choice == "light_walk":
            self.weight -= random.uniform(0.1, 0.3)
            self.health += 0.5
            self.energy -= 15
            self.happiness += 3
        # rest does nothing extra
        
        # Decision 3: Productivity / daily focus
        if self.has_job:
            focus_options = ["work_overtime", "standard_effort", "coast", "call_in_sick"]
            focus_weights = [15, 60, 20, 5]
            if self.energy < 40 or self.sick:
                focus_weights[3] += 40
            if self.job_stability < 60:
                focus_weights[0] += 30
            focus_choice = random.choices(focus_options, weights=focus_weights, k=1)[0]
            print(f"Decision 3 - Work: {focus_choice.replace('_', ' ')}")
            
            if focus_choice == "call_in_sick":
                missed_work = True
            else:
                missed_work = self.sick
        else:
            focus_options = ["aggressive_job_search", "casual_search", "side_hustle", "do_nothing"]
            focus_weights = [30, 40, 20, 10]
            if self.money < 2000:
                focus_weights[0] += 40
                focus_weights[2] += 20
            focus_choice = random.choices(focus_options, weights=focus_weights, k=1)[0]
            print(f"Decision 3 - Activity: {focus_choice.replace('_', ' ')}")
            missed_work = True  # no job = no commute needed
        
        # Decision 4: Leisure / social
        leisure_options = ["socialize", "personal_hobby", "relax_at_home", "risky_night_out"]
        leisure_weights = [20, 40, 30, 10]
        if self.happiness < 40:
            leisure_weights[0] += 30
            leisure_weights[3] += 20
        if self.money < 800:
            leisure_weights[0] -= 15
            leisure_weights[3] -= 10
        leisure_choice = random.choices(leisure_options, weights=leisure_weights, k=1)[0]
        print(f"Decision 4 - Leisure: {leisure_choice.replace('_', ' ')}")
        
        if leisure_choice == "socialize":
            cost = random.uniform(30, 150)
            self.money -= cost
            self.happiness += random.uniform(10, 25)
        elif leisure_choice == "personal_hobby":
            self.happiness += random.uniform(8, 18)
            self.energy -= 10
        elif leisure_choice == "relax_at_home":
            self.energy += 20
            self.happiness += 5
        elif leisure_choice == "risky_night_out":
            cost = random.uniform(50, 300)
            self.money -= cost
            if random.random() < 0.55:
                self.happiness += 25
            else:
                self.health -= random.uniform(5, 20)
                self.happiness -= 15
        
        # Decision 5: Financial / risk taking
        if self.money > 5000:
            fin_options = ["conservative_saving", "safe_investment", "luxury_spending", "gamble"]
            fin_weights = [50, 25, 15, 10]
            if self.happiness < 40:
                fin_weights[2] += 20
                fin_weights[3] += 20
        else:
            fin_options = ["cut_expenses", "borrow_money", "desperate_gamble", "risky_business"]
            fin_weights = [40, 30, 20, 10]
            if self.money < 1000:
                fin_weights[2] += 30
                fin_weights[3] += 30
        fin_choice = random.choices(fin_options, weights=fin_weights, k=1)[0]
        print(f"Decision 5 - Financial: {fin_choice.replace('_', ' ')}")
        
        if "gamble" in fin_choice:
            bet = random.uniform(300, min(2000, self.money * 0.3))
            self.money -= bet
            if random.random() < 0.3:
                win = bet * random.uniform(2, 6)
                self.money += win
                self.happiness += 30
                print(f"  Gambled and WON ${round(win)}!")
            else:
                self.happiness -= 20
                print(f"  Gambled and lost ${round(bet)}")
        elif "business" in fin_choice and self.money > 8000:
            invest = random.uniform(5000, self.money * 0.5)
            self.money -= invest
            if random.random() < 0.4:
                profit = invest * random.uniform(1.5, 4.0)
                self.money += profit
                self.happiness += 40
                print(f"  Started business - succeeded! Profit ${round(profit)}")
            else:
                self.happiness -= 35
                print(f"  Started business - failed")
        elif "luxury_spending" in fin_choice:
            spend = random.uniform(200, 1000)
            self.money -= spend
            self.happiness += 20
        
        # Medical decision if needed
        if (self.sick or self.health < 50) and self.money > 600:
            medical_chance = 0.6 if self.money > 2000 else 0.25
            if random.random() < medical_chance:
                cost = random.uniform(400, 2000)
                self.money -= cost
                self.health += random.uniform(15, 45)
                if self.sick:
                    self.sick_days_remaining = max(1, self.sick_days_remaining // 2)
                print(f"Sought medical help (-${round(cost)}, health improved)")
        
        # Work / transport handling
        missed_work = self.sick  # default
        if self.has_job:
            if focus_choice == "call_in_sick":
                missed_work = True
                print(f"Called in sick")
            
            if not self.car_working and not missed_work:
                transport_options = ["rideshare", "friend_ride", "walk", "skip_work"]
                transport_weights = [40, 25, 15, 20]
                if self.money < 50:
                    transport_weights[0] = 0
                transport_choice = random.choices(transport_options, weights=transport_weights, k=1)[0]
                self.transport_today = transport_choice
                print(f"Transport choice: {transport_choice.replace('_', ' ')}")
                
                if transport_choice == "rideshare":
                    cost = random.uniform(30, 70)
                    self.money -= cost
                elif transport_choice == "friend_ride":
                    if random.random() < 0.3:
                        missed_work = True
                        print(f"  Friend unavailable - missed work")
                    else:
                        self.happiness += 5
                elif transport_choice == "walk":
                    self.energy -= 35
                    self.health -= 1
                else:
                    missed_work = True
            
            if missed_work:
                self.job_stability -= random.uniform(10, 25)
                self.happiness -= 10
                print(f"Missed work day")
            else:
                self.energy -= 50
                self.happiness -= random.uniform(3, 12)
                self.job_stability += random.uniform(-3, 5)
                if focus_choice == "work_overtime":
                    bonus = random.uniform(60, 200)
                    self.money += bonus
                    self.energy -= 20
                    print(f"Worked overtime (+${round(bonus)})")
        
        # Job search if unemployed
        if not self.has_job and "job_search" in focus_choice:
            if random.random() < 0.18:
                self.has_job = True
                self.monthly_income = random.randint(3500, 6500)
                self.job_stability = 75
                self.happiness += 25
                print(f"Found a new job! (${self.monthly_income}/month)")
        
        # Side hustle if chosen
        if "side_hustle" in focus_choice:
            earnings = random.uniform(-100, 400)
            self.money += earnings
            self.energy -= 30
            if earnings > 0:
                print(f"Side hustle earned ${round(earnings)}")
            else:
                print(f"Side hustle lost ${round(-earnings)}")
        
        # Illness progression
        if self.sick:
            self.sick_days_remaining -= 1
            self.health -= self.sickness_severity * 2.0
            self.energy -= 40
            self.happiness -= 15
            if self.sick_days_remaining <= 0:
                self.sick = False
                print(f"Recovered from illness")
        
        # Random events (kept but slightly less frequent)
        event = random.random()
        if event < 0.18:
            if event < 0.03:
                self.sick = True
                self.sick_days_remaining = random.randint(5, 20)
                self.sickness_severity = random.uniform(5, 10)
                self.happiness -= 20
                print(f"Fell ill")
            elif event < 0.06:
                if self.car_working:
                    self.car_working = False
                    self.car_repair_cost = random.uniform(1500, 7000)
                    print(f"Car broke down (repair ~${round(self.car_repair_cost)})")
            # ... (other events kept similar but omitted here for brevity in planning)
        
        # Car repair attempt
        if not self.car_working and self.money > self.car_repair_cost + 2000 and random.random() < 0.5:
            self.money -= self.car_repair_cost
            self.car_working = True
            print(f"Repaired car (-${round(self.car_repair_cost)})")
        
        # Suicide risk
        if self.happiness < 20:
            self.low_happiness_streak += 1
        else:
            self.low_happiness_streak = 0
            
        if self.low_happiness_streak > 6 and random.random() < 0.35:
            self.alive = False
            self.cause_of_end = "Suicide from prolonged despair"
            print(f"!!! Ended in suicide")
            return
        
        # Violent / accidental death risk
        death_risk = 0.001
        if self.transport_today == "walk":
            death_risk += 0.018
        if self.transport_today in ["rideshare", "friend_ride"]:
            death_risk += 0.003
        if self.car_working and self.transport_today != "home":
            death_risk += 0.007
        if self.money < 500:
            death_risk += 0.012
        if random.random() < death_risk:
            causes = []
            if "walk" in self.transport_today:
                causes.append("hit by vehicle")
            if self.car_working:
                causes.append("car accident")
            causes.append("murdered")
            self.cause_of_end = random.choice(causes)
            self.alive = False
            print(f"!!! Sudden death: {self.cause_of_end}")
            return
        
        # Death from poor health
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
    
    print(f"30-Day AI Human Life Simulation with Extensive Daily Decisions (seed {seed})")
    print("The AI now makes at least 5 major state-based decisions per day,")
    print("facing complex trade-offs. Multiple possible endings including suicide,")
    print("accidents, and murder. Outcomes vary widely.\n")
    
    while sim.day < days and sim.alive:
        sim.daily_routine()
    
    df = pd.DataFrame(sim.logs)
    
    fig, axs = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle('AI Human Life Simulation - 30 Days with Complex Decisions', fontsize=16)
    
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
    
    final = df.iloc[-1] if not df.empty else None
    print("\n=== SIMULATION END ===")
    if final is not None:
        print(f"Ended on day {int(final['day'])} (age ~{final['age']})")
    if not sim.alive:
        print(f"CAUSE: {sim.cause_of_end}")
    else:
        print("Survived the 30-day period.")
    
    if final is not None:
        print(f"Final weight: {final['weight']} kg (BMI {final['bmi']})")
        print(f"Final money: ${final['money']}")
        print(f"Final health: {final['health']}/100")
        print(f"Final happiness: {final['happiness']}/100")
        print(f"Had job: {final['has_job']}")
        print(f"Car working: {final['car_working']}")

if __name__ == "__main__":
    run_simulation(days=30, seed=12345)