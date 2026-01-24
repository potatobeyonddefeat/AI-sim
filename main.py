import random
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, optimizers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("TensorFlow not available. RL training features disabled.")

class Person:
    def __init__(self, name, age, gender, relationship_type):
        self.name = name
        self.age = age
        self.gender = gender
        self.relationship_type = relationship_type  # 'parent', 'sibling', 'child', 'spouse', 'friend'
        self.alive = True
        self.health = random.uniform(60, 100)
        self.relationship_quality = random.uniform(40, 90)
        
class LifeSimulation:
    def __init__(self, seed=None, verbose=False):
        if seed is not None:
            random.seed(seed)
        self.verbose = verbose
        
        # Personal identity
        self.gender = random.choice(['male', 'female', 'non-binary'])
        self.name = self.generate_name()
        
        # Core state variables
        self.day = 0
        self.age = 25.0
        self.weight = 75.0 if self.gender == 'male' else 65.0
        self.height = 1.75 if self.gender == 'male' else 1.65
        self.health = 100.0
        self.mental_health = 100.0
        self.energy = 100.0
        self.happiness = 50.0
        self.money = 15000.0
        self.debt = 0.0
        self.monthly_income = 4500 if random.random() > 0.15 else 0
        self.has_job = self.monthly_income > 0
        self.job_stability = 100.0
        self.skill_level = 1.0
        self.social_support = 50.0
        
        # Relationships
        self.relationship_status = random.choice(['single', 'single', 'single', 'dating', 'married'])
        self.spouse = None
        if self.relationship_status == 'married':
            self.spouse = Person(self.generate_name(), random.randint(23, 30), 
                               random.choice(['male', 'female', 'non-binary']), 'spouse')
        self.relationship_satisfaction = random.uniform(40, 80) if self.relationship_status != 'single' else 0
        
        # Family and social
        self.family_members = self.generate_family()
        self.friends = self.generate_friends()
        self.children = []
        
        # Substance use
        self.alcohol_dependency = 0.0  # 0-100 scale
        self.drug_dependency = 0.0  # 0-100 scale
        self.days_sober_alcohol = 0
        self.days_sober_drugs = 0
        self.in_recovery = False
        
        # Criminal history
        self.criminal_record = []
        self.arrest_count = 0
        self.probation = False
        self.probation_days_remaining = 0
        
        # Transportation
        self.car_working = True
        self.car_issue_severity = 0.0
        self.car_repair_cost_shop = 0.0
        self.car_repair_cost_parts = 0.0
        self.traffic_tickets = 0
        self.license_suspended = False
        self.license_suspension_days = 0
        
        # Insurance and financial
        self.has_health_insurance = random.random() > 0.5
        self.insurance_cost_monthly = 350 if self.has_health_insurance else 0
        self.has_car_insurance = random.random() > 0.3
        self.car_insurance_cost_monthly = 150 if self.has_car_insurance else 0
        self.has_retirement_savings = 0.0
        self.investments = 0.0
        self.child_support_payment = 0.0
        
        # Health
        self.sick = False
        self.sick_days_remaining = 0
        self.sickness_severity = 0
        self.chronic_condition = random.random() < 0.1
        self.therapy = False
        self.medication = False
        self.medication_cost_monthly = 0
        
        # Life status
        self.low_happiness_streak = 0
        self.alive = True
        self.cause_of_end = None
        self.in_jail = False
        self.jail_days_remaining = 0
        
        # Tracking
        self.net_worth_history = []
        self.event_log = []
        self.logs = []
        self.total_reward = 0.0
        self.daily_rewards = []
        
    def generate_name(self):
        male_names = ['James', 'John', 'Robert', 'Michael', 'David', 'William', 'Richard']
        female_names = ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Susan', 'Jessica']
        nb_names = ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery']
        
        if self.gender == 'male':
            return random.choice(male_names)
        elif self.gender == 'female':
            return random.choice(female_names)
        else:
            return random.choice(nb_names)
    
    def generate_family(self):
        family = []
        # Parents (70% chance each is alive)
        if random.random() < 0.7:
            family.append(Person("Mother", random.randint(45, 70), 'female', 'parent'))
        if random.random() < 0.65:
            family.append(Person("Father", random.randint(45, 72), 'male', 'parent'))
        
        # Siblings
        num_siblings = random.choices([0, 1, 2, 3], weights=[30, 40, 20, 10])[0]
        for i in range(num_siblings):
            gender = random.choice(['male', 'female', 'non-binary'])
            age = self.age + random.randint(-8, 8)
            family.append(Person(f"Sibling{i+1}", max(1, age), gender, 'sibling'))
        
        return family
    
    def generate_friends(self):
        num_friends = random.randint(2, 8)
        friends = []
        for i in range(num_friends):
            gender = random.choice(['male', 'female', 'non-binary'])
            age = self.age + random.randint(-5, 5)
            friend = Person(f"Friend{i+1}", age, gender, 'friend')
            friend.relationship_quality = random.uniform(30, 80)
            friends.append(friend)
        return friends
        
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
            'gender': self.gender,
            'weight': round(self.weight, 1),
            'bmi': self.bmi(),
            'health': round(self.health),
            'mental_health': round(self.mental_health),
            'energy': round(self.energy),
            'happiness': round(self.happiness),
            'money': round(self.money, 2),
            'debt': round(self.debt, 2),
            'net_worth': round(self.money + self.investments + self.has_retirement_savings - self.debt, 2),
            'alcohol_dependency': round(self.alcohol_dependency, 1),
            'drug_dependency': round(self.drug_dependency, 1),
            'relationship_status': self.relationship_status,
            'num_children': len(self.children),
            'num_family_alive': len([f for f in self.family_members if f.alive]),
            'in_jail': self.in_jail,
            'criminal_record': len(self.criminal_record)
        })
        self.update_net_worth()
    
    def handle_family_death(self, person):
        person.alive = False
        self.log_event(f"{person.relationship_type.title()} ({person.name}) has died")
        
        # Emotional impact
        impact_multiplier = {'parent': 2.5, 'sibling': 2.0, 'child': 4.0, 'spouse': 3.5, 'friend': 1.0}
        multiplier = impact_multiplier.get(person.relationship_type, 1.0)
        
        self.mental_health -= random.uniform(15, 35) * multiplier
        self.happiness -= random.uniform(20, 40) * multiplier
        
        # Funeral costs
        funeral_cost = random.uniform(5000, 15000)
        financial_responsibility = random.random() < 0.5  # 50% chance you're responsible
        
        if person.relationship_type in ['parent', 'child', 'spouse'] or financial_responsibility:
            self.money -= funeral_cost
            self.log_event(f"Paid funeral costs: -${funeral_cost:.0f}")
            if self.money < 0:
                self.debt += abs(self.money)
                self.money = 0
        
        # Possible inheritance
        if person.relationship_type == 'parent' and random.random() < 0.4:
            inheritance = random.uniform(10000, 150000)
            self.money += inheritance
            self.log_event(f"Received inheritance: +${inheritance:.0f}")
    
    def handle_family_suicide(self, person):
        person.alive = False
        self.log_event(f"{person.relationship_type.title()} ({person.name}) committed suicide")
        
        # Severe emotional trauma
        impact_multiplier = {'parent': 3.0, 'sibling': 2.5, 'child': 5.0, 'spouse': 4.0, 'friend': 1.5}
        multiplier = impact_multiplier.get(person.relationship_type, 1.5)
        
        self.mental_health -= random.uniform(25, 50) * multiplier
        self.happiness -= random.uniform(30, 50) * multiplier
        self.social_support -= random.uniform(10, 25)
        
        # Higher chance of therapy/medication
        if random.random() < 0.6:
            self.therapy = True
            self.log_event("Started therapy to cope with loss")
        
        # Funeral costs
        funeral_cost = random.uniform(5000, 12000)
        if person.relationship_type in ['parent', 'child', 'spouse', 'sibling']:
            self.money -= funeral_cost
            self.log_event(f"Paid funeral costs: -${funeral_cost:.0f}")
            if self.money < 0:
                self.debt += abs(self.money)
                self.money = 0
    
    def handle_family_murder(self, person):
        person.alive = False
        self.log_event(f"{person.relationship_type.title()} ({person.name}) was murdered")
        
        # Extreme emotional trauma
        impact_multiplier = {'parent': 3.5, 'sibling': 3.0, 'child': 6.0, 'spouse': 5.0, 'friend': 2.0}
        multiplier = impact_multiplier.get(person.relationship_type, 2.0)
        
        self.mental_health -= random.uniform(30, 60) * multiplier
        self.happiness -= random.uniform(35, 60) * multiplier
        self.health -= random.uniform(5, 15)  # Physical toll from stress
        
        # Almost certainly need therapy
        if random.random() < 0.8:
            self.therapy = True
            self.medication = True
            self.medication_cost_monthly = random.uniform(100, 400)
            self.log_event("Started therapy and medication")
        
        # Funeral and legal costs
        total_cost = random.uniform(8000, 20000)
        self.money -= total_cost
        self.log_event(f"Funeral and legal costs: -${total_cost:.0f}")
        if self.money < 0:
            self.debt += abs(self.money)
            self.money = 0
    
    def check_family_events(self):
        """Check for deaths, suicides, murders in family/friends"""
        for person in self.family_members + self.friends + ([self.spouse] if self.spouse else []):
            if not person.alive:
                continue
            
            # Natural death (age and health based)
            death_chance = 0.0001
            if person.age > 70:
                death_chance += (person.age - 70) * 0.001
            if person.health < 30:
                death_chance += 0.005
            
            if random.random() < death_chance:
                self.handle_family_death(person)
                continue
            
            # Suicide (mental health crisis)
            suicide_chance = 0.0001
            if person.health < 20:
                suicide_chance += 0.002
            
            if random.random() < suicide_chance:
                self.handle_family_suicide(person)
                continue
            
            # Murder (random tragedy)
            murder_chance = 0.00005  # Very rare
            if random.random() < murder_chance:
                self.handle_family_murder(person)
                continue
            
            # Age the person
            person.age += 1/365.0
            person.health -= random.uniform(0, 0.05)
    
    def handle_pregnancy(self):
        """Handle pregnancy and childbirth"""
        if self.gender == 'female' and self.relationship_status in ['married', 'dating']:
            if random.random() < 0.001:  # ~0.3% daily chance if in relationship
                # Pregnancy
                self.log_event("Pregnancy discovered!")
                self.mental_health += random.uniform(-20, 30)  # Can be stressful or joyful
                
                # 9 months later...
                pregnancy_days = 270
                if self.day % 365 > pregnancy_days:  # Simplified
                    baby_gender = random.choice(['male', 'female'])
                    baby = Person(f"Child{len(self.children)+1}", 0, baby_gender, 'child')
                    self.children.append(baby)
                    self.log_event(f"Gave birth to a {baby_gender} child!")
                    
                    # Medical costs
                    if self.has_health_insurance:
                        cost = random.uniform(2000, 5000)
                    else:
                        cost = random.uniform(15000, 30000)
                    self.money -= cost
                    self.log_event(f"Medical costs for childbirth: -${cost:.0f}")
                    
                    self.happiness += random.uniform(20, 50)
                    self.mental_health -= random.uniform(10, 30)  # Postpartum stress
    
    def handle_substance_use(self):
        """Handle alcohol and drug use/addiction"""
        # Alcohol
        if self.alcohol_dependency > 0:
            # Dependency effects
            self.health -= self.alcohol_dependency * 0.05
            self.mental_health -= self.alcohol_dependency * 0.03
            self.money -= self.alcohol_dependency * 0.5  # Daily cost
            
            if self.alcohol_dependency > 30 and random.random() < 0.02:
                self.job_stability -= random.uniform(5, 15)
                self.log_event("Alcohol affecting work performance")
            
            # Recovery tracking
            if not self.in_recovery:
                self.days_sober_alcohol = 0
                if random.random() < 0.005:  # Small chance to seek help
                    self.in_recovery = True
                    self.log_event("Entered alcohol recovery program")
                    self.money -= random.uniform(3000, 10000)
            else:
                self.days_sober_alcohol += 1
                self.alcohol_dependency -= 0.3
                if self.days_sober_alcohol > 90:
                    self.mental_health += 0.5
                    self.health += 0.3
        
        # Drugs
        if self.drug_dependency > 0:
            self.health -= self.drug_dependency * 0.08
            self.mental_health -= self.drug_dependency * 0.06
            self.money -= self.drug_dependency * 1.5  # Expensive
            
            if self.drug_dependency > 40:
                # High risk of overdose
                if random.random() < 0.001:
                    self.health -= random.uniform(40, 80)
                    self.log_event("Drug overdose - hospitalized")
                    hospital_cost = random.uniform(20000, 100000)
                    if not self.has_health_insurance:
                        self.money -= hospital_cost
                        if self.money < 0:
                            self.debt += abs(self.money)
                            self.money = 0
            
            # Criminal risk
            if random.random() < 0.003:
                self.handle_arrest("drug_possession")
        
        # Triggers for substance use
        if self.mental_health < 30 or self.happiness < 20:
            if random.random() < 0.01:
                if random.random() < 0.7:
                    self.alcohol_dependency += random.uniform(5, 15)
                    self.log_event("Started drinking to cope")
                else:
                    self.drug_dependency += random.uniform(10, 25)
                    self.log_event("Started using drugs to cope")
    
    def handle_arrest(self, crime_type):
        """Handle criminal activity and arrests"""
        self.arrest_count += 1
        self.criminal_record.append(crime_type)
        self.log_event(f"Arrested for {crime_type.replace('_', ' ')}")
        
        # Immediate costs
        bail = random.uniform(500, 10000)
        lawyer_fees = random.uniform(2000, 15000)
        total_cost = bail + lawyer_fees
        self.money -= total_cost
        self.log_event(f"Legal costs: -${total_cost:.0f}")
        
        if self.money < 0:
            self.debt += abs(self.money)
            self.money = 0
        
        # Mental health impact
        self.mental_health -= random.uniform(15, 35)
        self.happiness -= random.uniform(20, 40)
        self.social_support -= random.uniform(10, 25)
        
        # Possible jail time
        jail_chance = {'traffic_violation': 0.05, 'DUI': 0.4, 'drug_possession': 0.5, 
                       'theft': 0.6, 'assault': 0.7, 'fraud': 0.5}
        
        if random.random() < jail_chance.get(crime_type, 0.3):
            jail_days = random.randint(30, 730)
            self.in_jail = True
            self.jail_days_remaining = jail_days
            self.log_event(f"Sentenced to {jail_days} days in jail")
            
            # Lose job
            if self.has_job and random.random() < 0.9:
                self.has_job = False
                self.monthly_income = 0
                self.log_event("Lost job due to incarceration")
        else:
            # Probation
            self.probation = True
            self.probation_days_remaining = random.randint(180, 730)
            self.log_event(f"Placed on probation for {self.probation_days_remaining} days")
        
        # Job impact even if not jailed
        if self.has_job and not self.in_jail:
            if random.random() < 0.4:
                self.has_job = False
                self.monthly_income = 0
                self.log_event("Lost job due to criminal record")
            else:
                self.job_stability -= random.uniform(20, 50)
    
    def handle_traffic_violations(self):
        """Handle traffic tickets and DUIs"""
        if self.car_working and not self.license_suspended:
            # Regular traffic violation
            if random.random() < 0.003:
                fine = random.uniform(150, 500)
                self.money -= fine
                self.traffic_tickets += 1
                self.log_event(f"Traffic ticket: -${fine:.0f}")
                
                if self.traffic_tickets > 5:
                    self.license_suspended = True
                    self.license_suspension_days = random.randint(30, 180)
                    self.log_event(f"License suspended for {self.license_suspension_days} days")
            
            # DUI
            if self.alcohol_dependency > 20 and random.random() < 0.002:
                self.handle_arrest("DUI")
                self.license_suspended = True
                self.license_suspension_days = random.randint(90, 365)
                
                # Additional fines
                self.money -= random.uniform(5000, 15000)
                
                # Insurance drops you or skyrockets
                if self.has_car_insurance:
                    self.car_insurance_cost_monthly *= random.uniform(2.5, 4.0)
    
    def calculate_daily_reward(self):
        """Calculate RL reward for the current day"""
        reward = 0.0
        
        # Base reward for staying alive and out of jail
        if self.alive and not self.in_jail:
            reward += 1.0
        elif self.in_jail:
            reward -= 2.0
        else:
            reward -= 100.0
            return reward
        
        # Health rewards
        reward += (self.health - 50) / 50.0 * 0.5
        reward += (self.mental_health - 50) / 50.0 * 0.5
        reward += (self.happiness - 50) / 50.0 * 1.0
        
        # Financial health
        if self.money > 0:
            reward += min(1.0, self.money / 10000.0) * 0.3
        else:
            reward -= 0.5
        
        if self.debt > 0:
            reward -= min(2.0, self.debt / 5000.0) * 0.3
        
        # Relationship rewards
        if self.relationship_status in ['married', 'dating']:
            reward += (self.relationship_satisfaction / 100.0) * 0.3
        
        # Children (responsibility but also joy)
        reward += len(self.children) * 0.1
        
        # Substance penalties
        reward -= (self.alcohol_dependency / 100.0) * 0.8
        reward -= (self.drug_dependency / 100.0) * 1.2
        
        # Criminal penalties
        reward -= len(self.criminal_record) * 0.1
        
        # Social rewards
        num_alive_family = len([f for f in self.family_members if f.alive])
        reward += (num_alive_family / max(1, len(self.family_members))) * 0.2
        
        # Job and stability
        if self.has_job:
            reward += 0.3 * (self.job_stability / 100.0)
        else:
            reward -= 0.5
        
        # Car and license
        if self.car_working and not self.license_suspended:
            reward += 0.2
        elif not self.car_working or self.license_suspended:
            reward -= 0.2
        
        self.daily_rewards.append(reward)
        self.total_reward += reward
        return reward
    
    def daily_routine(self):
        if not self.alive:
            return
        
        # Skip most activities if in jail
        if self.in_jail:
            self.jail_days_remaining -= 1
            self.mental_health -= 0.5
            self.happiness -= 1.0
            self.health -= 0.3
            self.day += 1
            self.age += 1/365.0
            
            if self.jail_days_remaining <= 0:
                self.in_jail = False
                self.log_event("Released from jail")
                self.happiness += 20
            
            self.log_day()
            self.calculate_daily_reward()
            return
        
        self.day += 1
        self.age += 1/365.0
        
        if self.verbose:
            print(f"\n--- Day {self.day} ({self.name}, Age {self.age:.1f}, {self.gender}) ---")
        
        # License suspension
        if self.license_suspended:
            self.license_suspension_days -= 1
            if self.license_suspension_days <= 0:
                self.license_suspended = False
                self.log_event("License reinstated")
        
        # Probation
        if self.probation:
            self.probation_days_remaining -= 1
            if self.probation_days_remaining <= 0:
                self.probation = False
                self.log_event("Probation ended")
            
            # Probation violation risk
            if random.random() < 0.002:
                self.handle_arrest("probation_violation")
        
        # Daily costs
        inflation_factor = 1 + (self.day // 30) * 0.0002
        daily_cost = random.uniform(50, 90) * inflation_factor
        
        # Children costs
        for child in self.children:
            if child.alive and child.age < 18:
                daily_cost += random.uniform(30, 80)
        
        self.money -= daily_cost
        
        # Child support
        if self.child_support_payment > 0:
            if self.day % 30 == 1:
                self.money -= self.child_support_payment
                self.log_event(f"Child support payment: -${self.child_support_payment:.0f}")
        
        # Financial stress effects
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
        
        # Monthly cycle
        if self.day % 30 == 1:
            # Rent
            rent_cost = 1400 * inflation_factor
            self.money -= rent_cost
            
            # Insurance
            self.money -= self.insurance_cost_monthly
            self.money -= self.car_insurance_cost_monthly
            
            # Therapy and medication
            if self.therapy:
                therapy_cost = random.uniform(200, 500)
                self.money -= therapy_cost
                self.mental_health += 5
            
            if self.medication:
                self.money -= self.medication_cost_monthly
                self.mental_health += 3
            
            # Debt payments
            if self.debt > 0:
                interest = self.debt * 0.08 / 12
                self.debt += interest
                min_payment = min(interest * 1.5, self.money * 0.1)
                self.money -= min_payment
                self.debt -= min_payment
                self.mental_health -= 8 if self.debt > 5000 else 3
            
            # Paycheck
            if self.has_job:
                gross_pay = self.monthly_income * (self.job_stability / 100) * (1 + (self.skill_level - 1)*0.3)
                tax = gross_pay * 0.10
                net_pay = gross_pay - tax
                self.money += net_pay
                self.has_retirement_savings += gross_pay * 0.05
        
        # Natural decline/recovery
        self.health -= 0.02
        self.mental_health -= 0.05
        self.happiness -= 0.1
        self.energy = min(100, self.energy + 45)
        
        # Eating
        calories = random.randint(1800, 3000)
        net_calories = calories - 2500
        self.weight += net_calories / 7700.0
        self.weight = max(40.0, min(200.0, self.weight))
        
        # Activity
        if random.random() < 0.4:
            self.weight -= random.uniform(0.2, 0.6)
            self.health += random.uniform(0.8, 1.5)
            self.mental_health += random.uniform(1, 3)
            self.happiness += random.uniform(4, 10)
        
        self.weight = max(40.0, min(200.0, self.weight))
        
        # Substance use
        self.handle_substance_use()
        
        # Traffic violations
        self.handle_traffic_violations()
        
        # Family events
        self.check_family_events()
        
        # Pregnancy chance
        if self.gender == 'female':
            self.handle_pregnancy()
        
        # Random events
        event = random.random()
        if event < 0.50:
            if event < 0.05:
                self.sick = True
                self.sick_days_remaining = random.randint(4, 20)
                self.sickness_severity = random.uniform(4, 10)
                self.log_event("Caught an illness")
            
            elif event < 0.08:
                # Relationship events
                if self.relationship_status == 'single' and random.random() < 0.3:
                    self.relationship_status = 'dating'
                    self.relationship_satisfaction = random.uniform(60, 85)
                    self.log_event("Started dating someone")
                    self.happiness += 20
                
                elif self.relationship_status == 'dating':
                    if random.random() < 0.1:
                        self.relationship_status = 'married'
                        spouse_gender = random.choice(['male', 'female', 'non-binary'])
                        self.spouse = Person(self.generate_name(), random.randint(23, 35), spouse_gender, 'spouse')
                        self.log_event("Got married!")
                        self.happiness += 35
                        # Wedding costs
                        wedding_cost = random.uniform(15000, 50000)
                        self.money -= wedding_cost
                    elif random.random() < 0.05:
                        self.relationship_status = 'single'
                        self.relationship_satisfaction = 0
                        self.log_event("Broke up")
                        self.happiness -= 25
                        self.mental_health -= 20
                
                elif self.relationship_status == 'married':
                    if self.relationship_satisfaction < 30 and random.random() < 0.02:
                        self.relationship_status = 'single'
                        self.log_event("Got divorced")
                        self.happiness -= 40
                        self.mental_health -= 35
                        # Divorce costs
                        divorce_cost = random.uniform(10000, 50000)
                        self.money -= divorce_cost
                        # Possible child support
                        if len(self.children) > 0 and random.random() < 0.6:
                            self.child_support_payment = random.uniform(500, 2000)
                            self.log_event(f"Ordered to pay ${self.child_support_payment:.0f}/month child support")
                        self.spouse = None
            
            elif event < 0.12:
                gain = random.uniform(500, 3000)
                self.money += gain
                self.happiness += 15
                self.log_event(f"Unexpected bonus/refund +${gain:.0f}")
            
            elif event < 0.16:
                cost = random.uniform(500, 3000)
                self.money -= cost
                self.mental_health -= 10
                self.happiness -= 15
                self.log_event(f"Unexpected expense -${cost:.0f}")
            
            elif event < 0.18:
                # Car breakdown
                if self.car_working and random.random() < 0.3:
                    self.car_working = False
                    self.car_issue_severity = random.uniform(1, 10)
                    self.car_repair_cost_parts = 200 + self.car_issue_severity * 300 + random.randint(0, 1000)
                    self.car_repair_cost_shop = self.car_repair_cost_parts * random.uniform(1.8, 3.0)
                    self.log_event(f"Car breakdown! Parts ~${self.car_repair_cost_parts:.0f}, Shop ~${self.car_repair_cost_shop:.0f}")
                    self.happiness -= 15
            
            elif event < 0.22:
                # Mental health crisis
                if self.mental_health < 40:
                    self.mental_health -= random.uniform(10, 25)
                    self.log_event("Mental health crisis")
                    if random.random() < 0.3:
                        self.therapy = True
                        self.medication = True
                        self.medication_cost_monthly = random.uniform(100, 400)
            
            elif event < 0.24:
                # Friend event
                if len(self.friends) > 0 and random.random() < 0.5:
                    friend = random.choice(self.friends)
                    if random.random() < 0.8:
                        # Positive
                        self.happiness += random.uniform(5, 15)
                        self.social_support += random.uniform(3, 10)
                        friend.relationship_quality += random.uniform(5, 15)
                    else:
                        # Conflict
                        self.happiness -= random.uniform(5, 15)
                        self.mental_health -= random.uniform(5, 10)
                        friend.relationship_quality -= random.uniform(10, 25)
                        if friend.relationship_quality < 10:
                            self.friends.remove(friend)
                            self.log_event(f"Lost friendship with {friend.name}")
            
            elif event < 0.26:
                # Crime temptation when desperate
                if self.money < 500 and not self.has_job and random.random() < 0.05:
                    crime_types = ['theft', 'fraud', 'drug_dealing']
                    crime = random.choice(crime_types)
                    
                    if random.random() < 0.7:  # Get away with it
                        stolen = random.uniform(500, 5000)
                        self.money += stolen
                        self.mental_health -= 15
                        self.log_event(f"Committed {crime}, gained ${stolen:.0f}")
                    else:  # Caught
                        self.handle_arrest(crime)
        
        # Sickness
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
        
        # Car repair
        if not self.car_working:
            if self.money >= self.car_repair_cost_parts and random.random() < 0.3:
                cost = self.car_repair_cost_parts
                self.money -= cost
                success = random.random() < (0.4 + self.skill_level * 0.2)
                if success:
                    self.car_working = True
                    self.log_event(f"DIY car repair successful: ${cost:.0f}")
                    self.happiness += 15
                else:
                    self.health -= random.uniform(5, 20)
                    self.log_event("DIY car repair failed")
            elif self.money >= self.car_repair_cost_shop and random.random() < 0.5:
                cost = self.car_repair_cost_shop
                self.money -= cost
                self.car_working = True
                self.log_event(f"Professional car repair: ${cost:.0f}")
                self.happiness += 10
        
        # Relationship satisfaction decay/growth
        if self.relationship_status in ['married', 'dating']:
            if self.mental_health > 60 and self.happiness > 50:
                self.relationship_satisfaction += random.uniform(0, 0.5)
            else:
                self.relationship_satisfaction -= random.uniform(0, 1.0)
            
            self.relationship_satisfaction = max(0, min(100, self.relationship_satisfaction))
        
        # Age children
        for child in self.children:
            if child.alive:
                child.age += 1/365.0
        
        # Job loss
        if self.has_job and self.job_stability < 20 and random.random() < 0.1:
            self.has_job = False
            self.monthly_income = 0
            self.job_stability = 0
            self.happiness -= 30
            self.mental_health -= 25
            self.log_event("Lost job")
        
        # Happiness tracking
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
            self.cause_of_end = "suicide"
            self.log_event("Committed suicide")
        elif self.low_happiness_streak > 365:
            self.alive = False
            self.cause_of_end = "gave_up"
            self.log_event("Gave up on life")
        elif self.weight < 40 or self.weight > 200:
            self.alive = False
            self.cause_of_end = "weight_related"
            self.log_event(f"Died from weight issues ({self.weight:.1f}kg)")
        elif self.alcohol_dependency > 90 or self.drug_dependency > 90:
            if random.random() < 0.01:
                self.alive = False
                self.cause_of_end = "overdose"
                self.log_event("Died from overdose")
        
        # Clamp stats
        self.health = max(0, min(100, self.health))
        self.mental_health = max(0, min(100, self.mental_health))
        self.energy = max(0, min(100, self.energy))
        self.happiness = max(0, min(100, self.happiness))
        self.job_stability = max(0, min(100, self.job_stability))
        self.skill_level = max(0.5, self.skill_level)
        self.social_support = max(0, min(100, self.social_support))
        self.weight = max(40.0, min(200.0, self.weight))
        self.alcohol_dependency = max(0, min(100, self.alcohol_dependency))
        self.drug_dependency = max(0, min(100, self.drug_dependency))
        self.relationship_satisfaction = max(0, min(100, self.relationship_satisfaction))
        
        self.log_day()
        self.calculate_daily_reward()

def run_simulation(days=365, seed=None, verbose=False):
    sim = LifeSimulation(seed=seed, verbose=verbose)
    
    for _ in range(days):
        sim.daily_routine()
        if not sim.alive:
            break
    
    # Summary
    print(f"\n{'='*70}")
    print(f"LIFE SIMULATION SUMMARY - {sim.name} ({sim.gender})")
    print(f"{'='*70}")
    print(f"Survived: {sim.day} days ({sim.day/365:.2f} years)")
    print(f"Final Age: {sim.age:.1f}")
    if not sim.alive:
        print(f"Cause of death: {sim.cause_of_end}")
    
    print(f"\nFinal Stats:")
    print(f"  Health: {sim.health:.1f}")
    print(f"  Mental Health: {sim.mental_health:.1f}")
    print(f"  Happiness: {sim.happiness:.1f}")
    print(f"  Weight: {sim.weight:.1f}kg (BMI: {sim.bmi()})")
    
    print(f"\nFinancial:")
    print(f"  Money: ${sim.money:,.2f}")
    print(f"  Debt: ${sim.debt:,.2f}")
    print(f"  Net Worth: ${sim.money + sim.investments + sim.has_retirement_savings - sim.debt:,.2f}")
    
    print(f"\nRelationships:")
    print(f"  Status: {sim.relationship_status}")
    if sim.relationship_status in ['married', 'dating']:
        print(f"  Satisfaction: {sim.relationship_satisfaction:.1f}")
    print(f"  Children: {len(sim.children)}")
    alive_family = len([f for f in sim.family_members if f.alive])
    print(f"  Family members alive: {alive_family}/{len(sim.family_members)}")
    print(f"  Friends: {len(sim.friends)}")
    
    print(f"\nSubstances:")
    print(f"  Alcohol dependency: {sim.alcohol_dependency:.1f}")
    print(f"  Drug dependency: {sim.drug_dependency:.1f}")
    
    print(f"\nLegal:")
    print(f"  Arrests: {sim.arrest_count}")
    print(f"  Criminal record: {len(sim.criminal_record)} offenses")
    if sim.criminal_record:
        print(f"  Crimes: {', '.join(set(sim.criminal_record))}")
    
    print(f"\nRL Metrics:")
    print(f"  Total Reward: {sim.total_reward:.2f}")
    print(f"  Average Daily Reward: {sim.total_reward/max(1,sim.day):.3f}")
    print(f"{'='*70}\n")
    
    # Create visualizations
    df = pd.DataFrame(sim.logs)
    
    fig, axes = plt.subplots(4, 3, figsize=(18, 16))
    fig.suptitle(f'Life Simulation: {sim.name} ({sim.gender})', fontsize=16, fontweight='bold')
    
    # Health metrics
    axes[0,0].plot(df['day'], df['health'], label='Health', color='red', alpha=0.7)
    axes[0,0].plot(df['day'], df['mental_health'], label='Mental Health', color='purple', alpha=0.7)
    axes[0,0].set_title('Health Metrics')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    # Happiness
    axes[0,1].plot(df['day'], df['happiness'], color='orange', linewidth=2)
    axes[0,1].set_title('Happiness Over Time')
    axes[0,1].grid(True, alpha=0.3)
    
    # Weight & BMI
    axes[0,2].plot(df['day'], df['weight'], label='Weight', color='blue')
    ax2 = axes[0,2].twinx()
    ax2.plot(df['day'], df['bmi'], label='BMI', color='darkblue', linestyle='--')
    axes[0,2].set_title('Weight & BMI')
    axes[0,2].legend(loc='upper left')
    ax2.legend(loc='upper right')
    axes[0,2].grid(True, alpha=0.3)
    
    # Financial
    axes[1,0].plot(df['day'], df['net_worth'], label='Net Worth', color='darkgreen', linewidth=2)
    axes[1,0].plot(df['day'], df['money'], label='Cash', color='green', alpha=0.6)
    axes[1,0].plot(df['day'], -df['debt'], label='-Debt', color='red', alpha=0.6)
    axes[1,0].axhline(y=0, color='black', linestyle='-', alpha=0.3)
    axes[1,0].set_title('Financial Overview')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    # Substance dependency
    axes[1,1].plot(df['day'], df['alcohol_dependency'], label='Alcohol', color='brown', alpha=0.7)
    axes[1,1].plot(df['day'], df['drug_dependency'], label='Drugs', color='red', alpha=0.7)
    axes[1,1].set_title('Substance Dependency')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    # Relationships
    axes[1,2].plot(df['day'], df['num_children'], label='Children', color='pink', linewidth=2)
    axes[1,2].plot(df['day'], df['num_family_alive'], label='Family Alive', color='purple', alpha=0.6)
    axes[1,2].set_title('Family & Children')
    axes[1,2].legend()
    axes[1,2].grid(True, alpha=0.3)
    
    # Criminal record
    axes[2,0].plot(df['day'], df['criminal_record'], color='red', linewidth=2)
    axes[2,0].fill_between(df['day'], 0, df['in_jail'].astype(int)*df['criminal_record'].max() if df['criminal_record'].max() > 0 else 1, 
                          alpha=0.3, label='In Jail', color='orange')
    axes[2,0].set_title('Criminal Record & Jail Time')
    axes[2,0].legend()
    axes[2,0].grid(True, alpha=0.3)
    
    # Daily rewards
    if sim.daily_rewards:
        axes[2,1].plot(range(len(sim.daily_rewards)), sim.daily_rewards, color='darkblue', alpha=0.6)
        axes[2,1].axhline(y=0, color='black', linestyle='-', alpha=0.5)
        axes[2,1].set_title('Daily RL Rewards')
        axes[2,1].grid(True, alpha=0.3)
    
    # Cumulative reward
    if sim.daily_rewards:
        cumulative = [sum(sim.daily_rewards[:i+1]) for i in range(len(sim.daily_rewards))]
        axes[2,2].plot(range(len(cumulative)), cumulative, color='darkgreen', linewidth=2)
        axes[2,2].set_title('Cumulative Reward')
        axes[2,2].grid(True, alpha=0.3)
    
    # Relationship status timeline
    status_map = {'single': 0, 'dating': 1, 'married': 2}
    status_values = [status_map.get(s, 0) for s in df['relationship_status']]
    axes[3,0].plot(df['day'], status_values, color='purple', linewidth=2)
    axes[3,0].set_title('Relationship Status')
    axes[3,0].set_yticks([0, 1, 2])
    axes[3,0].set_yticklabels(['Single', 'Dating', 'Married'])
    axes[3,0].grid(True, alpha=0.3)
    
    # Event timeline
    axes[3,1].text(0.1, 0.9, f"Major Events:", fontsize=12, fontweight='bold', transform=axes[3,1].transAxes)
    event_text = "\n".join(sim.event_log[-15:])  # Last 15 events
    axes[3,1].text(0.1, 0.7, event_text, fontsize=8, transform=axes[3,1].transAxes, verticalalignment='top', family='monospace')
    axes[3,1].axis('off')
    
    # Summary stats
    summary = f"""
Final Summary:
Age: {sim.age:.1f} years
Status: {'Alive' if sim.alive else 'Deceased'}
Health: {sim.health:.0f}
Mental: {sim.mental_health:.0f}
Happiness: {sim.happiness:.0f}
Net Worth: ${sim.money + sim.investments - sim.debt:,.0f}
Children: {len(sim.children)}
Arrests: {sim.arrest_count}
Total Reward: {sim.total_reward:.1f}
    """
    axes[3,2].text(0.1, 0.9, summary, fontsize=10, transform=axes[3,2].transAxes, 
                  verticalalignment='top', family='monospace')
    axes[3,2].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    return sim, df

if __name__ == "__main__":
    sim, df = run_simulation(days=1825, seed=None, verbose=False)  # 5 years

# ========================================
# REINFORCEMENT LEARNING TRAINING SECTION
# ========================================

class LifeEnvironment:
    """Gym-like environment wrapper for the life simulation"""
    
    def __init__(self, seed=None):
        self.sim = None
        self.seed = seed
        
    def reset(self):
        """Reset environment and return initial state"""
        self.sim = LifeSimulation(seed=self.seed, verbose=False)
        return self.get_state()
    
    def get_state(self):
        """Get current state as numpy array for neural network"""
        if not self.sim.alive or self.sim.in_jail:
            # Return zeros for terminal state
            return np.zeros(30)
        
        state = np.array([
            self.sim.age / 100.0,  # Normalize to 0-1
            self.sim.health / 100.0,
            self.sim.mental_health / 100.0,
            self.sim.happiness / 100.0,
            self.sim.energy / 100.0,
            min(self.sim.money / 50000.0, 1.0),  # Cap normalization
            min(self.sim.debt / 50000.0, 1.0),
            self.sim.weight / 200.0,
            self.sim.bmi() / 50.0,
            self.sim.job_stability / 100.0,
            self.sim.skill_level / 5.0,
            self.sim.social_support / 100.0,
            1.0 if self.sim.has_job else 0.0,
            1.0 if self.sim.car_working else 0.0,
            1.0 if self.sim.sick else 0.0,
            self.sim.alcohol_dependency / 100.0,
            self.sim.drug_dependency / 100.0,
            1.0 if self.sim.relationship_status == 'married' else 0.5 if self.sim.relationship_status == 'dating' else 0.0,
            self.sim.relationship_satisfaction / 100.0,
            len(self.sim.children) / 5.0,  # Normalize assuming max 5 kids
            len([f for f in self.sim.family_members if f.alive]) / max(1, len(self.sim.family_members)),
            len(self.sim.friends) / 10.0,
            len(self.sim.criminal_record) / 10.0,
            1.0 if self.sim.therapy else 0.0,
            1.0 if self.sim.has_health_insurance else 0.0,
            1.0 if self.sim.probation else 0.0,
            1.0 if self.sim.license_suspended else 0.0,
            self.sim.traffic_tickets / 10.0,
            min(self.sim.investments / 50000.0, 1.0),
            self.sim.day / 3650.0  # Normalize days (10 years max)
        ], dtype=np.float32)
        
        return state
    
    def step(self, action):
        """
        Execute one day with the given action
        
        Actions (simplified decision-making):
        0: Focus on health (exercise, healthy eating)
        1: Focus on work (skill building, career)
        2: Focus on relationships (social activities)
        3: Focus on finances (saving, investing)
        4: Risky behavior (substance use, crime if desperate)
        5: Self-care (therapy, rest, entertainment)
        """
        if not self.sim.alive:
            return self.get_state(), 0, True, {}
        
        # Modify simulation behavior based on action
        # This is a simplified approach - in reality you'd want more granular control
        old_money = self.sim.money
        old_health = self.sim.health
        old_mental_health = self.sim.mental_health
        
        # Execute action influence before daily routine
        if action == 0:  # Health focus
            self.sim.health += random.uniform(1, 3)
            self.sim.weight -= random.uniform(0.3, 0.8)
            self.sim.energy -= 20
            self.sim.happiness += 5
            
        elif action == 1:  # Career focus
            if self.sim.has_job:
                self.sim.job_stability += random.uniform(1, 3)
                self.sim.skill_level += random.uniform(0.01, 0.05)
            else:
                # Job searching
                if random.random() < 0.05:  # 5% daily chance
                    self.sim.has_job = True
                    self.sim.monthly_income = random.uniform(3000, 5000) * self.sim.skill_level
                    self.sim.job_stability = 70
            self.sim.energy -= 15
            
        elif action == 2:  # Relationship focus
            self.sim.social_support += random.uniform(1, 3)
            self.sim.happiness += random.uniform(3, 8)
            if self.sim.relationship_status in ['married', 'dating']:
                self.sim.relationship_satisfaction += random.uniform(1, 4)
            self.sim.money -= random.uniform(20, 100)  # Social activities cost money
            
        elif action == 3:  # Financial focus
            if self.sim.money > 1000:
                save_amount = self.sim.money * random.uniform(0.05, 0.15)
                self.sim.money -= save_amount
                self.sim.investments += save_amount
                self.sim.mental_health += 2
            if self.sim.debt > 0:
                pay_amount = min(self.sim.money * 0.2, self.sim.debt)
                self.sim.money -= pay_amount
                self.sim.debt -= pay_amount
                self.sim.mental_health += 3
                
        elif action == 4:  # Risky behavior
            # Substance use risk
            if random.random() < 0.3:
                self.sim.alcohol_dependency += random.uniform(2, 8)
                self.sim.happiness += random.uniform(5, 15)  # Short-term
                self.sim.mental_health -= random.uniform(2, 6)  # Long-term cost
                self.sim.money -= random.uniform(30, 100)
            
            # Crime if desperate
            if self.sim.money < 500 and random.random() < 0.1:
                if random.random() < 0.6:  # Success
                    self.sim.money += random.uniform(500, 2000)
                else:  # Caught
                    self.sim.criminal_record.append('theft')
                    self.sim.arrest_count += 1
                    self.sim.mental_health -= 20
                    
        elif action == 5:  # Self-care
            self.sim.mental_health += random.uniform(2, 6)
            self.sim.happiness += random.uniform(3, 10)
            self.sim.energy += random.uniform(10, 20)
            self.sim.money -= random.uniform(50, 200)
            
            if self.sim.mental_health < 40 and not self.sim.therapy:
                if random.random() < 0.3:
                    self.sim.therapy = True
        
        # Run normal daily routine
        self.sim.daily_routine()
        
        # Get reward
        reward = self.sim.daily_rewards[-1] if self.sim.daily_rewards else 0
        
        # Check if done
        done = not self.sim.alive
        
        # Additional info
        info = {
            'day': self.sim.day,
            'age': self.sim.age,
            'cause_of_end': self.sim.cause_of_end if done else None,
            'total_reward': self.sim.total_reward
        }
        
        return self.get_state(), reward, done, info


class DQNAgent:
    """Deep Q-Network agent for learning optimal life decisions"""
    
    def __init__(self, state_size=30, action_size=6, learning_rate=0.001):
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow is required for DQN training")
        
        self.state_size = state_size
        self.action_size = action_size
        self.memory = []
        self.memory_size = 10000
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = learning_rate
        self.batch_size = 64
        
        # Build neural networks
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()
        
    def _build_model(self):
        """Build neural network for Q-learning"""
        model = models.Sequential([
            layers.Dense(128, activation='relu', input_shape=(self.state_size,)),
            layers.Dropout(0.2),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.Dense(self.action_size, activation='linear')
        ])
        
        model.compile(
            optimizer=optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse'
        )
        return model
    
    def update_target_model(self):
        """Update target network with current model weights"""
        self.target_model.set_weights(self.model.get_weights())
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory"""
        self.memory.append((state, action, reward, next_state, done))
        if len(self.memory) > self.memory_size:
            self.memory.pop(0)
    
    def act(self, state):
        """Choose action using epsilon-greedy policy"""
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        
        state = np.reshape(state, [1, self.state_size])
        q_values = self.model.predict(state, verbose=0)
        return np.argmax(q_values[0])
    
    def replay(self):
        """Train on batch of experiences from memory"""
        if len(self.memory) < self.batch_size:
            return 0
        
        # Sample batch
        batch = random.sample(self.memory, self.batch_size)
        
        states = np.array([exp[0] for exp in batch])
        actions = np.array([exp[1] for exp in batch])
        rewards = np.array([exp[2] for exp in batch])
        next_states = np.array([exp[3] for exp in batch])
        dones = np.array([exp[4] for exp in batch])
        
        # Predict Q-values
        current_q = self.model.predict(states, verbose=0)
        next_q = self.target_model.predict(next_states, verbose=0)
        
        # Update Q-values
        for i in range(self.batch_size):
            if dones[i]:
                current_q[i][actions[i]] = rewards[i]
            else:
                current_q[i][actions[i]] = rewards[i] + self.gamma * np.max(next_q[i])
        
        # Train
        history = self.model.fit(states, current_q, epochs=1, verbose=0)
        loss = history.history['loss'][0]
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss
    
    def save(self, filepath):
        """Save model weights"""
        self.model.save_weights(filepath)
    
    def load(self, filepath):
        """Load model weights"""
        self.model.load_weights(filepath)
        self.update_target_model()


def train_agent(episodes=100, max_days=1825, save_path='life_agent.h5'):
    """
    Train DQN agent to play the life simulation
    
    Args:
        episodes: Number of lifetimes to simulate
        max_days: Maximum days per episode (5 years default)
        save_path: Path to save trained model
    """
    if not TF_AVAILABLE:
        print("TensorFlow not available. Cannot train agent.")
        return None
    
    env = LifeEnvironment()
    agent = DQNAgent()
    
    rewards_history = []
    days_survived_history = []
    losses = []
    
    print(f"\n{'='*70}")
    print(f"STARTING DQN TRAINING - {episodes} EPISODES")
    print(f"{'='*70}\n")
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        day = 0
        
        for day in range(max_days):
            # Choose action
            action = agent.act(state)
            
            # Take step
            next_state, reward, done, info = env.step(action)
            
            # Store experience
            agent.remember(state, action, reward, next_state, done)
            
            # Train
            loss = agent.replay()
            if loss > 0:
                losses.append(loss)
            
            state = next_state
            total_reward += reward
            
            if done:
                break
        
        # Update target network periodically
        if episode % 10 == 0:
            agent.update_target_model()
        
        rewards_history.append(total_reward)
        days_survived_history.append(day)
        
        # Print progress
        if episode % 10 == 0:
            avg_reward = np.mean(rewards_history[-10:])
            avg_days = np.mean(days_survived_history[-10:])
            avg_loss = np.mean(losses[-100:]) if losses else 0
            print(f"Episode {episode}/{episodes} | "
                  f"Days: {day} | "
                  f"Reward: {total_reward:.1f} | "
                  f"Avg Reward: {avg_reward:.1f} | "
                  f"Avg Days: {avg_days:.0f} | "
                  f"Loss: {avg_loss:.4f} | "
                  f"Epsilon: {agent.epsilon:.3f}")
    
    # Save trained model
    agent.save(save_path)
    print(f"\nModel saved to {save_path}")
    
    # Plot training results
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('DQN Training Results', fontsize=16, fontweight='bold')
    
    axes[0,0].plot(rewards_history)
    axes[0,0].set_title('Total Reward per Episode')
    axes[0,0].set_xlabel('Episode')
    axes[0,0].set_ylabel('Total Reward')
    axes[0,0].grid(True, alpha=0.3)
    
    axes[0,1].plot(days_survived_history)
    axes[0,1].set_title('Days Survived per Episode')
    axes[0,1].set_xlabel('Episode')
    axes[0,1].set_ylabel('Days')
    axes[0,1].grid(True, alpha=0.3)
    
    if losses:
        axes[1,0].plot(losses)
        axes[1,0].set_title('Training Loss')
        axes[1,0].set_xlabel('Training Step')
        axes[1,0].set_ylabel('Loss')
        axes[1,0].grid(True, alpha=0.3)
    
    # Moving average of rewards
    window = 10
    if len(rewards_history) >= window:
        moving_avg = [np.mean(rewards_history[i:i+window]) for i in range(len(rewards_history)-window+1)]
        axes[1,1].plot(moving_avg)
        axes[1,1].set_title(f'Moving Average Reward (window={window})')
        axes[1,1].set_xlabel('Episode')
        axes[1,1].set_ylabel('Average Reward')
        axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return agent


def evaluate_agent(agent, episodes=10, render=True):
    """
    Evaluate trained agent
    
    Args:
        agent: Trained DQNAgent
        episodes: Number of test episodes
        render: Whether to show detailed output
    """
    env = LifeEnvironment()
    
    total_rewards = []
    days_survived = []
    
    print(f"\n{'='*70}")
    print(f"EVALUATING AGENT - {episodes} EPISODES")
    print(f"{'='*70}\n")
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        day = 0
        
        # Use greedy policy (no exploration)
        old_epsilon = agent.epsilon
        agent.epsilon = 0
        
        for day in range(1825):  # Max 5 years
            action = agent.act(state)
            next_state, reward, done, info = env.step(action)
            
            state = next_state
            total_reward += reward
            
            if done:
                break
        
        agent.epsilon = old_epsilon
        
        total_rewards.append(total_reward)
        days_survived.append(day)
        
        if render:
            print(f"Episode {episode+1}: Days={day}, Reward={total_reward:.1f}, "
                  f"Cause={'Alive' if env.sim.alive else env.sim.cause_of_end}")
    
    print(f"\n{'='*70}")
    print(f"EVALUATION RESULTS")
    print(f"{'='*70}")
    print(f"Average Reward: {np.mean(total_rewards):.1f} (±{np.std(total_rewards):.1f})")
    print(f"Average Days Survived: {np.mean(days_survived):.0f} (±{np.std(days_survived):.0f})")
    print(f"Best Reward: {np.max(total_rewards):.1f}")
    print(f"Worst Reward: {np.min(total_rewards):.1f}")
    print(f"{'='*70}\n")


# Example usage for training
def train_example():
    """Example: Train an agent for 100 episodes"""
    if not TF_AVAILABLE:
        print("TensorFlow not available. Install with: pip install tensorflow")
        return
    
    agent = train_agent(episodes=100, max_days=1825, save_path='life_agent.h5')
    
    if agent:
        print("\nEvaluating trained agent...")
        evaluate_agent(agent, episodes=5, render=True)


# Uncomment to train:
# train_example()