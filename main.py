import random
import matplotlib.pyplot as plt
import pandas as pd

class LifeSimulation:
    def __init__(self, seed=None, verbose=False):
        if seed is not None:
            random.seed(seed)
        self.verbose = verbose
        
        # Core state variables
        self.day = 0
        self.age = 25.0
        self.weight = 75.0  # kg - realistic starting point
        self.height = 1.75  # meters
        self.health = 100.0
        self.mental_health = 100.0
        self.energy = 100.0
        self.happiness = 50.0
        self.money = 15000.0
        self.debt = 0.0
        self.monthly_income = 4500 if random.random() > 0.15 else 0
        self.has_job = self.monthly_income > 0
        self.job_stability = 100.0
        self.skill_level = 1.0  # Multiplier for income, job success, DIY repairs
        self.social_support = 50.0
        self.car_working = True
        self.car_issue_severity = 0.0  # 0-10 scale for repair complexity
        self.car_repair_cost_shop = 0.0  # Full shop cost
        self.car_repair_cost_parts = 0.0  # Parts cost for DIY
        self.has_health_insurance = False
        self.has_emergency_fund = self.money >= 5000
        self.has_retirement_savings = 0.0
        self.investments = 0.0
        self.sick = False
        self.sick_days_remaining = 0
        self.sickness_severity = 0
        self.low_happiness_streak = 0
        self.alive = True
        self.cause_of_end = None
        self.transport_today = "home"
        self.net_worth_history = []
        self.event_log = []
        
        self.logs = []
        
        # RL reward tracking
        self.total_reward = 0.0
        self.daily_rewards = []
        
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
    
    def calculate_daily_reward(self):
        """
        Calculate RL reward for the current day.
        Positive rewards for good outcomes, negative for bad.
        """
        reward = 0.0
        
        # Base reward for staying alive
        if self.alive:
            reward += 1.0
        else:
            # Death penalty
            reward -= 100.0
            return reward
        
        # Health-based rewards (scaled to -1 to +1)
        health_reward = (self.health - 50) / 50.0  # -1 to +1
        reward += health_reward * 0.5
        
        # Mental health reward
        mental_reward = (self.mental_health - 50) / 50.0
        reward += mental_reward * 0.5
        
        # Happiness reward (primary driver)
        happiness_reward = (self.happiness - 50) / 50.0
        reward += happiness_reward * 1.0
        
        # Financial health reward
        if self.money > 0:
            money_reward = min(1.0, self.money / 10000.0)  # Capped at $10k
            reward += money_reward * 0.3
        else:
            reward -= 0.5  # Penalty for being broke
        
        if self.debt > 0:
            debt_penalty = min(2.0, self.debt / 5000.0)
            reward -= debt_penalty * 0.3
        
        # Sickness penalty
        if self.sick:
            reward -= 0.5 * (self.sickness_severity / 10.0)
        
        # Car working bonus
        if self.car_working:
            reward += 0.2
        else:
            reward -= 0.3  # Penalty for broken car
        
        # Job stability bonus
        if self.has_job:
            reward += 0.3 * (self.job_stability / 100.0)
        else:
            reward -= 0.5
        
        # BMI health penalty (too high or too low)
        bmi = self.bmi()
        if bmi < 18.5 or bmi > 30:
            reward -= 0.3
        elif 18.5 <= bmi <= 25:
            reward += 0.2
        
        # Social support bonus
        reward += (self.social_support / 100.0) * 0.2
        
        self.daily_rewards.append(reward)
        self.total_reward += reward
        
        return reward
        
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
        
        # Daily living costs with gradual inflation
        inflation_factor = 1 + (self.day // 30) * 0.0002
        daily_cost = random.uniform(50, 90) * inflation_factor if self.money >= 1000 else random.uniform(30, 60) * inflation_factor
        self.money -= daily_cost
        
        # Effects of financial stress
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
        
        # Monthly financial cycle
        if self.day % 30 == 1:
            rent_cost = 1400 * inflation_factor
            self.money -= rent_cost
            self.log_event(f"Paid rent/bills (-${rent_cost:.0f})")
            
            if self.debt > 0:
                interest = self.debt * 0.08 / 12
                self.debt += interest
                min_payment = min(interest * 1.5, self.money * 0.1)
                self.money -= min_payment
                self.debt -= min_payment
                self.mental_health -= 8 if self.debt > 5000 else 3
                self.log_event(f"Debt payment: -${min_payment:.0f} (interest: ${interest:.0f})")
            
            if self.has_job:
                gross_pay = self.monthly_income * (self.job_stability / 100) * (1 + (self.skill_level - 1)*0.3)
                tax = gross_pay * 0.10
                net_pay = gross_pay - tax
                self.money += net_pay
                self.has_retirement_savings += gross_pay * 0.05
                self.log_event(f"Paycheck received: +${net_pay:.0f} (after taxes)")
        
        # Natural daily decline/recovery
        self.health -= 0.02
        self.mental_health -= 0.05
        self.happiness -= 0.1
        self.energy = min(100, self.energy + 45)
        
        # Decision 1: Eating strategy
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
        weight_change = net_calories / 7700.0
        self.weight += weight_change
        # FIX: Prevent negative weight with realistic minimum
        self.weight = max(40.0, min(200.0, self.weight))
        
        # Decision 2: Physical activity
        activity_options = ["intense_gym", "moderate_exercise", "light_walk", "rest_day"]
        activity_weights = [15, 40, 30, 15]
        activity_choice = self.make_decision("activity", activity_options, activity_weights)
        if self.verbose:
            print(f"Activity: {activity_choice.replace('_', ' ')}")
        
        if activity_choice == "intense_gym":
            weight_loss = random.uniform(0.4, 0.9)
            self.weight -= weight_loss
            self.health += 1.8
            self.mental_health += 3
            self.energy -= 45
            self.happiness += 10
            self.money -= 10 if random.random() < 0.3 else 0
        elif activity_choice == "moderate_exercise":
            weight_loss = random.uniform(0.2, 0.5)
            self.weight -= weight_loss
            self.health += 1.2
            self.mental_health += 2
            self.energy -= 30
            self.happiness += 6
        elif activity_choice == "light_walk":
            weight_loss = random.uniform(0.1, 0.3)
            self.weight -= weight_loss
            self.health += 0.6
            self.mental_health += 1
            self.energy -= 15
            self.happiness += 4
        # FIX: Ensure weight stays within bounds after exercise
        self.weight = max(40.0, min(200.0, self.weight))
        
        # Car breakdown and repair logic
        if self.car_working and random.random() < 0.005:  # ~1.8% chance per year
            self.car_working = False
            self.car_issue_severity = random.uniform(1, 10)
            # Parts cost scales with severity
            self.car_repair_cost_parts = 200 + self.car_issue_severity * 300 + random.randint(0, 1000)
            # Shop adds labor markup (1.8x to 3x parts cost)
            self.car_repair_cost_shop = self.car_repair_cost_parts * random.uniform(1.8, 3.0)
            self.log_event(f"Car breakdown! Severity {self.car_issue_severity:.1f} - Parts ~${self.car_repair_cost_parts:.0f}, Shop ~${self.car_repair_cost_shop:.0f}")
            self.happiness -= 15
            self.mental_health -= 10
        
        # Handle car repair if car is broken
        if not self.car_working:
            repair_options = ["diy_attempt", "professional_shop", "delay_repair"]
            repair_weights = [30, 50, 20]
            
            # Adjust weights based on skill level
            if self.skill_level > 1.8:
                repair_weights[0] += 30  # More likely to DIY if skilled
            
            # Can't afford options
            if self.money < self.car_repair_cost_parts:
                repair_weights[0] = 0  # Can't DIY
            if self.money < self.car_repair_cost_shop:
                repair_weights[1] = 0  # Can't afford shop
            
            # Normalize weights
            total_weight = sum(repair_weights)
            if total_weight == 0:
                repair_choice = "delay_repair"
            else:
                repair_choice = random.choices(repair_options, weights=repair_weights, k=1)[0]
            
            if self.verbose:
                print(f"Car repair choice: {repair_choice.replace('_', ' ')}")
            
            if repair_choice == "diy_attempt":
                # DIY costs parts + potential extra if mistakes made
                cost = self.car_repair_cost_parts * random.uniform(0.9, 1.2)
                if self.money >= cost:
                    self.money -= cost
                    # Success chance based on skill level and issue severity
                    base_success = 0.4
                    skill_bonus = (self.skill_level - 1) * 0.2
                    severity_penalty = (self.car_issue_severity / 10) * 0.15
                    success_chance = min(0.9, base_success + skill_bonus - severity_penalty)
                    
                    if random.random() < success_chance:
                        self.car_working = True
                        self.car_issue_severity = 0
                        self.log_event(f"DIY repair successful! Cost ${cost:.0f}")
                        self.happiness += 15
                        self.skill_level += 0.05  # Learn from success
                    else:
                        # Failed DIY - potential injury or making it worse
                        injury = random.uniform(5, 25)
                        self.health -= injury
                        self.mental_health -= 15
                        self.happiness -= 10
                        # Might need to go to shop anyway
                        if random.random() < 0.5:
                            self.car_repair_cost_shop *= 1.3  # Made it worse
                        self.log_event(f"DIY repair failed - injury/stress (health -{injury:.0f})")
                else:
                    self.log_event("Couldn't afford DIY parts")
                    
            elif repair_choice == "professional_shop":
                cost = self.car_repair_cost_shop
                if self.money >= cost:
                    self.money -= cost
                    self.car_working = True
                    self.car_issue_severity = 0
                    self.log_event(f"Professional repair completed. Cost ${cost:.0f}")
                    self.happiness += 10
                    self.mental_health += 5  # Relief
                else:
                    self.log_event("Couldn't afford professional repair")
            
            # delay_repair: car remains broken
            if repair_choice == "delay_repair":
                self.mental_health -= 2
                self.happiness -= 3
                # Job impact if car needed for work
                if self.has_job and random.random() < 0.3:
                    self.job_stability -= 5
                    self.log_event("Missed work due to car issues - job stability decreased")
        
        # Sickness progression
        if self.sick:
            self.health -= self.sickness_severity * 0.8
            self.energy -= 30
            self.happiness -= 5
            self.sick_days_remaining -= 1
            
            if self.has_job and random.random() < 0.6:
                self.job_stability -= 2
            
            if self.sick_days_remaining <= 0:
                self.sick = False
                self.log_event("Recovered from illness")
                self.happiness += 10
        
        # Decision 3: Financial management
        if self.day % 7 == 0 and self.money > 500:
            financial_options = ["build_emergency_fund", "pay_down_debt", "invest_in_skills", 
                               "contribute_retirement", "invest_market", "small_treat", "do_nothing"]
            financial_weights = [25, 20, 20, 15, 10, 5, 5]
            financial_choice = self.make_decision("financial", financial_options, financial_weights)
            
            if financial_choice == "build_emergency_fund":
                amount = min(self.money * 0.2, 500)
                self.money -= amount
                # Emergency fund reduces stress
                self.mental_health += 2
                if self.verbose:
                    print(f"Saved ${amount:.0f} for emergencies")
                    
            elif financial_choice == "pay_down_debt" and self.debt > 0:
                amount = min(self.money * 0.3, self.debt)
                self.money -= amount
                self.debt -= amount
                self.mental_health += 5
                self.happiness += 5
                self.log_event(f"Paid ${amount:.0f} toward debt")
                
            elif financial_choice == "invest_in_skills":
                cost = random.uniform(200, 800)
                if self.money >= cost:
                    self.money -= cost
                    self.skill_level += random.uniform(0.05, 0.15)
                    self.log_event(f"Invested ${cost:.0f} in learning/skills")
                    
            elif financial_choice == "contribute_retirement":
                amount = min(self.money * 0.15, 1000)
                self.money -= amount
                self.has_retirement_savings += amount
                self.mental_health += 1
                
            elif financial_choice == "invest_market":
                amount = min(self.money * 0.25, 2000)
                self.money -= amount
                self.investments += amount
                
            elif financial_choice == "small_treat":
                cost = random.uniform(50, 200)
                self.money -= cost
                self.happiness += random.uniform(10, 25)
                self.log_event(f"Enjoyed a treat (-${cost:.0f}, +happiness)")
        
        # Expanded random events for more R&G (Risk & Growth)
        event = random.random()
        if event < 0.45:  # 45% chance of some event
            if event < 0.06:
                # Major illness
                self.sick = True
                self.sick_days_remaining = random.randint(4, 20)
                self.sickness_severity = random.uniform(4, 10)
                self.log_event("Caught an illness")
                
            elif event < 0.12:
                # Windfall
                gain = random.uniform(500, 3000)
                self.money += gain
                self.happiness += 15
                self.log_event(f"Unexpected bonus/refund +${gain:.0f}")
                
            elif event < 0.18:
                # Investment volatility
                if self.investments > 1000:
                    volatility = random.uniform(-0.3, 0.4)
                    change = self.investments * volatility
                    self.investments += change
                    self.log_event(f"Market swing: {'gain' if change > 0 else 'loss'} ${abs(change):.0f}")
                    if change < 0:
                        self.happiness -= 10
                        self.mental_health -= 5
                    else:
                        self.happiness += 15
                        
            elif event < 0.24:
                # Good deal / savings
                savings = random.uniform(100, 400)
                self.money += savings
                self.happiness += 5
                self.log_event(f"Found a great deal - saved ${savings:.0f}")
                
            elif event < 0.30:
                # Emergency expense
                cost = random.uniform(500, 3000)
                self.money -= cost
                self.mental_health -= 10
                self.happiness -= 15
                self.log_event(f"Unexpected expense (appliance, medical, etc.) -${cost:.0f}")
                
            elif event < 0.35:
                # Inspiring moment
                self.mental_health += random.uniform(5, 20)
                self.happiness += 10
                self.social_support += 5
                self.log_event("Inspiring moment - mood boost")
                
            elif event < 0.39:
                # Job opportunity or threat
                if self.has_job:
                    if random.random() < 0.5:
                        # Promotion opportunity
                        self.monthly_income *= random.uniform(1.1, 1.3)
                        self.happiness += 25
                        self.log_event(f"Promotion! New income: ${self.monthly_income:.0f}/month")
                    else:
                        # Job instability
                        self.job_stability -= random.uniform(10, 30)
                        self.mental_health -= 15
                        self.log_event("Job security threatened")
                else:
                    # Job offer
                    if random.random() < 0.3:
                        self.has_job = True
                        self.monthly_income = random.uniform(3000, 5000)
                        self.job_stability = 70
                        self.happiness += 35
                        self.log_event(f"Got a job! Income: ${self.monthly_income:.0f}/month")
                        
            elif event < 0.43:
                # Social event
                if random.random() < 0.7:
                    self.social_support += random.uniform(5, 15)
                    self.happiness += random.uniform(5, 15)
                    self.mental_health += 8
                    self.money -= random.uniform(20, 80)
                    self.log_event("Positive social interaction")
                else:
                    self.social_support -= random.uniform(5, 15)
                    self.happiness -= 10
                    self.mental_health -= 10
                    self.log_event("Social conflict")
                    
            elif event < 0.45:
                # Rare jackpot
                if random.random() < 0.001:
                    jackpot = random.randint(50000, 500000)
                    self.money += jackpot
                    self.happiness = min(100, self.happiness + 50)
                    self.mental_health = min(100, self.mental_health + 30)
                    self.log_event(f"Lottery/inheritance win! +${jackpot:,}")
        
        # Job loss check
        if self.has_job and self.job_stability < 20 and random.random() < 0.1:
            self.has_job = False
            self.monthly_income = 0
            self.job_stability = 0
            self.happiness -= 30
            self.mental_health -= 25
            self.log_event("Lost job")
        
        # Track happiness streaks
        if self.happiness < 20:
            self.low_happiness_streak += 1
        else:
            self.low_happiness_streak = 0
        
        # Death conditions
        if self.health <= 0:
            self.alive = False
            self.cause_of_end = "health_failure"
            self.log_event("Died from health failure")
        elif self.mental_health <= 0:
            self.alive = False
            self.cause_of_end = "mental_health_crisis"
            self.log_event("Succumbed to mental health crisis")
        elif self.low_happiness_streak > 365:
            self.alive = False
            self.cause_of_end = "prolonged_unhappiness"
            self.log_event("Gave up after prolonged unhappiness")
        elif self.weight < 40 or self.weight > 200:
            self.alive = False
            self.cause_of_end = "weight_related"
            self.log_event(f"Died from weight-related issues (weight: {self.weight:.1f}kg)")
        
        # Clamp all stats
        self.health = max(0, min(100, self.health))
        self.mental_health = max(0, min(100, self.mental_health))
        self.energy = max(0, min(100, self.energy))
        self.happiness = max(0, min(100, self.happiness))
        self.job_stability = max(0, min(100, self.job_stability))
        self.skill_level = max(0.5, self.skill_level)
        self.social_support = max(0, min(100, self.social_support))
        self.weight = max(40.0, min(200.0, self.weight))
        
        self.log_day()
        
        # Calculate and log reward
        reward = self.calculate_daily_reward()
        if self.verbose:
            print(f"Daily Reward: {reward:.2f} | Total Reward: {self.total_reward:.2f}")

def run_simulation(days=365, seed=None, verbose=False):
    sim = LifeSimulation(seed=seed, verbose=verbose)
    
    for _ in range(days):
        sim.daily_routine()
        if not sim.alive:
            break
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"SIMULATION SUMMARY")
    print(f"{'='*60}")
    print(f"Survived: {sim.day} days ({sim.day/365:.2f} years)")
    print(f"Final Age: {sim.age:.1f}")
    if not sim.alive:
        print(f"Cause of end: {sim.cause_of_end}")
    print(f"\nFinal Stats:")
    print(f"  Health: {sim.health:.1f}")
    print(f"  Mental Health: {sim.mental_health:.1f}")
    print(f"  Happiness: {sim.happiness:.1f}")
    print(f"  Weight: {sim.weight:.1f}kg (BMI: {sim.bmi()})")
    print(f"  Money: ${sim.money:,.2f}")
    print(f"  Debt: ${sim.debt:,.2f}")
    print(f"  Net Worth: ${sim.money + sim.investments + sim.has_retirement_savings - sim.debt:,.2f}")
    print(f"  Skill Level: {sim.skill_level:.2f}")
    print(f"  Car Working: {sim.car_working}")
    print(f"\nRL Metrics:")
    print(f"  Total Reward: {sim.total_reward:.2f}")
    print(f"  Average Daily Reward: {sim.total_reward/sim.day:.3f}")
    print(f"  Final Daily Reward: {sim.daily_rewards[-1]:.3f}" if sim.daily_rewards else "N/A")
    print(f"{'='*60}\n")
    
    # Create visualizations
    df = pd.DataFrame(sim.logs)
    
    fig, axes = plt.subplots(3, 3, figsize=(16, 12))
    fig.suptitle('Life Simulation Results', fontsize=16, fontweight='bold')
    
    # Plot 1: Health metrics
    axes[0,0].plot(df['day'], df['health'], label='Health', color='red', alpha=0.7)
    axes[0,0].plot(df['day'], df['mental_health'], label='Mental Health', color='purple', alpha=0.7)
    axes[0,0].set_title('Health Metrics')
    axes[0,0].set_xlabel('Day')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    # Plot 2: Happiness & Energy
    axes[0,1].plot(df['day'], df['happiness'], label='Happiness', color='orange', alpha=0.7)
    axes[0,1].plot(df['day'], df['energy'], label='Energy', color='green', alpha=0.7)
    axes[0,1].set_title('Happiness & Energy')
    axes[0,1].set_xlabel('Day')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    # Plot 3: Weight & BMI
    axes[0,2].plot(df['day'], df['weight'], label='Weight (kg)', color='blue', alpha=0.7)
    ax2 = axes[0,2].twinx()
    ax2.plot(df['day'], df['bmi'], label='BMI', color='darkblue', alpha=0.5, linestyle='--')
    axes[0,2].axhline(y=40, color='red', linestyle=':', alpha=0.5, label='Min Weight')
    axes[0,2].set_title('Weight & BMI')
    axes[0,2].set_xlabel('Day')
    axes[0,2].legend(loc='upper left')
    ax2.legend(loc='upper right')
    axes[0,2].grid(True, alpha=0.3)
    
    # Plot 4: Financial Overview
    axes[1,0].plot(df['day'], df['net_worth'], label='Net Worth', color='darkgreen', linewidth=2)
    axes[1,0].plot(df['day'], df['money'], label='Cash', color='green', alpha=0.6)
    axes[1,0].plot(df['day'], -df['debt'], label='-Debt', color='red', alpha=0.6)
    axes[1,0].axhline(y=0, color='black', linestyle='-', alpha=0.3)
    axes[1,0].set_title('Financial Overview')
    axes[1,0].set_xlabel('Day')
    axes[1,0].set_ylabel('Dollars')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    # Plot 5: Investments & Retirement
    axes[1,1].plot(df['day'], df['investments'], label='Investments', color='teal', alpha=0.7)
    axes[1,1].plot(df['day'], df['retirement'], label='Retirement', color='navy', alpha=0.7)
    axes[1,1].set_title('Long-term Savings')
    axes[1,1].set_xlabel('Day')
    axes[1,1].set_ylabel('Dollars')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    # Plot 6: Skill & Social
    axes[1,2].plot(df['day'], df['skill_level'], label='Skill Level', color='purple', alpha=0.7)
    ax3 = axes[1,2].twinx()
    ax3.plot(df['day'], df['social_support'], label='Social Support', color='pink', alpha=0.7)
    axes[1,2].set_title('Skills & Social')
    axes[1,2].set_xlabel('Day')
    axes[1,2].set_ylabel('Skill Level')
    ax3.set_ylabel('Social Support')
    axes[1,2].legend(loc='upper left')
    ax3.legend(loc='upper right')
    axes[1,2].grid(True, alpha=0.3)
    
    # Plot 7: Binary States (Job, Car, Sick)
    axes[2,0].fill_between(df['day'], 0, df['has_job'].astype(int), alpha=0.3, label='Has Job', color='blue')
    axes[2,0].fill_between(df['day'], 0, df['car_working'].astype(int), alpha=0.3, label='Car Working', color='green')
    axes[2,0].fill_between(df['day'], 0, df['sick'].astype(int), alpha=0.3, label='Sick', color='red')
    axes[2,0].set_title('Binary States')
    axes[2,0].set_xlabel('Day')
    axes[2,0].set_ylim(0, 1.2)
    axes[2,0].legend()
    axes[2,0].grid(True, alpha=0.3)
    
    # Plot 8: Daily Rewards
    if sim.daily_rewards:
        axes[2,1].plot(range(len(sim.daily_rewards)), sim.daily_rewards, color='darkblue', alpha=0.6)
        axes[2,1].axhline(y=0, color='black', linestyle='-', alpha=0.5)
        axes[2,1].set_title('Daily RL Rewards')
        axes[2,1].set_xlabel('Day')
        axes[2,1].set_ylabel('Reward')
        axes[2,1].grid(True, alpha=0.3)
    
    # Plot 9: Cumulative Reward
    if sim.daily_rewards:
        cumulative = [sum(sim.daily_rewards[:i+1]) for i in range(len(sim.daily_rewards))]
        axes[2,2].plot(range(len(cumulative)), cumulative, color='darkgreen', linewidth=2)
        axes[2,2].set_title('Cumulative Reward')
        axes[2,2].set_xlabel('Day')
        axes[2,2].set_ylabel('Total Reward')
        axes[2,2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return sim, df

if __name__ == "__main__":
    sim, df = run_simulation(days=365, seed=12345, verbose=False)