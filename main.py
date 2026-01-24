import random
import matplotlib.pyplot as plt
import pandas as pd

class LifeSimulation:
    def __init__(self, seed=None, verbose=False):
        if seed is not None:
            random.seed(seed)
        self.verbose = verbose
        
        # Core state
        self.day = 0
        self.age = 25.0
        self.weight = 75.0
        self.height = 1.75
        self.health = 100.0
        self.mental_health = 100.0  # New: separate from happiness
        self.energy = 100.0
        self.happiness = 50.0
        self.money = 15000.0
        self.debt = 0.0
        self.monthly_income = 4500 if random.random() > 0.15 else 0
        self.has_job = self.monthly_income > 0
        self.job_stability = 100.0
        self.skill_level = 1.0
        self.social_support = 50.0
        self.car_working = True
        self.car_repair_cost = 0
        self.has_health_insurance = False
        self.has_emergency_fund = self.money >= 5000
        self.has_retirement_savings = 0.0
        self.investments = 0.0  # Stock/bond portfolio
        self.sick = False
        self.sick_days_remaining = 0
        self.sickness_severity = 0
        self.low_happiness_streak = 0
        self.alive = True
        self.cause_of_end = None
        self.transport_today = "home"
        self.net_worth_history = []
        self.event_log = []  # For summary report
        
        self.logs = []
        
    def bmi(self):
        return round(self.weight / (self.height ** 2), 1)
    
    def update_net_worth(self):
        net_worth = self.money + self.investments + self.has_retirement_savings - self.debt
        self.net_worth_history.append(net_worth)
    
    def log_event(self, msg):
        self.event_log.append(f"Day {self.day}: {msg}")
        if self.verbose:
            print(msg)
    
    def log_day(self):
        self.logs.append({
            'day': self.day,
            'age': round(self.age, 1),
            'weight': round(self.weight, 1),
            'bmi': self.bmi(),
            'health': round(self.health),
            'mental_health': round(self.mental_health),
            'energy': round(self.energy),
            'happiness': round(self.happiness),
            'money': round(self.money, 2),
            'debt': round(self.debt, 2),
            'investments': round(self.investments, 2),
            'retirement': round(self.has_retirement_savings, 2),
            'net_worth': round(self.money + self.investments + self.has_retirement_savings - self.debt, 2),
            'skill_level': round(self.skill_level, 2),
            'social_support': round(self.social_support, 1),
            'has_job': self.has_job,
            'car_working': self.car_working,
            'sick': self.sick
        })
        self.update_net_worth()
        
    def make_decision(self, category, options, base_weights):
        adjusted_weights = base_weights[:]
        
        survival_priority = max(0, (30 - self.health)/30 + (1000 - self.money)/1000 if self.money < 1000 else 0)
        happiness_priority = max(0, (40 - self.happiness)/40)
        career_priority = max(0, 1 - self.skill_level) if not self.has_job else (1 - self.job_stability/100)
        
        if category == "eating":
            if survival_priority > 0.5:
                adjusted_weights[options.index("balanced_meals")] += 30
                adjusted_weights[options.index("strict_diet")] += 20
            if happiness_priority > 0.4:
                adjusted_weights[options.index("comfort_eating")] += 25
        
        elif category == "activity":
            if survival_priority > 0.4:
                adjusted_weights[options.index("moderate_exercise")] += 30
            if happiness_priority > 0.3:
                adjusted_weights[options.index("light_walk")] += 20
        
        elif category == "financial":
            if survival_priority > 0.6:
                adjusted_weights[options.index("build_emergency_fund")] += 50
                adjusted_weights[options.index("pay_down_debt")] += 40
            if career_priority > 0.3:
                adjusted_weights[options.index("invest_in_skills")] += 35
            if happiness_priority > 0.5 and self.money > 3000:
                adjusted_weights[options.index("small_treat")] += 15
            if self.money > 10000:
                adjusted_weights[options.index("contribute_retirement")] += 20
        
        total = sum(adjusted_weights)
        if total > 0:
            adjusted_weights = [w / total for w in adjusted_weights]
        else:
            adjusted_weights = [1/len(options)] * len(options)
        
        return random.choices(options, weights=adjusted_weights, k=1)[0]
    
    def daily_routine(self):
        if not self.alive:
            return
            
        self.day += 1
        self.age += 1/365.0
        self.transport_today = "home"
        
        if self.verbose:
            print(f"\n--- Day {self.day} (Age {self.age:.1f}) ---")
            print(f"Status: Health {self.health:.0f} | Mental {self.mental_health:.0f} | Happiness {self.happiness:.0f} | Money ${self.money:.0f} | Debt ${self.debt:.0f}")
        
        # Daily costs + inflation (0.02% monthly increase in base costs)
        inflation_factor = 1 + (self.day // 30) * 0.0002
        daily_cost = random.uniform(50, 90) * inflation_factor if self.money >= 1000 else random.uniform(30, 60) * inflation_factor
        self.money -= daily_cost
        
        # Poverty / debt effects
        if self.money < 500:
            self.health -= 0.5
            self.mental_health -= 1.0
            self.happiness -= 1.2
        if self.money < 0:
            self.debt += abs(self.money)
            self.money = 0
            self.health -= 0.8
            self.mental_health -= 2.0
            self.happiness -= 4
        
        # Monthly cycle: bills, taxes (10% income tax), paycheck
        if self.day % 30 == 1:
            self.money -= 1400 * inflation_factor
            if self.debt > 0:
                interest = self.debt * 0.08
                self.debt += interest
                self.money -= min(interest, self.money)
                self.mental_health -= 8 if self.debt > 5000 else 3
            
            if self.has_job:
                gross_pay = self.monthly_income * (self.job_stability / 100) * (1 + (self.skill_level - 1)*0.3)
                tax = gross_pay * 0.10
                pay = gross_pay - tax
                self.money += pay
                self.has_retirement_savings += gross_pay * 0.05  # auto 5% contribution
                if self.verbose:
                    print(f"Paycheck: +${pay:.0f} (after tax)")
                self.log_event(f"Paycheck received: +${pay:.0f}")
        
        # Natural changes
        self.health -= 0.02
        self.mental_health -= 0.05
        self.happiness -= 0.1
        self.energy = min(100, self.energy + 45)
        
        # Decision 1: Eating
        eating_options = ["strict_diet", "balanced_meals", "comfort_eating", "cheap_basic"]
        eating_weights = [20, 60, 10, 10]
        eating_choice = self.make_decision("eating", eating_options, eating_weights)
        if self.verbose:
            print(f"Eating: {eating_choice.replace('_', ' ')}")
        
        if eating_choice == "strict_diet":
            calories = random.randint(1400, 1900)
            self.health += 0.5
        elif eating_choice == "balanced_meals":
            calories = random.randint(2100, 2700)
            self.health += 0.8
            self.mental_health += 0.5
        elif eating_choice == "comfort_eating":
            calories = random.randint(2800, 3800)
            self.happiness += 15
            self.mental_health += 5
            self.money -= 20
        else:
            calories = random.randint(1200, 2000)
            self.money -= 10
            self.health -= 0.5
        net_calories = calories - 2500
        self.weight += net_calories / 7700.0
        
        # Decision 2: Activity
        activity_options = ["intense_gym", "moderate_exercise", "light_walk", "rest_day"]
        activity_weights = [15, 40, 30, 15]
        activity_choice = self.make_decision("activity", activity_options, activity_weights)
        if self.verbose:
            print(f"Activity: {activity_choice.replace('_', ' ')}")
        
        if activity_choice == "intense_gym":
            self.weight -= random.uniform(0.4, 0.9)
            self.health += 1.8
            self.mental_health += 3
            self.energy -= 45
            self.happiness += 10
            self.money -= 10 if random.random() < 0.3 else 0
        elif activity_choice == "moderate_exercise":
            self.weight -= random.uniform(0.2, 0.5)
            self.health += 1.2
            self.mental_health += 2
            self.energy -= 30
            self.happiness += 6
        elif activity_choice == "light_walk":
            self.weight -= random.uniform(0.1, 0.3)
            self.health += 0.6
            self.mental_health += 1
            self.energy -= 15
            self.happiness += 4
        
        # Decision 3: Career/Productivity
        if self.has_job:
            career_options = ["work_hard_promotion", "standard_effort", "upskill_after_work", "call_in_sick"]
            career_weights = [25, 50, 20, 5]
            if self.job_stability > 80:
                career_weights[0] += 20
            career_choice = self.make_decision("career", career_options, career_weights)
            if self.verbose:
                print(f"Career: {career_choice.replace('_', ' ')}")
            
            if career_choice == "work_hard_promotion":
                self.job_stability += random.uniform(3, 8)
                self.energy -= 60
                if random.random() < 0.15 * self.skill_level:
                    self.monthly_income += random.randint(400, 1200)
                    self.skill_level += 0.1
                    self.log_event("Promotion! Income increased")
            elif career_choice == "upskill_after_work":
                self.skill_level += random.uniform(0.02, 0.08)
                self.energy -= 25
                self.mental_health += 5 if self.skill_level > 1.2 else 0
            elif career_choice == "call_in_sick":
                self.job_stability -= 15
        else:
            career_options = ["intensive_job_hunt", "networking", "upskill_full_time", "side_gig"]
            career_weights = [40, 30, 25, 5]
            if self.money < 3000:
                career_weights[0] += 30
                career_weights[3] += 20
            career_choice = self.make_decision("career", career_options, career_weights)
            if self.verbose:
                print(f"Career: {career_choice.replace('_', ' ')}")
            
            if career_choice == "intensive_job_hunt":
                if random.random() < 0.22 + (self.skill_level * 0.1):
                    self.has_job = True
                    self.monthly_income = random.randint(3800, 6800) * self.skill_level
                    self.job_stability = 75
                    self.happiness += 30
                    self.log_event("New job landed!")
            elif career_choice == "upskill_full_time":
                self.skill_level += random.uniform(0.05, 0.15)
                self.energy -= 40
            elif career_choice == "side_gig":
                earnings = random.uniform(-100, 600)
                self.money += earnings
                self.energy -= 30
                if earnings > 0:
                    self.log_event(f"Side gig earned ${earnings:.0f}")
                else:
                    self.log_event(f"Side gig cost ${-earnings:.0f}")
        
        # Decision 4: Social / Mental health
        social_options = ["call_friend_family", "join_community", "solitary_hobby", "date_night", "vacation_day"]
        social_weights = [35, 25, 30, 10, 0]
        if self.mental_health < 60:
            social_weights[0] += 30
            social_weights[1] += 20
        if self.happiness < 50:
            social_weights[4] += 25
        social_choice = self.make_decision("social", social_options, social_weights)
        if self.verbose:
            print(f"Social: {social_choice.replace('_', ' ')}")
        
        if social_choice == "call_friend_family":
            self.social_support += random.uniform(2, 8)
            self.happiness += random.uniform(8, 20)
            self.mental_health += 10
        elif social_choice == "join_community":
            cost = random.uniform(20, 80)
            self.money -= cost
            self.social_support += random.uniform(5, 15)
            self.happiness += random.uniform(10, 25)
            self.mental_health += 12
        elif social_choice == "date_night":
            cost = random.uniform(80, 250)
            self.money -= cost
            if random.random() < 0.6:
                self.happiness += 25
                self.social_support += 10
                self.mental_health += 15
            else:
                self.happiness -= 10
                self.mental_health -= 8
        elif social_choice == "vacation_day":
            cost = random.uniform(300, 800)
            if self.money >= cost:
                self.money -= cost
                self.happiness += 40
                self.mental_health += 30
                self.energy = 100
                self.log_event("Took a vacation day - refreshed")
        
        # Decision 5: Financial
        financial_options = ["build_emergency_fund", "pay_down_debt", "invest_in_skills", "small_treat", "safe_investment", "contribute_retirement", "risky_investment"]
        financial_weights = [40, 30, 20, 5, 5, 0, 0]
        if self.debt > 0:
            financial_weights[1] += 40
        if not self.has_emergency_fund:
            financial_weights[0] += 50
        if self.skill_level < 1.5:
            financial_weights[2] += 30
        if self.happiness < 35:
            financial_weights[3] += 15
        if self.money > 10000:
            financial_weights[4] += 25
            financial_weights[5] += 20
            financial_weights[6] += 5 if self.mental_health > 80 else 0
        financial_choice = self.make_decision("financial", financial_options, financial_weights)
        if self.verbose:
            print(f"Financial: {financial_choice.replace('_', ' ')}")
        
        if financial_choice == "build_emergency_fund":
            save = min(500, self.money * 0.1)
            self.money -= save
            self.has_emergency_fund = True if self.money >= 5000 else False
        elif financial_choice == "pay_down_debt":
            pay = min(1000, self.money * 0.2, self.debt)
            self.debt -= pay
            self.money -= pay
        elif financial_choice == "invest_in_skills":
            cost = random.uniform(200, 800)
            if self.money >= cost:
                self.money -= cost
                self.skill_level += random.uniform(0.05, 0.12)
                self.log_event("Invested in skills training")
        elif financial_choice == "small_treat":
            cost = random.uniform(30, 100)
            self.money -= cost
            self.happiness += 15
            self.mental_health += 5
        elif financial_choice == "safe_investment":
            invest = min(2000, self.money * 0.15)
            self.money -= invest
            self.investments += invest
            return_rate = random.uniform(0.02, 0.08)
            self.investments += invest * return_rate
        elif financial_choice == "contribute_retirement":
            contrib = min(500, self.money * 0.1)
            self.money -= contrib
            self.has_retirement_savings += contrib * 1.05  # employer match
        elif financial_choice == "risky_investment":
            invest = min(1000, self.money * 0.1)
            self.money -= invest
            self.investments += invest
            return_rate = random.uniform(-0.5, 1.0)
            self.investments += invest * return_rate
            if return_rate > 0.2:
                self.log_event(f"Risky investment gained ${invest * return_rate:.0f}")
            elif return_rate < 0:
                self.log_event(f"Risky investment lost ${-invest * return_rate:.0f}")
        
        # Health insurance
        if not self.has_health_insurance and self.money > 2000 and random.random() < 0.15:
            cost = 300
            self.money -= cost
            self.has_health_insurance = True
            self.log_event("Purchased health insurance")
        
        # Transport if needed
        if self.has_job and not self.sick:
            if not self.car_working:
                transport_options = ["rideshare_safe", "public_transit", "ask_friend", "walk_carefully", "skip_work"]
                transport_weights = [45, 25, 15, 10, 5]
                if self.money < 50:
                    transport_weights[0] -= 20
                transport_choice = random.choices(transport_options, weights=transport_weights, k=1)[0]
                if self.verbose:
                    print(f"Transport: {transport_choice.replace('_', ' ')}")
                
                if transport_choice == "rideshare_safe":
                    cost = random.uniform(35, 65)
                    self.money -= cost
                elif transport_choice == "public_transit":
                    cost = random.uniform(5, 15)
                    self.money -= cost
                elif transport_choice == "walk_carefully":
                    self.energy -= 25
                    self.health -= 0.5
        
        # Illness & recovery
        if self.sick:
            self.sick_days_remaining -= 1
            self.health -= self.sickness_severity * 1.5
            self.mental_health -= 10
            self.energy -= 35
            self.happiness -= 12
            if self.has_health_insurance and random.random() < 0.6:
                self.health += 20
                self.mental_health += 10
                self.sick_days_remaining = max(0, self.sick_days_remaining - 3)
            if self.sick_days_remaining <= 0:
                self.sick = False
                self.log_event("Recovered from illness")
        
        # Random events (balanced)
        event = random.random()
        if event < 0.30:
            if event < 0.05:
                self.sick = True
                self.sick_days_remaining = random.randint(4, 18)
                self.sickness_severity = random.uniform(4, 9)
                self.log_event("Fell ill")
            elif event < 0.10:
                if self.car_working:
                    self.car_working = False
                    self.car_repair_cost = random.uniform(1200, 6000)
                    self.log_event("Car broke down")
            elif event < 0.15:
                self.social_support += random.uniform(5, 15)
                self.happiness += 15
                self.mental_health += 10
                self.log_event("Positive social interaction")
            elif event < 0.20:
                self.skill_level += 0.05
                self.log_event("Learned something useful")
            elif event < 0.25:
                gain = random.uniform(300, 1500)
                self.money += gain
                self.log_event(f"Small windfall +${gain:.0f}")
            elif event < 0.30:
                if self.has_job:
                    self.job_stability += 10
                    self.log_event("Positive feedback at work")
        
        # Despair check
        if self.happiness < 15 or self.mental_health < 20:
            self.low_happiness_streak += 1
        else:
            self.low_happiness_streak = 0
        if self.low_happiness_streak > 8 and random.random() < 0.15:
            self.alive = False
            self.cause_of_end = "Suicide from despair"
            self.log_event("Overwhelmed by despair")
            return
        
        # Sudden death risk
        death_risk = 0.002
        if self.transport_today in ["walk_carefully"]:
            death_risk += 0.012
        if self.money < 200:
            death_risk += 0.01
        if random.random() < death_risk:
            self.alive = False
            causes = ["car accident", "hit by vehicle", "violent crime", "health complication"]
            self.cause_of_end = random.choice(causes)
            self.log_event(f"Sudden death: {self.cause_of_end}")
            return
        
        if self.health <= 0 or self.mental_health <= 0:
            self.alive = False
            self.cause_of_end = "Death from poor health"
            self.log_event(self.cause_of_end)
        
        # Clamp values
        self.health = max(0, min(100, self.health))
        self.mental_health = max(0, min(100, self.mental_health))
        self.energy = max(0, min(100, self.energy))
        self.happiness = max(0, min(100, self.happiness))
        self.job_stability = max(0, min(100, self.job_stability))
        self.skill_level = max(0.5, self.skill_level)
        self.social_support = max(0, min(100, self.social_support))
        
        self.log_day()

def run_simulation(days=365, seed=12345, verbose=False):
    sim = LifeSimulation(seed=seed, verbose=verbose)
    
    print(f"Life Simulation - {days} days (seed {seed})")
    print("Running full year simulation with strategic decisions.\n")
    
    while sim.day < days and sim.alive:
        sim.daily_routine()
    
    df = pd.DataFrame(sim.logs)
    
    fig, axs = plt.subplots(4, 2, figsize=(16, 14))
    fig.suptitle('Life Simulation Results', fontsize=16)
    
    axs[0,0].plot(df['day'], df['weight'], color='blue')
    axs[0,0].set_title('Weight (kg)')
    
    axs[0,1].plot(df['day'], df['money'], color='green', label='Cash')
    axs[0,1].plot(df['day'], df['net_worth'], color='darkgreen', linestyle='--', label='Net Worth')
    axs[0,1].legend()
    axs[0,1].set_title('Financial Progress')
    
    axs[1,0].plot(df['day'], df['health'], color='red', label='Physical')
    axs[1,0].plot(df['day'], df['mental_health'], color='purple', label='Mental')
    axs[1,0].legend()
    axs[1,0].set_title('Health')
    
    axs[1,1].plot(df['day'], df['happiness'], color='orange')
    axs[1,1].set_title('Happiness')
    
    axs[2,0].plot(df['day'], df['skill_level'], color='purple')
    axs[2,0].set_title('Skill Level')
    
    axs[2,1].plot(df['day'], df['social_support'], color='cyan')
    axs[2,1].set_title('Social Support')
    
    axs[3,0].plot(df['day'], df['debt'], color='black')
    axs[3,0].set_title('Debt Level')
    axs[3,0].set_xlabel('Day')
    
    axs[3,1].plot(df['day'], df['investments'], color='brown')
    axs[3,1].set_title('Investments')
    axs[3,1].set_xlabel('Day')
    
    plt.tight_layout()
    plt.show()
    
    final = df.iloc[-1] if not df.empty else None
    print("\n=== SIMULATION SUMMARY ===")
    if final is not None:
        print(f"Ended on Day {int(final['day'])} (Age ~{final['age']})")
    if not sim.alive:
        print(f"Ended due to: {sim.cause_of_end}")
    else:
        print("Completed the full period successfully.")
    
    if final is not None:
        print("\nFinal Stats:")
        print(f"  Age: {final['age']:.1f}")
        print(f"  Weight: {final['weight']} kg (BMI {final['bmi']})")
        print(f"  Health: Physical {final['health']}/100 | Mental {final['mental_health']}/100")
        print(f"  Happiness: {final['happiness']}/100")
        print(f"  Money: ${final['money']:.0f} | Debt: ${final['debt']:.0f}")
        print(f"  Investments: ${final['investments']:.0f} | Retirement: ${final['retirement']:.0f}")
        print(f"  Net Worth: ${final['net_worth']:.0f}")
        print(f"  Skill Level: {final['skill_level']:.1f} | Social Support: {final['social_support']:.0f}")
        print(f"  Job: {'Yes' if final['has_job'] else 'No'} (Income ${sim.monthly_income:.0f}/month if employed)")
        print(f"  Car: {'Working' if final['car_working'] else 'Broken'}")
    
    print("\nKey Events:")
    for event in sim.event_log[:20]:  # Show first 20 for brevity
        print(event)
    if len(sim.event_log) > 20:
        print(f"... and {len(sim.event_log) - 20} more events.")

if __name__ == "__main__":
    run_simulation(days=365, seed=12345, verbose=False)