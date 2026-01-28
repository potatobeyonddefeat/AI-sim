import random
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import defaultdict
from enum import Enum

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, optimizers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("TensorFlow not available. RL training features disabled.")

# ==================== ENUMS AND CONSTANTS ====================

class PersonalityType(Enum):
    AGGRESSIVE = "aggressive"
    CAUTIOUS = "cautious"
    SOCIAL = "social"
    AMBITIOUS = "ambitious"
    HEDONISTIC = "hedonistic"
    BALANCED = "balanced"

class EducationLevel(Enum):
    HIGH_SCHOOL = "high_school"
    ASSOCIATES = "associates"
    BACHELORS = "bachelors"
    MASTERS = "masters"
    PHD = "phd"

class CareerField(Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    BUSINESS = "business"
    TRADES = "trades"
    ARTS = "arts"
    SERVICE = "service"
    GOVERNMENT = "government"

# ==================== ENHANCED PERSON CLASS ====================

class Person:
    def __init__(self, name, age, gender, relationship_type, ai_controlled=False):
        self.name = name
        self.age = age
        self.gender = gender
        self.relationship_type = relationship_type
        self.alive = True
        self.health = random.uniform(60, 100)
        self.mental_health = random.uniform(50, 90)
        self.relationship_quality = random.uniform(40, 90)
        self.ai_controlled = ai_controlled
        
        # AI personality
        if ai_controlled:
            self.personality = random.choice(list(PersonalityType))
            self.ambition = random.uniform(0, 100)
            self.risk_tolerance = random.uniform(0, 100)
            self.sociability = random.uniform(0, 100)
            self.empathy = random.uniform(0, 100)
            
            # AI state
            self.money = random.uniform(5000, 30000)
            self.job_title = None
            self.education = random.choice(list(EducationLevel))
            self.hobbies = []
            self.goals = []
            self.memories = []  # Store interactions
            
    def age_one_day(self):
        """Age the person by one day and apply health decay"""
        self.age += 1/365.0
        
        # Age-based health decline
        if self.age > 50:
            self.health -= random.uniform(0.01, 0.05) * ((self.age - 50) / 50)
        if self.age > 70:
            self.health -= random.uniform(0.05, 0.15)
        
        # Random health fluctuations
        self.health -= random.uniform(0, 0.03)
        self.mental_health -= random.uniform(0, 0.02)
        
        # Clamp values
        self.health = max(0, min(100, self.health))
        self.mental_health = max(0, min(100, self.mental_health))
    
    def calculate_death_probability(self):
        """Calculate probability of death based on age and health"""
        base_prob = 0.00001
        
        # Age factor
        if self.age < 1:
            base_prob += 0.001  # Infant mortality
        elif self.age < 18:
            base_prob += 0.00005
        elif self.age < 50:
            base_prob += 0.0001
        elif self.age < 70:
            base_prob += 0.0005 + (self.age - 50) * 0.0002
        else:
            base_prob += 0.002 + (self.age - 70) * 0.0015
        
        # Health factor
        if self.health < 20:
            base_prob += 0.01
        elif self.health < 40:
            base_prob += 0.005
        elif self.health < 60:
            base_prob += 0.001
        
        # Mental health factor (suicide risk)
        if self.mental_health < 10:
            base_prob += 0.005
        elif self.mental_health < 30:
            base_prob += 0.001
        
        return min(base_prob, 0.1)  # Cap at 10%
    
    def should_die(self):
        """Check if person dies this day"""
        return random.random() < self.calculate_death_probability()
    
    def get_cause_of_death(self):
        """Determine cause of death based on age and health"""
        if self.age < 1:
            return random.choice(["infant_mortality", "birth_complications"])
        elif self.age < 18:
            return random.choice(["accident", "illness", "congenital_condition"])
        elif self.age < 50:
            causes = ["accident", "illness", "heart_disease", "cancer"]
            if self.mental_health < 30:
                causes.extend(["suicide", "suicide"])
            return random.choice(causes)
        elif self.age < 70:
            return random.choice(["heart_disease", "cancer", "stroke", "illness", "accident"])
        else:
            return random.choice(["old_age", "heart_disease", "cancer", "stroke", "organ_failure"])
    
    def make_ai_decision(self, context):
        """AI makes a decision based on personality"""
        if not self.ai_controlled:
            return None
        
        decision_weights = {
            'work_hard': self.ambition * 0.01,
            'socialize': self.sociability * 0.01,
            'take_risk': self.risk_tolerance * 0.01,
            'help_others': self.empathy * 0.01,
            'rest': (100 - self.ambition) * 0.01
        }
        
        # Personality modifiers
        if self.personality == PersonalityType.AGGRESSIVE:
            decision_weights['take_risk'] *= 2
            decision_weights['work_hard'] *= 1.5
        elif self.personality == PersonalityType.CAUTIOUS:
            decision_weights['take_risk'] *= 0.3
            decision_weights['rest'] *= 1.3
        elif self.personality == PersonalityType.SOCIAL:
            decision_weights['socialize'] *= 2
        elif self.personality == PersonalityType.AMBITIOUS:
            decision_weights['work_hard'] *= 2
        elif self.personality == PersonalityType.HEDONISTIC:
            decision_weights['rest'] *= 2
            decision_weights['socialize'] *= 1.5
        
        # Choose action
        actions = list(decision_weights.keys())
        weights = list(decision_weights.values())
        return random.choices(actions, weights=weights)[0]

# ==================== HOBBY AND SKILL SYSTEM ====================

class Hobby:
    def __init__(self, name, category, cost_per_session, skill_gain, happiness_gain):
        self.name = name
        self.category = category
        self.cost = cost_per_session
        self.skill_gain = skill_gain
        self.happiness_gain = happiness_gain
        self.skill_level = 0

HOBBIES = {
    'gaming': Hobby('Gaming', 'entertainment', 20, 0.5, 10),
    'reading': Hobby('Reading', 'intellectual', 15, 1.0, 8),
    'cooking': Hobby('Cooking', 'practical', 30, 1.2, 12),
    'sports': Hobby('Sports', 'physical', 25, 0.8, 15),
    'music': Hobby('Music', 'creative', 40, 1.5, 18),
    'art': Hobby('Art', 'creative', 35, 1.3, 16),
    'photography': Hobby('Photography', 'creative', 50, 1.0, 14),
    'gardening': Hobby('Gardening', 'practical', 20, 0.7, 12),
    'coding': Hobby('Coding', 'intellectual', 10, 2.0, 10),
    'writing': Hobby('Writing', 'creative', 5, 1.5, 13),
    'yoga': Hobby('Yoga', 'physical', 20, 0.8, 15),
    'chess': Hobby('Chess', 'intellectual', 10, 1.8, 11),
}

# ==================== ENHANCED LIFE SIMULATION ====================

class EnhancedLifeSimulation:
    def __init__(self, seed=None, verbose=False):
        if seed is not None:
            random.seed(seed)
        self.verbose = verbose
        
        # Personal identity
        self.gender = random.choice(['male', 'female', 'non-binary'])
        self.name = self.generate_name()
        self.personality = random.choice(list(PersonalityType))
        
        # Core state variables
        self.day = 0
        self.age = 25.0
        self.weight = 75.0 if self.gender == 'male' else 65.0
        self.height = 1.75 if self.gender == 'male' else 1.65
        self.health = 100.0
        self.mental_health = 100.0
        self.energy = 100.0
        self.happiness = 50.0
        self.stress = 20.0
        self.money = 15000.0
        self.debt = 0.0
        self.student_loan_debt = 0.0
        
        # Career and education
        self.education_level = random.choice([EducationLevel.HIGH_SCHOOL, EducationLevel.BACHELORS])
        if self.education_level == EducationLevel.BACHELORS:
            self.student_loan_debt = random.uniform(20000, 80000)
        
        self.career_field = random.choice(list(CareerField))
        self.job_title = self.get_initial_job_title()
        self.monthly_income = self.calculate_income()
        self.has_job = self.monthly_income > 0
        self.job_stability = 100.0 if self.has_job else 0
        self.job_satisfaction = random.uniform(40, 80) if self.has_job else 0
        self.years_experience = random.uniform(0, 3)
        self.skill_level = 1.0 + self.years_experience * 0.1
        self.career_achievements = []
        
        # Social
        self.social_support = 50.0
        self.reputation = 50.0
        self.charisma = random.uniform(30, 80)
        
        # Relationships
        self.relationship_status = random.choice(['single', 'single', 'single', 'dating', 'married'])
        self.spouse = None
        if self.relationship_status == 'married':
            self.spouse = Person(self.generate_name(), random.randint(23, 30), 
                               random.choice(['male', 'female', 'non-binary']), 'spouse', ai_controlled=True)
        self.relationship_satisfaction = random.uniform(40, 80) if self.relationship_status != 'single' else 0
        self.dating_pool = []
        
        # Family and social
        self.family_members = self.generate_family()
        self.friends = self.generate_friends()
        self.children = []
        self.acquaintances = []
        
        # Hobbies and interests
        self.hobbies = {}
        num_hobbies = random.randint(1, 3)
        for hobby_name in random.sample(list(HOBBIES.keys()), num_hobbies):
            self.hobbies[hobby_name] = HOBBIES[hobby_name]
        
        # Life goals
        self.life_goals = self.generate_life_goals()
        self.completed_goals = []
        
        # Substance use
        self.alcohol_dependency = 0.0
        self.drug_dependency = 0.0
        self.smoking = random.random() < 0.15
        self.smoking_intensity = random.uniform(5, 20) if self.smoking else 0
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
        self.car_value = random.uniform(5000, 25000)
        self.car_age = random.randint(2, 10)
        self.car_issue_severity = 0.0
        self.car_repair_cost_shop = 0.0
        self.car_repair_cost_parts = 0.0
        self.traffic_tickets = 0
        self.license_suspended = False
        self.license_suspension_days = 0
        
        # Insurance and financial
        self.has_health_insurance = random.random() > 0.3
        self.insurance_cost_monthly = 350 if self.has_health_insurance else 0
        self.has_car_insurance = random.random() > 0.2
        self.car_insurance_cost_monthly = 150 if self.has_car_insurance else 0
        self.has_retirement_savings = random.uniform(0, 5000)
        self.investments = random.uniform(0, 10000)
        self.investment_knowledge = random.uniform(0, 50)
        self.credit_score = random.randint(550, 750)
        self.child_support_payment = 0.0
        
        # Health
        self.sick = False
        self.sick_days_remaining = 0
        self.sickness_severity = 0
        self.chronic_conditions = []
        if random.random() < 0.1:
            self.chronic_conditions.append(random.choice(['diabetes', 'asthma', 'hypertension', 'arthritis']))
        self.therapy = False
        self.medication = False
        self.medication_cost_monthly = 0
        self.gym_membership = random.random() < 0.3
        self.gym_cost_monthly = 50 if self.gym_membership else 0
        
        # Housing
        self.owns_home = random.random() < 0.1
        self.home_value = random.uniform(150000, 400000) if self.owns_home else 0
        self.mortgage_payment = self.home_value * 0.004 if self.owns_home else 0
        self.rent = random.uniform(1000, 2000) if not self.owns_home else 0
        
        # Life events tracking
        self.life_milestones = []
        self.major_purchases = []
        
        # Life status
        self.low_happiness_streak = 0
        self.alive = True
        self.cause_of_end = None
        self.in_jail = False
        self.jail_days_remaining = 0
        
        # AI NPCs
        self.ai_npcs = []
        self.npc_interactions = []
        
        # Tracking
        self.net_worth_history = []
        self.event_log = []
        self.logs = []
        self.total_reward = 0.0
        self.daily_rewards = []
        
        # Initialize AI NPCs in the world
        self.initialize_ai_npcs()
        
    def generate_name(self):
        male_names = ['James', 'John', 'Robert', 'Michael', 'David', 'William', 'Richard', 
                     'Thomas', 'Charles', 'Daniel', 'Matthew', 'Christopher', 'Andrew']
        female_names = ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Susan', 'Jessica',
                       'Sarah', 'Karen', 'Nancy', 'Betty', 'Margaret', 'Emily']
        nb_names = ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery',
                   'Quinn', 'Blake', 'Cameron']
        
        if self.gender == 'male':
            return random.choice(male_names)
        elif self.gender == 'female':
            return random.choice(female_names)
        else:
            return random.choice(nb_names)
    
    def get_initial_job_title(self):
        """Get job title based on education and career field"""
        titles = {
            CareerField.TECHNOLOGY: {
                EducationLevel.HIGH_SCHOOL: ['Tech Support', 'Junior Developer', 'IT Assistant'],
                EducationLevel.BACHELORS: ['Software Developer', 'Systems Analyst', 'Data Analyst'],
                EducationLevel.MASTERS: ['Senior Developer', 'Solutions Architect', 'Data Scientist'],
            },
            CareerField.HEALTHCARE: {
                EducationLevel.HIGH_SCHOOL: ['Medical Assistant', 'Pharmacy Technician'],
                EducationLevel.BACHELORS: ['Nurse', 'Physical Therapist', 'Lab Technician'],
                EducationLevel.MASTERS: ['Nurse Practitioner', 'Physician Assistant'],
            },
            CareerField.BUSINESS: {
                EducationLevel.HIGH_SCHOOL: ['Sales Associate', 'Customer Service Rep'],
                EducationLevel.BACHELORS: ['Business Analyst', 'Marketing Manager', 'Accountant'],
                EducationLevel.MASTERS: ['Senior Manager', 'Director', 'Consultant'],
            },
            # Add more...
        }
        
        field_titles = titles.get(self.career_field, {
            EducationLevel.HIGH_SCHOOL: ['Entry Level Worker'],
            EducationLevel.BACHELORS: ['Professional'],
            EducationLevel.MASTERS: ['Senior Professional'],
        })
        
        return random.choice(field_titles.get(self.education_level, ['Worker']))
    
    def calculate_income(self):
        """Calculate monthly income based on education, experience, and field"""
        base_income = {
            EducationLevel.HIGH_SCHOOL: 2500,
            EducationLevel.ASSOCIATES: 3200,
            EducationLevel.BACHELORS: 4500,
            EducationLevel.MASTERS: 6500,
            EducationLevel.PHD: 8000,
        }
        
        field_multiplier = {
            CareerField.TECHNOLOGY: 1.4,
            CareerField.HEALTHCARE: 1.3,
            CareerField.BUSINESS: 1.2,
            CareerField.EDUCATION: 0.9,
            CareerField.TRADES: 1.1,
            CareerField.ARTS: 0.8,
            CareerField.SERVICE: 0.7,
            CareerField.GOVERNMENT: 1.0,
        }
        
        income = base_income.get(self.education_level, 2000)
        income *= field_multiplier.get(self.career_field, 1.0)
        income *= (1 + self.years_experience * 0.05)
        income *= random.uniform(0.85, 1.15)  # Random variation
        
        return income if random.random() > 0.1 else 0  # 10% unemployment
    
    def generate_life_goals(self):
        """Generate life goals based on personality and situation"""
        possible_goals = [
            ('buy_house', 'Buy a house', 300000),
            ('get_married', 'Get married', 0),
            ('have_children', 'Have children', 0),
            ('career_promotion', 'Get promoted', 0),
            ('masters_degree', 'Get masters degree', 50000),
            ('save_100k', 'Save $100,000', 100000),
            ('travel_world', 'Travel to 10 countries', 30000),
            ('start_business', 'Start a business', 50000),
            ('write_book', 'Write a book', 5000),
            ('run_marathon', 'Run a marathon', 500),
        ]
        
        num_goals = random.randint(3, 6)
        return random.sample(possible_goals, num_goals)
    
    def generate_family(self):
        family = []
        
        # Parents (age-based survival probability)
        parent_age_mother = self.age + random.randint(20, 35)
        parent_age_father = self.age + random.randint(22, 38)
        
        if random.random() < self.calculate_survival_prob(parent_age_mother):
            mother = Person("Mother", parent_age_mother, 'female', 'parent', ai_controlled=True)
            family.append(mother)
        
        if random.random() < self.calculate_survival_prob(parent_age_father):
            father = Person("Father", parent_age_father, 'male', 'parent', ai_controlled=True)
            family.append(father)
        
        # Grandparents
        if random.random() < 0.3:
            gm_age = self.age + random.randint(45, 70)
            if random.random() < self.calculate_survival_prob(gm_age):
                family.append(Person("Grandmother", gm_age, 'female', 'grandparent', ai_controlled=True))
        
        if random.random() < 0.25:
            gf_age = self.age + random.randint(45, 72)
            if random.random() < self.calculate_survival_prob(gf_age):
                family.append(Person("Grandfather", gf_age, 'male', 'grandparent', ai_controlled=True))
        
        # Siblings
        num_siblings = random.choices([0, 1, 2, 3, 4], weights=[20, 35, 25, 15, 5])[0]
        for i in range(num_siblings):
            gender = random.choice(['male', 'female', 'non-binary'])
            age = self.age + random.randint(-10, 10)
            age = max(1, age)
            sibling = Person(f"Sibling{i+1}", age, gender, 'sibling', ai_controlled=True)
            family.append(sibling)
        
        return family
    
    def calculate_survival_prob(self, age):
        """Calculate probability someone of given age is still alive"""
        if age < 50:
            return 0.98
        elif age < 60:
            return 0.95
        elif age < 70:
            return 0.85
        elif age < 80:
            return 0.65
        elif age < 90:
            return 0.30
        else:
            return 0.10
    
    def generate_friends(self):
        num_friends = random.randint(2, 10)
        friends = []
        for i in range(num_friends):
            gender = random.choice(['male', 'female', 'non-binary'])
            age = self.age + random.randint(-7, 7)
            friend = Person(f"Friend{i+1}", age, gender, 'friend', ai_controlled=True)
            friend.relationship_quality = random.uniform(40, 85)
            friends.append(friend)
        return friends
    
    def initialize_ai_npcs(self):
        """Create AI-controlled NPCs that exist in the world"""
        num_npcs = random.randint(10, 25)
        for i in range(num_npcs):
            gender = random.choice(['male', 'female', 'non-binary'])
            age = random.randint(18, 70)
            npc = Person(f"NPC_{i}", age, gender, 'stranger', ai_controlled=True)
            self.ai_npcs.append(npc)
    
    def simulate_npc_interactions(self):
        """Simulate interactions between NPCs and with player"""
        # NPCs age and potentially die
        npcs_to_remove = []
        for npc in self.ai_npcs:
            npc.age_one_day()
            if npc.should_die():
                npcs_to_remove.append(npc)
                if self.verbose:
                    print(f"  NPC {npc.name} has died at age {npc.age:.1f}")
        
        for npc in npcs_to_remove:
            self.ai_npcs.remove(npc)
        
        # Random chance of NPC interaction
        if random.random() < 0.05 and len(self.ai_npcs) > 0:
            npc = random.choice(self.ai_npcs)
            self.handle_npc_interaction(npc)
        
        # NPCs interact with each other
        if random.random() < 0.1 and len(self.ai_npcs) >= 2:
            npc1, npc2 = random.sample(self.ai_npcs, 2)
            self.handle_npc_to_npc_interaction(npc1, npc2)
    
    def handle_npc_interaction(self, npc):
        """Handle player interaction with an NPC"""
        interaction_types = ['casual_chat', 'help_request', 'conflict', 'business', 'romantic']
        weights = [0.5, 0.2, 0.1, 0.15, 0.05]
        
        interaction = random.choices(interaction_types, weights=weights)[0]
        
        if interaction == 'casual_chat':
            self.happiness += random.uniform(2, 8)
            self.social_support += random.uniform(1, 5)
            self.log_event(f"Had a pleasant chat with {npc.name}")
            
        elif interaction == 'help_request':
            if random.random() < 0.7:  # Help them
                cost = random.uniform(50, 500)
                self.money -= cost
                self.reputation += random.uniform(5, 15)
                self.happiness += random.uniform(5, 12)
                self.log_event(f"Helped {npc.name} (cost ${cost:.0f})")
                
                # Might become friend
                if random.random() < 0.3:
                    npc.relationship_type = 'friend'
                    self.friends.append(npc)
                    self.ai_npcs.remove(npc)
                    self.log_event(f"{npc.name} became your friend!")
            else:
                self.reputation -= random.uniform(2, 8)
                
        elif interaction == 'conflict':
            self.mental_health -= random.uniform(5, 15)
            self.happiness -= random.uniform(8, 20)
            self.stress += random.uniform(5, 15)
            self.log_event(f"Had a conflict with {npc.name}")
            
            # Small chance of escalation
            if random.random() < 0.05:
                self.handle_arrest("assault")
                
        elif interaction == 'business':
            # Business opportunity
            if random.random() < 0.6:
                profit = random.uniform(100, 2000)
                self.money += profit
                self.log_event(f"Business deal with {npc.name}: +${profit:.0f}")
            else:
                loss = random.uniform(100, 1000)
                self.money -= loss
                self.log_event(f"Bad business deal with {npc.name}: -${loss:.0f}")
                
        elif interaction == 'romantic':
            if self.relationship_status == 'single' and random.random() < 0.4:
                self.relationship_status = 'dating'
                self.relationship_satisfaction = random.uniform(60, 85)
                npc.relationship_type = 'romantic_partner'
                self.dating_pool.append(npc)
                self.ai_npcs.remove(npc)
                self.happiness += 25
                self.log_event(f"Started dating {npc.name}!")
        
        npc.memories.append(f"Interacted with {self.name}")
    
    def handle_npc_to_npc_interaction(self, npc1, npc2):
        """Simulate interaction between two NPCs"""
        # NPCs can become friends, enemies, or romantic partners
        if random.random() < 0.3:
            # Positive interaction
            npc1.relationship_quality += random.uniform(5, 15)
            npc2.relationship_quality += random.uniform(5, 15)
            
            if self.verbose and random.random() < 0.1:
                print(f"  {npc1.name} and {npc2.name} are getting along well")
        else:
            # Negative interaction
            npc1.mental_health -= random.uniform(2, 8)
            npc2.mental_health -= random.uniform(2, 8)
    
    def bmi(self):
        return round(self.weight / (self.height ** 2), 1)
    
    def update_net_worth(self):
        total_assets = self.money + self.investments + self.has_retirement_savings
        if self.owns_home:
            total_assets += self.home_value
        if self.car_working:
            total_assets += self.car_value
        
        total_liabilities = self.debt + self.student_loan_debt
        if self.owns_home:
            total_liabilities += self.home_value * 0.8  # Approximate mortgage
        
        net_worth = total_assets - total_liabilities
        self.net_worth_history.append(net_worth)
    
    def log_event(self, msg):
        self.event_log.append(f"Day {self.day}: {msg}")
        if self.verbose:
            print(f"  {msg}")
    
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
            'stress': round(self.stress),
            'money': round(self.money, 2),
            'debt': round(self.debt, 2),
            'net_worth': round(self.money + self.investments + self.has_retirement_savings - self.debt - self.student_loan_debt, 2),
            'alcohol_dependency': round(self.alcohol_dependency, 1),
            'drug_dependency': round(self.drug_dependency, 1),
            'relationship_status': self.relationship_status,
            'num_children': len(self.children),
            'num_family_alive': len([f for f in self.family_members if f.alive]),
            'num_friends': len(self.friends),
            'in_jail': self.in_jail,
            'criminal_record': len(self.criminal_record),
            'job_satisfaction': round(self.job_satisfaction),
            'reputation': round(self.reputation),
            'num_ai_npcs': len(self.ai_npcs),
        })
        self.update_net_worth()
    
    def handle_family_death(self, person):
        person.alive = False
        cause = person.get_cause_of_death()
        self.log_event(f"{person.relationship_type.title()} ({person.name}) died of {cause} at age {person.age:.0f}")
        
        # Emotional impact based on relationship
        impact_multiplier = {
            'parent': 2.5, 'grandparent': 1.8, 'sibling': 2.2, 
            'child': 4.5, 'spouse': 3.8, 'friend': 1.2, 'romantic_partner': 2.0
        }
        multiplier = impact_multiplier.get(person.relationship_type, 1.0)
        
        # Relationship quality affects grief
        quality_factor = person.relationship_quality / 100.0
        
        self.mental_health -= random.uniform(15, 40) * multiplier * quality_factor
        self.happiness -= random.uniform(20, 45) * multiplier * quality_factor
        self.stress += random.uniform(10, 30) * multiplier
        
        # Funeral costs
        funeral_cost = random.uniform(5000, 18000)
        financial_responsibility = random.random() < 0.5
        
        if person.relationship_type in ['parent', 'child', 'spouse', 'sibling'] or financial_responsibility:
            self.money -= funeral_cost
            self.log_event(f"Funeral costs: -${funeral_cost:.0f}")
            if self.money < 0:
                self.debt += abs(self.money)
                self.money = 0
        
        # Inheritance
        if person.relationship_type in ['parent', 'grandparent']:
            if random.random() < 0.45:
                inheritance = random.uniform(5000, 200000)
                if person.relationship_type == 'grandparent':
                    inheritance *= 0.6
                self.money += inheritance
                self.log_event(f"Inheritance: +${inheritance:.0f}")
        
        # Therapy recommendation
        if multiplier > 2.0 and random.random() < 0.5:
            self.therapy = True
            self.log_event("Started grief therapy")
    
    def check_family_events(self):
        """Check for deaths and life events in family/friends"""
        all_people = self.family_members + self.friends + ([self.spouse] if self.spouse else [])
        
        for person in all_people:
            if not person.alive:
                continue
            
            # Age the person
            person.age_one_day()
            
            # Check for death
            if person.should_die():
                self.handle_family_death(person)
                continue
            
            # AI-controlled people make decisions
            if person.ai_controlled and random.random() < 0.1:
                decision = person.make_ai_decision({'day': self.day})
                
                # Their decisions can affect you
                if decision == 'help_others' and random.random() < 0.2:
                    if person.money > 100:
                        gift = random.uniform(50, min(500, person.money * 0.1))
                        person.money -= gift
                        self.money += gift
                        self.log_event(f"{person.name} gave you ${gift:.0f}")
                        person.relationship_quality += 5
                elif decision == 'socialize' and random.random() < 0.15:
                    self.happiness += random.uniform(3, 10)
                    self.social_support += random.uniform(2, 6)
                    person.relationship_quality += random.uniform(2, 8)
    
    def handle_education_progression(self):
        """Handle going back to school, getting degrees"""
        if not hasattr(self, 'in_school'):
            self.in_school = False
            self.school_progress = 0
        
        if self.in_school:
            self.school_progress += 1
            self.money -= random.uniform(500, 2000)  # Tuition/month
            self.stress += random.uniform(5, 15)
            self.energy -= random.uniform(10, 25)
            
            degree_duration = {
                EducationLevel.ASSOCIATES: 24,
                EducationLevel.BACHELORS: 48,
                EducationLevel.MASTERS: 24,
                EducationLevel.PHD: 60
            }
            
            if self.school_progress >= degree_duration.get(self.target_degree, 48):
                self.education_level = self.target_degree
                self.in_school = False
                self.school_progress = 0
                self.skill_level += 1.5
                self.log_event(f"Graduated with {self.target_degree.value}!")
                self.happiness += 40
                self.life_milestones.append(f"Earned {self.target_degree.value}")
                
                # Update career prospects
                self.monthly_income = self.calculate_income()
        
        # Decide to go back to school
        elif not self.in_school and self.has_job and random.random() < 0.001:
            if self.education_level == EducationLevel.HIGH_SCHOOL:
                self.target_degree = EducationLevel.BACHELORS
            elif self.education_level == EducationLevel.BACHELORS:
                self.target_degree = EducationLevel.MASTERS
            else:
                return
            
            if self.money > 10000 or random.random() < 0.5:
                self.in_school = True
                self.school_progress = 0
                self.student_loan_debt += random.uniform(20000, 60000)
                self.log_event(f"Enrolled in {self.target_degree.value} program")
    
    def handle_career_progression(self):
        """Handle promotions, job changes, career development"""
        if not self.has_job:
            # Job hunting
            if random.random() < 0.02:  # 2% daily chance
                self.has_job = True
                self.monthly_income = self.calculate_income()
                self.job_stability = 70
                self.job_satisfaction = random.uniform(50, 80)
                self.log_event(f"Found new job: {self.job_title}")
                self.happiness += 30
                self.mental_health += 20
        else:
            # Experience gain
            self.years_experience += 1/365.0
            
            # Promotion chance
            if random.random() < 0.002 and self.job_satisfaction > 60:
                old_income = self.monthly_income
                self.monthly_income *= random.uniform(1.15, 1.35)
                raise_amount = self.monthly_income - old_income
                self.job_title = f"Senior {self.job_title}"
                self.log_event(f"Promoted! Raise: +${raise_amount:.0f}/month")
                self.happiness += 25
                self.job_satisfaction += 15
                self.career_achievements.append(f"Promoted to {self.job_title}")
                self.life_milestones.append("Career promotion")
            
            # Job satisfaction changes
            if self.stress > 70:
                self.job_satisfaction -= random.uniform(0.5, 2)
            elif self.happiness > 70:
                self.job_satisfaction += random.uniform(0.2, 1)
    
    def handle_hobbies(self):
        """Engage in hobbies"""
        if random.random() < 0.2 and len(self.hobbies) > 0:
            hobby_name = random.choice(list(self.hobbies.keys()))
            hobby = self.hobbies[hobby_name]
            
            if self.money > hobby.cost and self.energy > 20:
                self.money -= hobby.cost
                self.energy -= 15
                self.happiness += hobby.happiness_gain
                self.stress -= random.uniform(5, 15)
                hobby.skill_level += hobby.skill_gain
                
                # Master level achievements
                if hobby.skill_level > 100 and random.random() < 0.1:
                    bonus = random.uniform(500, 5000)
                    self.money += bonus
                    self.log_event(f"Won competition/sold work in {hobby_name}: +${bonus:.0f}")
                    self.reputation += 10
    
    def handle_investments(self):
        """Handle investment gains/losses"""
        if self.investments > 0:
            # Market fluctuation
            daily_return = random.uniform(-0.003, 0.004)  # -0.3% to +0.4% daily
            
            # Investment knowledge helps
            if self.investment_knowledge > 50:
                daily_return += 0.0005
            
            change = self.investments * daily_return
            self.investments += change
            
            if abs(change) > 100:
                if change > 0:
                    self.happiness += 2
                else:
                    self.stress += 2
        
        # Decide to invest
        if self.money > 5000 and random.random() < 0.005:
            investment_amount = self.money * random.uniform(0.05, 0.2)
            self.money -= investment_amount
            self.investments += investment_amount
            self.log_event(f"Invested ${investment_amount:.0f}")
    
    def handle_home_purchase(self):
        """Handle buying a home"""
        if not self.owns_home and self.money > 50000 and self.credit_score > 650:
            if random.random() < 0.001:  # Rare event
                down_payment = random.uniform(30000, 80000)
                self.home_value = down_payment * random.uniform(4, 8)
                self.money -= down_payment
                self.owns_home = True
                self.mortgage_payment = self.home_value * 0.004
                self.rent = 0
                self.log_event(f"Bought house for ${self.home_value:.0f}!")
                self.happiness += 40
                self.life_milestones.append("Became homeowner")
                
                # One of the life goals
                for i, goal in enumerate(self.life_goals):
                    if goal[0] == 'buy_house':
                        self.completed_goals.append(goal)
                        self.life_goals.pop(i)
                        self.happiness += 30
                        break
    
    def handle_major_purchases(self):
        """Handle buying cars, electronics, etc."""
        if random.random() < 0.003 and self.money > 10000:
            purchase_types = ['new_car', 'electronics', 'furniture', 'vacation']
            purchase = random.choice(purchase_types)
            
            costs = {
                'new_car': random.uniform(15000, 40000),
                'electronics': random.uniform(1000, 5000),
                'furniture': random.uniform(2000, 8000),
                'vacation': random.uniform(2000, 10000)
            }
            
            cost = costs[purchase]
            if self.money > cost * 1.5:  # Can afford it comfortably
                self.money -= cost
                self.happiness += random.uniform(15, 35)
                self.log_event(f"Major purchase: {purchase} -${cost:.0f}")
                self.major_purchases.append(purchase)
                
                if purchase == 'new_car':
                    self.car_value = cost
                    self.car_age = 0
                    self.car_working = True
    
    def handle_pregnancy(self):
        """Handle pregnancy and childbirth"""
        if self.gender == 'female' and self.relationship_status in ['married', 'dating']:
            if random.random() < 0.0008:  # ~30% yearly chance
                self.log_event("Pregnancy discovered!")
                self.mental_health += random.uniform(-15, 25)
                self.stress += random.uniform(10, 30)
                
                # Simplified: baby arrives
                if random.random() < 0.95:  # 95% successful pregnancy
                    baby_gender = random.choice(['male', 'female'])
                    baby = Person(f"Child{len(self.children)+1}", 0, baby_gender, 'child', ai_controlled=True)
                    self.children.append(baby)
                    self.log_event(f"Gave birth to {baby.name}!")
                    
                    # Medical costs
                    if self.has_health_insurance:
                        cost = random.uniform(2000, 6000)
                    else:
                        cost = random.uniform(15000, 35000)
                    
                    self.money -= cost
                    self.happiness += random.uniform(30, 60)
                    self.mental_health -= random.uniform(10, 25)
                    self.life_milestones.append("Became a parent")
                    
                    # Check life goal
                    for i, goal in enumerate(self.life_goals):
                        if goal[0] == 'have_children':
                            self.completed_goals.append(goal)
                            self.life_goals.pop(i)
                            self.happiness += 20
                            break
    
    def handle_substance_use(self):
        """Handle alcohol, drugs, smoking"""
        # Smoking
        if self.smoking:
            self.health -= self.smoking_intensity * 0.01
            self.money -= self.smoking_intensity * 0.3
            
            # Quit attempt
            if random.random() < 0.002:
                self.smoking = False
                self.smoking_intensity = 0
                self.log_event("Quit smoking!")
                self.happiness += 15
                self.health += 5
        
        # Alcohol
        if self.alcohol_dependency > 0:
            self.health -= self.alcohol_dependency * 0.06
            self.mental_health -= self.alcohol_dependency * 0.04
            self.money -= self.alcohol_dependency * 0.6
            self.job_satisfaction -= self.alcohol_dependency * 0.02
            
            if self.alcohol_dependency > 30 and random.random() < 0.03:
                self.job_stability -= random.uniform(5, 20)
                self.log_event("Alcohol affecting work")
            
            if not self.in_recovery:
                self.days_sober_alcohol = 0
                if random.random() < 0.006:
                    self.in_recovery = True
                    self.log_event("Entered alcohol recovery")
                    self.money -= random.uniform(3000, 12000)
            else:
                self.days_sober_alcohol += 1
                self.alcohol_dependency -= 0.4
                if self.days_sober_alcohol > 90:
                    self.mental_health += 0.6
                    self.health += 0.4
        
        # Drugs
        if self.drug_dependency > 0:
            self.health -= self.drug_dependency * 0.10
            self.mental_health -= self.drug_dependency * 0.08
            self.money -= self.drug_dependency * 2.0
            
            if self.drug_dependency > 50:
                if random.random() < 0.002:
                    self.health -= random.uniform(50, 90)
                    self.log_event("Drug overdose!")
                    hospital_cost = random.uniform(25000, 120000)
                    if not self.has_health_insurance:
                        self.money -= hospital_cost
                        if self.money < 0:
                            self.debt += abs(self.money)
                            self.money = 0
            
            if random.random() < 0.004:
                self.handle_arrest("drug_possession")
        
        # Triggers
        if self.mental_health < 25 or self.happiness < 15 or self.stress > 80:
            if random.random() < 0.015:
                choice = random.random()
                if choice < 0.6:
                    self.alcohol_dependency += random.uniform(5, 18)
                    self.log_event("Drinking to cope")
                elif choice < 0.85:
                    self.smoking = True
                    self.smoking_intensity = random.uniform(10, 20)
                    self.log_event("Started smoking")
                else:
                    self.drug_dependency += random.uniform(10, 30)
                    self.log_event("Using drugs to cope")
    
    def handle_arrest(self, crime_type):
        """Handle arrests"""
        self.arrest_count += 1
        self.criminal_record.append(crime_type)
        self.log_event(f"Arrested: {crime_type.replace('_', ' ')}")
        
        bail = random.uniform(500, 15000)
        lawyer = random.uniform(2000, 20000)
        self.money -= (bail + lawyer)
        
        if self.money < 0:
            self.debt += abs(self.money)
            self.money = 0
        
        self.mental_health -= random.uniform(15, 40)
        self.happiness -= random.uniform(20, 45)
        self.reputation -= random.uniform(15, 35)
        self.stress += random.uniform(20, 40)
        
        jail_chances = {
            'traffic_violation': 0.05, 'DUI': 0.45, 'drug_possession': 0.55,
            'theft': 0.65, 'assault': 0.75, 'fraud': 0.6
        }
        
        if random.random() < jail_chances.get(crime_type, 0.4):
            self.in_jail = True
            self.jail_days_remaining = random.randint(30, 1095)
            self.log_event(f"Sentenced: {self.jail_days_remaining} days")
            
            if self.has_job and random.random() < 0.95:
                self.has_job = False
                self.monthly_income = 0
                self.log_event("Lost job due to incarceration")
        else:
            self.probation = True
            self.probation_days_remaining = random.randint(180, 1095)
        
        self.credit_score -= random.randint(50, 150)
    
    def handle_traffic_violations(self):
        """Traffic tickets and DUIs"""
        if self.car_working and not self.license_suspended:
            if random.random() < 0.004:
                fine = random.uniform(150, 600)
                self.money -= fine
                self.traffic_tickets += 1
                self.log_event(f"Traffic ticket: -${fine:.0f}")
                
                if self.traffic_tickets > 6:
                    self.license_suspended = True
                    self.license_suspension_days = random.randint(30, 240)
                    self.log_event(f"License suspended: {self.license_suspension_days} days")
            
            if self.alcohol_dependency > 25 and random.random() < 0.003:
                self.handle_arrest("DUI")
                self.license_suspended = True
                self.license_suspension_days = random.randint(90, 365)
                self.money -= random.uniform(5000, 18000)
                
                if self.has_car_insurance:
                    self.car_insurance_cost_monthly *= random.uniform(2.5, 5.0)
    
    def calculate_daily_reward(self):
        """RL reward calculation"""
        reward = 0.0
        
        if self.alive and not self.in_jail:
            reward += 1.0
        elif self.in_jail:
            reward -= 3.0
        else:
            return -100.0
        
        reward += (self.health - 50) / 50.0 * 0.5
        reward += (self.mental_health - 50) / 50.0 * 0.6
        reward += (self.happiness - 50) / 50.0 * 1.0
        reward -= (self.stress - 50) / 50.0 * 0.4
        
        if self.money > 0:
            reward += min(1.2, self.money / 10000.0) * 0.4
        else:
            reward -= 0.6
        
        if self.debt > 0:
            reward -= min(2.5, self.debt / 5000.0) * 0.4
        
        if self.relationship_status in ['married', 'dating']:
            reward += (self.relationship_satisfaction / 100.0) * 0.4
        
        reward += len(self.children) * 0.15
        reward += len(self.completed_goals) * 2.0
        reward += (self.reputation / 100.0) * 0.3
        
        reward -= (self.alcohol_dependency / 100.0) * 1.0
        reward -= (self.drug_dependency / 100.0) * 1.5
        reward -= len(self.criminal_record) * 0.15
        
        if self.has_job:
            reward += 0.4 * (self.job_satisfaction / 100.0)
        else:
            reward -= 0.6
        
        reward += len([f for f in self.family_members if f.alive]) / max(1, len(self.family_members)) * 0.3
        reward += len(self.friends) * 0.05
        
        self.daily_rewards.append(reward)
        self.total_reward += reward
        return reward
    
    def daily_routine(self):
        if not self.alive:
            return
        
        # Jail time
        if self.in_jail:
            self.jail_days_remaining -= 1
            self.mental_health -= 0.6
            self.happiness -= 1.2
            self.health -= 0.4
            self.stress += 0.8
            self.day += 1
            self.age += 1/365.0
            
            if self.jail_days_remaining <= 0:
                self.in_jail = False
                self.log_event("Released from jail")
                self.happiness += 25
            
            self.log_day()
            self.calculate_daily_reward()
            return
        
        self.day += 1
        self.age += 1/365.0
        
        if self.verbose:
            print(f"\n--- Day {self.day} ({self.name}, Age {self.age:.1f}) ---")
        
        # License/probation
        if self.license_suspended:
            self.license_suspension_days -= 1
            if self.license_suspension_days <= 0:
                self.license_suspended = False
                self.log_event("License reinstated")
        
        if self.probation:
            self.probation_days_remaining -= 1
            if self.probation_days_remaining <= 0:
                self.probation = False
                self.log_event("Probation ended")
            elif random.random() < 0.003:
                self.handle_arrest("probation_violation")
        
        # Daily costs
        inflation = 1 + (self.day // 365) * 0.02
        daily_cost = random.uniform(40, 100) * inflation
        
        # Children costs
        for child in self.children:
            if child.alive and child.age < 18:
                daily_cost += random.uniform(25, 90)
            elif child.alive and 18 <= child.age < 22:
                if random.random() < 0.6:  # College support
                    daily_cost += random.uniform(50, 150)
        
        self.money -= daily_cost
        
        if self.child_support_payment > 0 and self.day % 30 == 1:
            self.money -= self.child_support_payment
        
        # Financial stress
        if self.money < 1000:
            self.stress += 1.5
            self.mental_health -= 0.8
            self.happiness -= 1.0
        
        if self.money < 0:
            self.debt += abs(self.money)
            self.money = 0
            self.stress += 2.0
            self.mental_health -= 1.5
            self.happiness -= 2.5
            self.credit_score -= 1
        
        # Monthly expenses
        if self.day % 30 == 1:
            if self.owns_home:
                self.money -= self.mortgage_payment
            else:
                self.money -= self.rent
            
            self.money -= self.insurance_cost_monthly
            self.money -= self.car_insurance_cost_monthly
            self.money -= self.gym_cost_monthly
            
            if self.therapy:
                therapy_cost = random.uniform(200, 600)
                self.money -= therapy_cost
                self.mental_health += 6
                self.stress -= 8
            
            if self.medication:
                self.money -= self.medication_cost_monthly
                self.mental_health += 4
            
            # Student loans
            if self.student_loan_debt > 0:
                interest = self.student_loan_debt * 0.05 / 12
                self.student_loan_debt += interest
                payment = max(interest * 1.5, self.student_loan_debt * 0.01)
                payment = min(payment, self.money * 0.15)
                self.money -= payment
                self.student_loan_debt -= payment
                self.stress += 5 if self.student_loan_debt > 30000 else 2
            
            # Debt payments
            if self.debt > 0:
                interest = self.debt * 0.12 / 12
                self.debt += interest
                payment = min(interest * 2, self.money * 0.1)
                self.money -= payment
                self.debt -= payment
                self.stress += 10 if self.debt > 10000 else 4
            
            # Paycheck
            if self.has_job:
                gross = self.monthly_income * (self.job_stability / 100) * (1 + (self.skill_level - 1) * 0.25)
                taxes = gross * 0.22
                retirement = gross * 0.06
                net = gross - taxes - retirement
                
                self.money += net
                self.has_retirement_savings += retirement
                
                # Credit score improvement
                if self.money > 0:
                    self.credit_score += random.randint(0, 2)
                    self.credit_score = min(850, self.credit_score)
        
        # Natural decline
        self.health -= 0.03
        self.mental_health -= 0.06
        self.happiness -= 0.12
        self.energy = min(100, self.energy + 50)
        self.stress -= 0.5 if self.stress > 20 else 0
        
        # Eating
        calories = random.randint(1600, 3200)
        net_cal = calories - 2400
        self.weight += net_cal / 7700.0
        
        # Exercise
        if random.random() < (0.5 if self.gym_membership else 0.3):
            self.weight -= random.uniform(0.2, 0.7)
            self.health += random.uniform(0.8, 1.8)
            self.mental_health += random.uniform(1, 4)
            self.happiness += random.uniform(4, 12)
            self.stress -= random.uniform(5, 12)
        
        self.weight = max(40, min(200, self.weight))
        
        # Hobbies
        self.handle_hobbies()
        
        # Career progression
        self.handle_career_progression()
        
        # Education
        self.handle_education_progression()
        
        # Investments
        self.handle_investments()
        
        # Home purchase
        self.handle_home_purchase()
        
        # Major purchases
        self.handle_major_purchases()
        
        # Substance use
        self.handle_substance_use()
        
        # Traffic
        self.handle_traffic_violations()
        
        # Family events
        self.check_family_events()
        
        # Pregnancy
        if self.gender == 'female':
            self.handle_pregnancy()
        
        # AI NPCs
        self.simulate_npc_interactions()
        
        # Age children
        for child in self.children:
            if child.alive:
                child.age_one_day()
                if child.should_die():
                    self.handle_family_death(child)
        
        # Random events
        event_roll = random.random()
        
        if event_roll < 0.55:
            if event_roll < 0.04:
                # Illness
                self.sick = True
                self.sick_days_remaining = random.randint(3, 25)
                self.sickness_severity = random.uniform(3, 12)
                self.log_event("Fell ill")
                
            elif event_roll < 0.07:
                # New chronic condition
                if random.random() < 0.3:
                    conditions = ['diabetes', 'hypertension', 'arthritis', 'asthma', 'depression']
                    new_condition = random.choice([c for c in conditions if c not in self.chronic_conditions])
                    if new_condition:
                        self.chronic_conditions.append(new_condition)
                        self.health -= random.uniform(10, 25)
                        self.medication = True
                        self.medication_cost_monthly += random.uniform(100, 500)
                        self.log_event(f"Diagnosed with {new_condition}")
                        
            elif event_roll < 0.12:
                # Relationship events
                if self.relationship_status == 'single':
                    if random.random() < 0.4:
                        self.relationship_status = 'dating'
                        self.relationship_satisfaction = random.uniform(55, 90)
                        self.log_event("Started dating")
                        self.happiness += 25
                        self.social_support += 15
                        
                elif self.relationship_status == 'dating':
                    if random.random() < 0.08:
                        self.relationship_status = 'married'
                        spouse_gender = random.choice(['male', 'female', 'non-binary'])
                        self.spouse = Person(self.generate_name(), random.randint(23, 38), spouse_gender, 'spouse', ai_controlled=True)
                        self.log_event("Got married!")
                        self.happiness += 40
                        self.life_milestones.append("Got married")
                        
                        # Wedding
                        wedding_cost = random.uniform(10000, 60000)
                        self.money -= wedding_cost
                        
                        # Goal check
                        for i, goal in enumerate(self.life_goals):
                            if goal[0] == 'get_married':
                                self.completed_goals.append(goal)
                                self.life_goals.pop(i)
                                self.happiness += 25
                                break
                    elif random.random() < 0.06:
                        self.relationship_status = 'single'
                        self.log_event("Broke up")
                        self.happiness -= 30
                        self.mental_health -= 25
                        self.stress += 20
                        
                elif self.relationship_status == 'married':
                    if self.relationship_satisfaction < 25 and random.random() < 0.025:
                        self.relationship_status = 'single'
                        self.log_event("Divorced")
                        self.happiness -= 45
                        self.mental_health -= 40
                        self.stress += 35
                        
                        divorce_cost = random.uniform(8000, 70000)
                        self.money -= divorce_cost
                        
                        if len(self.children) > 0 and random.random() < 0.7:
                            self.child_support_payment = random.uniform(400, 2500)
                        
                        self.spouse = None
                        
            elif event_roll < 0.16:
                # Windfall
                amount = random.uniform(300, 4000)
                self.money += amount
                self.happiness += 18
                self.log_event(f"Windfall: +${amount:.0f}")
                
            elif event_roll < 0.20:
                # Unexpected expense
                cost = random.uniform(400, 4000)
                self.money -= cost
                self.stress += 15
                self.happiness -= 18
                self.log_event(f"Unexpected expense: -${cost:.0f}")
                
            elif event_roll < 0.23:
                # Car problems
                if self.car_working:
                    self.car_working = False
                    self.car_issue_severity = random.uniform(1, 10)
                    self.car_repair_cost_parts = 150 + self.car_issue_severity * 400 + random.randint(0, 1200)
                    self.car_repair_cost_shop = self.car_repair_cost_parts * random.uniform(1.7, 3.2)
                    self.log_event(f"Car breakdown! Parts: ${self.car_repair_cost_parts:.0f}, Shop: ${self.car_repair_cost_shop:.0f}")
                    self.stress += 20
                    
            elif event_roll < 0.26:
                # Mental health crisis
                if self.mental_health < 35 or self.stress > 75:
                    self.mental_health -= random.uniform(8, 30)
                    self.stress += random.uniform(10, 25)
                    self.log_event("Mental health crisis")
                    
                    if random.random() < 0.4:
                        self.therapy = True
                        self.medication = True
                        self.medication_cost_monthly = random.uniform(100, 500)
                        
            elif event_roll < 0.29:
                # Crime temptation
                if self.money < 800 and not self.has_job:
                    if random.random() < 0.08:
                        crimes = ['theft', 'fraud', 'burglary']
                        crime = random.choice(crimes)
                        
                        if random.random() < 0.65:
                            stolen = random.uniform(400, 6000)
                            self.money += stolen
                            self.mental_health -= 20
                            self.reputation -= 15
                            self.log_event(f"Committed {crime}: +${stolen:.0f}")
                        else:
                            self.handle_arrest(crime)
        
        # Sickness effects
        if self.sick:
            self.health -= self.sickness_severity * 0.9
            self.energy -= 35
            self.happiness -= 6
            self.stress += 5
            self.sick_days_remaining -= 1
            
            if self.has_job:
                self.job_stability -= random.uniform(1, 3)
            
            if self.sick_days_remaining <= 0:
                self.sick = False
                self.log_event("Recovered from illness")
                self.happiness += 12
        
        # Chronic conditions
        for condition in self.chronic_conditions:
            self.health -= random.uniform(0.05, 0.2)
            if not self.medication:
                self.health -= random.uniform(0.1, 0.4)
        
        # Car repair
        if not self.car_working:
            if self.money >= self.car_repair_cost_parts and random.random() < 0.25:
                cost = self.car_repair_cost_parts
                self.money -= cost
                if random.random() < (0.35 + self.skill_level * 0.15):
                    self.car_working = True
                    self.log_event(f"DIY car repair: ${cost:.0f}")
                    self.happiness += 18
                else:
                    self.log_event("DIY repair failed")
                    self.stress += 10
            elif self.money >= self.car_repair_cost_shop and random.random() < 0.4:
                cost = self.car_repair_cost_shop
                self.money -= cost
                self.car_working = True
                self.log_event(f"Professional repair: ${cost:.0f}")
                self.happiness += 12
        
        # Relationship dynamics
        if self.relationship_status in ['married', 'dating']:
            if self.mental_health > 55 and self.happiness > 50 and self.stress < 60:
                self.relationship_satisfaction += random.uniform(0, 0.8)
            else:
                self.relationship_satisfaction -= random.uniform(0.2, 1.5)
            
            self.relationship_satisfaction = max(0, min(100, self.relationship_satisfaction))
        
        # Job loss
        if self.has_job:
            if self.job_stability < 15 and random.random() < 0.12:
                self.has_job = False
                self.monthly_income = 0
                self.job_stability = 0
                self.job_satisfaction = 0
                self.happiness -= 35
                self.mental_health -= 30
                self.stress += 40
                self.log_event("Lost job")
        
        # Happiness tracking
        if self.happiness < 15:
            self.low_happiness_streak += 1
        else:
            self.low_happiness_streak = 0
        
        # Death conditions
        if self.health <= 0:
            self.alive = False
            self.cause_of_end = "health_failure"
            self.log_event("Died from health complications")
        elif self.mental_health <= 0:
            self.alive = False
            self.cause_of_end = "suicide"
            self.log_event("Died by suicide")
        elif self.low_happiness_streak > 400:
            self.alive = False
            self.cause_of_end = "gave_up"
            self.log_event("Lost the will to live")
        elif self.bmi() < 13 or self.bmi() > 55:
            self.alive = False
            self.cause_of_end = "weight_related"
            self.log_event(f"Died from weight complications (BMI: {self.bmi()})")
        elif (self.alcohol_dependency > 95 or self.drug_dependency > 95) and random.random() < 0.015:
            self.alive = False
            self.cause_of_end = "overdose"
            self.log_event("Died from overdose")
        elif self.age > 85 and random.random() < 0.005:
            self.alive = False
            self.cause_of_end = "old_age"
            self.log_event("Died of old age")
        
        # Clamp
        self.health = max(0, min(100, self.health))
        self.mental_health = max(0, min(100, self.mental_health))
        self.energy = max(0, min(100, self.energy))
        self.happiness = max(0, min(100, self.happiness))
        self.stress = max(0, min(100, self.stress))
        self.job_stability = max(0, min(100, self.job_stability))
        self.job_satisfaction = max(0, min(100, self.job_satisfaction))
        self.reputation = max(0, min(100, self.reputation))
        self.weight = max(40, min(200, self.weight))
        self.credit_score = max(300, min(850, self.credit_score))
        
        self.log_day()
        self.calculate_daily_reward()


def run_simulation(days=1825, seed=None, verbose=False):
    """Run enhanced simulation"""
    sim = EnhancedLifeSimulation(seed=seed, verbose=verbose)
    
    for _ in range(days):
        sim.daily_routine()
        if not sim.alive:
            break
    
    # Summary
    print(f"\n{'='*80}")
    print(f"ENHANCED LIFE SIMULATION - {sim.name} ({sim.gender}, {sim.personality.value})")
    print(f"{'='*80}")
    print(f"Survived: {sim.day} days ({sim.day/365:.2f} years)")
    print(f"Final Age: {sim.age:.1f}")
    if not sim.alive:
        print(f"Cause of death: {sim.cause_of_end}")
    
    print(f"\nFinal Stats:")
    print(f"  Health: {sim.health:.1f} | Mental: {sim.mental_health:.1f} | Happiness: {sim.happiness:.1f}")
    print(f"  Stress: {sim.stress:.1f} | Energy: {sim.energy:.1f}")
    print(f"  Weight: {sim.weight:.1f}kg (BMI: {sim.bmi()})")
    
    print(f"\nFinancial:")
    print(f"  Money: ${sim.money:,.0f} | Debt: ${sim.debt:,.0f}")
    print(f"  Investments: ${sim.investments:,.0f} | Retirement: ${sim.has_retirement_savings:,.0f}")
    if sim.owns_home:
        print(f"  Home Value: ${sim.home_value:,.0f}")
    print(f"  Net Worth: ${sim.money + sim.investments + sim.has_retirement_savings - sim.debt:,.0f}")
    print(f"  Credit Score: {sim.credit_score}")
    
    print(f"\nCareer:")
    print(f"  Field: {sim.career_field.value} | Title: {sim.job_title}")
    print(f"  Education: {sim.education_level.value}")
    print(f"  Income: ${sim.monthly_income:,.0f}/mo | Satisfaction: {sim.job_satisfaction:.0f}")
    print(f"  Achievements: {len(sim.career_achievements)}")
    
    print(f"\nRelationships:")
    print(f"  Status: {sim.relationship_status}")
    if sim.relationship_status in ['married', 'dating']:
        print(f"  Satisfaction: {sim.relationship_satisfaction:.1f}")
    print(f"  Children: {len(sim.children)}")
    alive_family = len([f for f in sim.family_members if f.alive])
    print(f"  Family alive: {alive_family}/{len(sim.family_members)}")
    print(f"  Friends: {len(sim.friends)} | Reputation: {sim.reputation:.0f}")
    
    print(f"\nLife Milestones: {len(sim.life_milestones)}")
    for milestone in sim.life_milestones[:10]:
        print(f"  • {milestone}")
    
    print(f"\nCompleted Goals: {len(sim.completed_goals)}/{len(sim.completed_goals) + len(sim.life_goals)}")
    for goal in sim.completed_goals[:5]:
        print(f"  ✓ {goal[1]}")
    
    print(f"\nHobbies: {len(sim.hobbies)}")
    for hobby_name, hobby in list(sim.hobbies.items())[:5]:
        print(f"  • {hobby_name} (skill: {hobby.skill_level:.0f})")
    
    print(f"\nSubstances:")
    print(f"  Alcohol: {sim.alcohol_dependency:.1f} | Drugs: {sim.drug_dependency:.1f}")
    if sim.smoking:
        print(f"  Smoking: {sim.smoking_intensity:.1f} cigs/day")
    
    print(f"\nLegal:")
    print(f"  Arrests: {sim.arrest_count} | Record: {len(sim.criminal_record)}")
    if sim.criminal_record:
        print(f"  Crimes: {', '.join(set(sim.criminal_record))}")
    
    print(f"\nAI NPCs in world: {len(sim.ai_npcs)}")
    print(f"NPC interactions: {len(sim.npc_interactions)}")
    
    print(f"\nRL Metrics:")
    print(f"  Total Reward: {sim.total_reward:.1f}")
    print(f"  Avg Daily Reward: {sim.total_reward/max(1, sim.day):.3f}")
    print(f"{'='*80}\n")
    
    # Create visualizations
    df = pd.DataFrame(sim.logs)
    
    fig, axes = plt.subplots(5, 3, figsize=(20, 20))
    fig.suptitle(f'Enhanced Life Simulation: {sim.name}', fontsize=18, fontweight='bold')
    
    # Row 1
    axes[0,0].plot(df['day'], df['health'], label='Health', color='red', alpha=0.8)
    axes[0,0].plot(df['day'], df['mental_health'], label='Mental', color='purple', alpha=0.8)
    axes[0,0].set_title('Health Metrics')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    axes[0,1].plot(df['day'], df['happiness'], color='orange', linewidth=2, label='Happiness')
    axes[0,1].plot(df['day'], df['stress'], color='red', linewidth=2, alpha=0.6, label='Stress')
    axes[0,1].set_title('Happiness vs Stress')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    axes[0,2].plot(df['day'], df['weight'], label='Weight', color='blue')
    ax2 = axes[0,2].twinx()
    ax2.plot(df['day'], df['bmi'], label='BMI', color='darkblue', linestyle='--')
    axes[0,2].set_title('Weight & BMI')
    axes[0,2].legend(loc='upper left')
    ax2.legend(loc='upper right')
    axes[0,2].grid(True, alpha=0.3)
    
    # Row 2
    axes[1,0].plot(df['day'], df['net_worth'], label='Net Worth', color='darkgreen', linewidth=2.5)
    axes[1,0].plot(df['day'], df['money'], label='Cash', color='green', alpha=0.5)
    axes[1,0].axhline(y=0, color='black', linestyle='-', alpha=0.4)
    axes[1,0].set_title('Financial Overview')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    axes[1,1].plot(df['day'], df['job_satisfaction'], label='Job Satisfaction', color='blue', linewidth=2)
    axes[1,1].plot(df['day'], df['reputation'], label='Reputation', color='purple', alpha=0.7)
    axes[1,1].set_title('Career & Reputation')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    axes[1,2].plot(df['day'], df['alcohol_dependency'], label='Alcohol', color='brown', alpha=0.7)
    axes[1,2].plot(df['day'], df['drug_dependency'], label='Drugs', color='red', alpha=0.7)
    axes[1,2].set_title('Substance Dependency')
    axes[1,2].legend()
    axes[1,2].grid(True, alpha=0.3)
    
    # Row 3
    axes[2,0].plot(df['day'], df['num_children'], label='Children', color='pink', linewidth=2)
    axes[2,0].plot(df['day'], df['num_family_alive'], label='Family Alive', color='purple', alpha=0.6)
    axes[2,0].plot(df['day'], df['num_friends'], label='Friends', color='blue', alpha=0.6)
    axes[2,0].set_title('Relationships')
    axes[2,0].legend()
    axes[2,0].grid(True, alpha=0.3)
    
    axes[2,1].plot(df['day'], df['criminal_record'], color='red', linewidth=2)
    axes[2,1].fill_between(df['day'], 0, df['in_jail'].astype(int) * df['criminal_record'].max() if df['criminal_record'].max() > 0 else 1,
                           alpha=0.3, label='In Jail', color='orange')
    axes[2,1].set_title('Criminal Record')
    axes[2,1].legend()
    axes[2,1].grid(True, alpha=0.3)
    
    axes[2,2].plot(df['day'], df['num_ai_npcs'], color='teal', linewidth=2)
    axes[2,2].set_title('AI NPCs in World')
    axes[2,2].grid(True, alpha=0.3)
    
    # Row 4
    if sim.daily_rewards:
        axes[3,0].plot(range(len(sim.daily_rewards)), sim.daily_rewards, color='darkblue', alpha=0.6)
        axes[3,0].axhline(y=0, color='black', linestyle='-', alpha=0.5)
        axes[3,0].set_title('Daily RL Rewards')
        axes[3,0].grid(True, alpha=0.3)
        
        cumulative = [sum(sim.daily_rewards[:i+1]) for i in range(len(sim.daily_rewards))]
        axes[3,1].plot(range(len(cumulative)), cumulative, color='darkgreen', linewidth=2)
        axes[3,1].set_title('Cumulative Reward')
        axes[3,1].grid(True, alpha=0.3)
    
    # Energy over time
    axes[3,2].plot(df['day'], df['energy'], color='orange', linewidth=2)
    axes[3,2].set_title('Energy Levels')
    axes[3,2].grid(True, alpha=0.3)
    
    # Row 5 - Summary text panels
    event_text = "\n".join([e.split(': ', 1)[1] for e in sim.event_log[-20:]])
    axes[4,0].text(0.05, 0.95, f"Recent Events:\n{event_text}", 
                   fontsize=7, transform=axes[4,0].transAxes, 
                   verticalalignment='top', family='monospace')
    axes[4,0].axis('off')
    
    milestone_text = "\n".join([f"• {m}" for m in sim.life_milestones[-15:]])
    axes[4,1].text(0.05, 0.95, f"Life Milestones:\n{milestone_text}",
                   fontsize=7, transform=axes[4,1].transAxes,
                   verticalalignment='top', family='monospace')
    axes[4,1].axis('off')
    
    summary = f"""Final Summary:
Name: {sim.name}
Age: {sim.age:.1f} years
Status: {'Alive' if sim.alive else f'Deceased ({sim.cause_of_end})'}
Personality: {sim.personality.value}

Health: {sim.health:.0f}
Mental: {sim.mental_health:.0f}
Happiness: {sim.happiness:.0f}
Stress: {sim.stress:.0f}

Net Worth: ${sim.money + sim.investments - sim.debt:,.0f}
Career: {sim.job_title}
Education: {sim.education_level.value}

Children: {len(sim.children)}
Friends: {len(sim.friends)}
Arrests: {sim.arrest_count}

Goals: {len(sim.completed_goals)}/{len(sim.completed_goals) + len(sim.life_goals)}
Total Reward: {sim.total_reward:.0f}
    """
    axes[4,2].text(0.05, 0.95, summary, fontsize=9, 
                   transform=axes[4,2].transAxes,
                   verticalalignment='top', family='monospace')
    axes[4,2].axis('off')
    
    plt.tight_layout()
    plt.savefig('/home/claude/simulation_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return sim, df


if __name__ == "__main__":
    print("Running Enhanced Life Simulation with AI NPCs...")
    print("This includes:")
    print("- AI-controlled NPCs that age and die")
    print("- NPC-to-NPC interactions")
    print("- NPC-to-player interactions")
    print("- Enhanced career progression")
    print("- Education system")
    print("- Hobby system")
    print("- Life goals and achievements")
    print("- Home ownership")
    print("- Investment system")
    print("- Credit score tracking")
    print("- And much more!\n")
    
    sim, df = run_simulation(days=3650, seed=None, verbose=False)  # 10 years