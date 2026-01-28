import random
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import defaultdict
from enum import Enum

# Try to import TensorFlow, but make it optional
TF_AVAILABLE = False
TF_ERROR_MESSAGE = None

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, optimizers
    TF_AVAILABLE = True
    print("✓ TensorFlow loaded successfully")
except ImportError as e:
    TF_ERROR_MESSAGE = f"ImportError: {str(e)}"
    print("⚠ TensorFlow not available - RL training features disabled")
    print("  The simulation will still work perfectly for single runs!")
except Exception as e:
    TF_ERROR_MESSAGE = f"Error: {str(e)}"
    print("⚠ TensorFlow import failed - RL training features disabled")
    print("  The simulation will still work perfectly for single runs!")

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

class Pet:
    """Pet companion"""
    def __init__(self, pet_type, name, age=0):
        self.type = pet_type  # 'dog', 'cat', 'bird', etc.
        self.name = name
        self.age = age
        self.health = 100.0
        self.happiness = 80.0
        self.alive = True
        
        # Lifespan varies by type
        self.max_age = {
            'dog': 12,
            'cat': 15,
            'bird': 10,
            'fish': 3,
            'hamster': 2
        }.get(pet_type, 10)
        
    def age_one_day(self):
        self.age += 1/365.0
        self.health -= random.uniform(0, 0.1)
        
        # Aging effects
        if self.age > self.max_age * 0.7:
            self.health -= random.uniform(0.1, 0.3)
            
    def should_die(self):
        if self.age > self.max_age:
            return random.random() < 0.1
        return self.health <= 0 or random.random() < 0.0001

class Business:
    """Player-owned business"""
    def __init__(self, business_type, initial_investment):
        self.type = business_type
        self.value = initial_investment
        self.monthly_profit = 0
        self.age = 0
        self.success_level = random.uniform(0, 50)
        
    def operate_monthly(self, owner_skill, owner_time_invested):
        """Calculate monthly profit/loss"""
        self.age += 1
        
        # Base profit calculation
        base_profit = self.value * 0.05  # 5% monthly return on value
        
        # Factors
        skill_factor = 1 + (owner_skill / 100)
        time_factor = owner_time_invested / 100
        success_factor = 1 + (self.success_level / 100)
        market_factor = random.uniform(0.7, 1.3)
        
        profit = base_profit * skill_factor * time_factor * success_factor * market_factor
        
        # Random events
        if random.random() < 0.05:  # 5% chance of major event
            if random.random() < 0.5:
                # Good event
                profit *= random.uniform(1.5, 3.0)
            else:
                # Bad event
                profit *= random.uniform(0.3, 0.7)
        
        self.monthly_profit = profit - (self.value * 0.03)  # Operating costs
        self.value += self.monthly_profit * 0.1  # Growth
        self.success_level += random.uniform(-2, 3)
        self.success_level = max(0, min(100, self.success_level))
        
        return self.monthly_profit

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
        self.years_experience = random.uniform(0, 3)  # MOVED HERE - before calculate_income
        self.monthly_income = self.calculate_income()
        self.has_job = self.monthly_income > 0
        self.job_stability = 100.0 if self.has_job else 0
        self.job_satisfaction = random.uniform(40, 80) if self.has_job else 0
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
        
        # Pets
        self.pets = []
        if random.random() < 0.3:  # 30% start with a pet
            pet_type = random.choice(['dog', 'cat', 'bird', 'fish'])
            self.pets.append(Pet(pet_type, f"{pet_type.capitalize()}1", random.uniform(0, 5)))
        
        # Business ownership
        self.owns_business = False
        self.business = None
        
        # Mental health specifics
        self.has_anxiety = random.random() < 0.15
        self.has_depression = random.random() < 0.10
        self.ptsd = False
        
        # Additional tracking
        self.lottery_wins = []
        self.inheritances_received = []
        self.natural_disasters_survived = []
        self.major_accidents = []
        self.volunteer_hours = 0
        self.books_read = 0
        self.countries_visited = []
        self.languages_learned = []
        
        # Skills beyond job
        self.cooking_skill = random.uniform(0, 50)
        self.fitness_level = random.uniform(0, 50)
        self.creativity = random.uniform(0, 50)
        self.leadership = random.uniform(0, 50)
        
        # Political/social
        self.political_affiliation = random.choice(['liberal', 'conservative', 'moderate', 'none'])
        self.votes_cast = 0
        
        # Fame/notoriety
        self.fame_level = 0  # 0-100
        self.viral_moments = []
        
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
    
    def handle_pets(self):
        """Handle pet care and events"""
        pets_to_remove = []
        
        for pet in self.pets:
            pet.age_one_day()
            
            # Pet care costs
            daily_cost = {'dog': 3, 'cat': 2, 'bird': 1, 'fish': 0.5, 'hamster': 1}
            self.money -= daily_cost.get(pet.type, 2)
            
            # Pet benefits
            if pet.type in ['dog', 'cat']:
                self.happiness += random.uniform(1, 4)
                self.mental_health += random.uniform(0.5, 2)
                self.stress -= random.uniform(1, 3)
                self.social_support += 0.2
            
            # Pet health issues
            if random.random() < 0.002:
                vet_cost = random.uniform(200, 2000)
                self.money -= vet_cost
                self.stress += 10
                pet.health += 20
                self.log_event(f"{pet.name} had vet visit: ${vet_cost:.0f}")
            
            # Pet death
            if pet.should_die():
                pets_to_remove.append(pet)
                self.log_event(f"{pet.name} (pet {pet.type}) died at age {pet.age:.1f}")
                self.happiness -= random.uniform(20, 40)
                self.mental_health -= random.uniform(15, 30)
                self.stress += random.uniform(10, 25)
        
        for pet in pets_to_remove:
            self.pets.remove(pet)
        
        # Get a new pet
        if len(self.pets) == 0 and random.random() < 0.003:
            if self.money > 500:
                pet_type = random.choice(['dog', 'cat', 'bird', 'fish', 'hamster'])
                adoption_cost = random.uniform(50, 500)
                self.money -= adoption_cost
                self.pets.append(Pet(pet_type, f"{pet_type.capitalize()}1", 0))
                self.log_event(f"Adopted a {pet_type}!")
                self.happiness += 25
    
    def handle_natural_disasters(self):
        """Handle natural disasters"""
        if random.random() < 0.0001:  # Very rare
            disasters = ['hurricane', 'tornado', 'earthquake', 'flood', 'wildfire']
            disaster = random.choice(disasters)
            
            self.log_event(f"Natural disaster: {disaster}!")
            self.natural_disasters_survived.append(disaster)
            
            # Health impact
            injury_severity = random.uniform(0, 30)
            self.health -= injury_severity
            self.mental_health -= random.uniform(15, 40)
            self.stress += random.uniform(25, 50)
            self.ptsd = True if injury_severity > 15 else self.ptsd
            
            # Property damage
            if self.owns_home:
                damage = self.home_value * random.uniform(0.1, 0.8)
                self.home_value -= damage
                self.log_event(f"Home damaged: -${damage:.0f} value")
                
                # Insurance payout
                if self.has_health_insurance:
                    payout = damage * random.uniform(0.6, 0.9)
                    self.money += payout
                    self.log_event(f"Insurance payout: +${payout:.0f}")
            
            if self.car_working and random.random() < 0.4:
                self.car_working = False
                self.car_value *= random.uniform(0.3, 0.7)
                self.log_event("Car damaged in disaster")
            
            # Financial losses
            loss = random.uniform(1000, 20000)
            self.money -= loss
            
            # PTSD treatment
            if self.ptsd:
                self.therapy = True
                self.medication = True
                self.medication_cost_monthly += random.uniform(200, 500)
    
    def handle_accidents(self):
        """Handle random accidents"""
        if random.random() < 0.001:  # 0.1% daily
            accidents = ['car_crash', 'fall', 'sports_injury', 'work_accident', 'home_accident']
            accident = random.choice(accidents)
            
            severity = random.uniform(0, 100)
            
            if severity > 80:
                # Severe accident
                self.log_event(f"Severe {accident.replace('_', ' ')}!")
                self.health -= random.uniform(30, 60)
                self.mental_health -= random.uniform(15, 35)
                
                hospital_stay = random.randint(3, 30)
                if self.has_health_insurance:
                    cost = random.uniform(5000, 30000)
                else:
                    cost = random.uniform(30000, 200000)
                
                self.money -= cost
                self.stress += 40
                self.major_accidents.append(accident)
                
                # Disability chance
                if severity > 95:
                    self.chronic_conditions.append('disability')
                    self.log_event("Permanent disability from accident")
                    self.health -= 20
                    
                    if self.has_job:
                        self.monthly_income *= 0.6  # Reduced income
                        
            elif severity > 40:
                # Moderate accident
                self.log_event(f"Moderate {accident.replace('_', ' ')}")
                self.health -= random.uniform(10, 25)
                
                if self.has_health_insurance:
                    cost = random.uniform(1000, 8000)
                else:
                    cost = random.uniform(5000, 25000)
                    
                self.money -= cost
                self.stress += 15
            else:
                # Minor accident
                self.health -= random.uniform(2, 8)
                self.money -= random.uniform(200, 2000)
    
    def handle_lottery(self):
        """Handle lottery and gambling"""
        # Buy lottery ticket
        if random.random() < 0.01 and self.money > 10:
            ticket_cost = random.uniform(5, 20)
            self.money -= ticket_cost
            
            # Winning chances
            win_chance = random.random()
            
            if win_chance < 0.0001:  # Jackpot!
                winnings = random.uniform(1000000, 100000000)
                self.money += winnings
                self.log_event(f"LOTTERY JACKPOT: ${winnings:,.0f}!!!")
                self.lottery_wins.append(winnings)
                self.happiness += 100  # Will be clamped
                self.fame_level += 30
                self.viral_moments.append(f"lottery_win_{winnings:.0f}")
                self.life_milestones.append("Won lottery jackpot")
                
            elif win_chance < 0.001:  # Big win
                winnings = random.uniform(10000, 500000)
                self.money += winnings
                self.log_event(f"Lottery win: ${winnings:,.0f}!")
                self.lottery_wins.append(winnings)
                self.happiness += 50
                
            elif win_chance < 0.01:  # Small win
                winnings = random.uniform(100, 5000)
                self.money += winnings
                self.happiness += 10
    
    def handle_business_ownership(self):
        """Handle owning and operating a business"""
        if self.owns_business and self.business:
            # Monthly operations
            if self.day % 30 == 1:
                time_invested = random.uniform(40, 100) if self.has_job else 100
                profit = self.business.operate_monthly(self.skill_level * 10, time_invested)
                
                self.money += profit
                
                if profit > 0:
                    self.happiness += min(20, profit / 1000)
                    self.log_event(f"Business profit: +${profit:.0f}")
                else:
                    self.stress += min(20, abs(profit) / 1000)
                    self.log_event(f"Business loss: ${profit:.0f}")
                
                # Business failure
                if self.business.success_level < 10 and random.random() < 0.1:
                    self.log_event("Business failed!")
                    self.owns_business = False
                    self.mental_health -= 30
                    self.happiness -= 40
                    self.stress += 35
                    self.business = None
        
        # Start a business
        elif not self.owns_business and random.random() < 0.0005:
            if self.money > 20000 and self.skill_level > 2:
                investment = random.uniform(15000, 100000)
                
                if self.money > investment or random.random() < 0.4:
                    business_types = ['restaurant', 'retail', 'tech_startup', 'consulting', 'trade_service']
                    business_type = random.choice(business_types)
                    
                    self.money -= investment
                    self.business = Business(business_type, investment)
                    self.owns_business = True
                    self.log_event(f"Started {business_type} business!")
                    self.life_milestones.append("Started own business")
                    self.stress += 25
    
    def handle_inheritance_events(self):
        """Random inheritances from distant relatives"""
        if random.random() < 0.0002:  # Very rare
            inheritance = random.uniform(5000, 500000)
            self.money += inheritance
            self.inheritances_received.append(inheritance)
            self.log_event(f"Received inheritance: ${inheritance:,.0f}")
            self.happiness += min(40, inheritance / 10000)
    
    def handle_mental_health_conditions(self):
        """Handle specific mental health conditions"""
        # Anxiety
        if self.has_anxiety:
            self.stress += random.uniform(0.5, 2)
            self.mental_health -= random.uniform(0.2, 1)
            
            if not self.medication and random.random() < 0.01:
                self.medication = True
                self.medication_cost_monthly += random.uniform(50, 200)
                self.log_event("Started anxiety medication")
        
        # Depression
        if self.has_depression:
            self.happiness -= random.uniform(0.3, 1.5)
            self.energy -= random.uniform(0.2, 1)
            self.mental_health -= random.uniform(0.3, 1.2)
            
            if not self.therapy and random.random() < 0.02:
                self.therapy = True
                self.log_event("Started therapy for depression")
        
        # PTSD
        if self.ptsd:
            if random.random() < 0.05:  # Flashbacks/episodes
                self.mental_health -= random.uniform(5, 20)
                self.stress += random.uniform(10, 30)
                self.happiness -= random.uniform(10, 25)
        
        # Develop new conditions
        if self.stress > 80 and not self.has_anxiety and random.random() < 0.001:
            self.has_anxiety = True
            self.log_event("Developed anxiety disorder")
        
        if self.happiness < 20 and self.mental_health < 30 and not self.has_depression and random.random() < 0.001:
            self.has_depression = True
            self.log_event("Developed depression")
    
    def handle_skill_development(self):
        """Develop various skills through practice"""
        # Cooking
        if random.random() < 0.1:
            self.cooking_skill += random.uniform(0.1, 0.5)
            if self.cooking_skill > 80 and random.random() < 0.01:
                # Cooking side income
                earnings = random.uniform(100, 1000)
                self.money += earnings
                self.log_event(f"Catering job: +${earnings:.0f}")
        
        # Fitness
        if self.gym_membership and random.random() < 0.3:
            self.fitness_level += random.uniform(0.3, 1.0)
            self.health += random.uniform(0.2, 0.8)
        
        # Creativity
        for hobby_name, hobby in self.hobbies.items():
            if hobby.category == 'creative':
                self.creativity += 0.1
        
        # Leadership
        if self.has_job and self.job_satisfaction > 70:
            self.leadership += random.uniform(0.05, 0.2)
        
        # Skills cap at 100
        self.cooking_skill = min(100, self.cooking_skill)
        self.fitness_level = min(100, self.fitness_level)
        self.creativity = min(100, self.creativity)
        self.leadership = min(100, self.leadership)
    
    def handle_social_media_fame(self):
        """Handle viral moments and fame"""
        # Random viral moment
        if random.random() < 0.0005:
            viral_type = random.choice(['video', 'tweet', 'photo', 'blog_post'])
            self.fame_level += random.uniform(10, 40)
            self.viral_moments.append(viral_type)
            self.log_event(f"Went viral with {viral_type}!")
            
            # Fame effects
            self.happiness += 20
            self.social_support += 15
            self.stress += 10
            
            # Monetary gain
            earnings = random.uniform(1000, 50000)
            self.money += earnings
        
        # Fame decay
        if self.fame_level > 0:
            self.fame_level -= random.uniform(0.1, 0.5)
            self.fame_level = max(0, self.fame_level)
        
        # High fame effects
        if self.fame_level > 50:
            self.stress += random.uniform(0.5, 2)
            self.happiness += random.uniform(0, 1)
            
            # Chance of losing privacy/stalker
            if random.random() < 0.001:
                self.mental_health -= random.uniform(10, 30)
                self.stress += random.uniform(15, 35)
                self.log_event("Dealing with loss of privacy due to fame")
    
    def handle_education_achievements(self):
        """Reading, learning languages, etc."""
        # Reading
        if random.random() < 0.05:
            self.books_read += 1
            self.mental_health += random.uniform(1, 3)
            self.happiness += random.uniform(2, 6)
            self.creativity += random.uniform(0.2, 0.8)
            
            if self.books_read % 50 == 0:
                self.log_event(f"Read {self.books_read} books!")
                self.life_milestones.append(f"Read {self.books_read} books")
        
        # Learning languages
        if random.random() < 0.0003 and len(self.languages_learned) < 5:
            language = random.choice(['Spanish', 'French', 'German', 'Chinese', 'Japanese', 'Italian'])
            if language not in self.languages_learned:
                self.languages_learned.append(language)
                self.log_event(f"Learned {language}!")
                self.skill_level += 0.5
                self.happiness += 20
    
    def handle_travel(self):
        """Handle travel and vacations"""
        if random.random() < 0.002 and self.money > 2000:
            countries = ['France', 'Italy', 'Japan', 'Australia', 'Brazil', 'Egypt', 
                        'Thailand', 'Spain', 'Greece', 'Mexico', 'UK', 'Germany']
            country = random.choice([c for c in countries if c not in self.countries_visited])
            
            if country:
                cost = random.uniform(1500, 8000)
                self.money -= cost
                self.countries_visited.append(country)
                self.happiness += random.uniform(25, 50)
                self.stress -= random.uniform(20, 40)
                self.mental_health += random.uniform(10, 25)
                self.log_event(f"Traveled to {country}!")
                
                # Check travel goal
                if len(self.countries_visited) >= 10:
                    for i, goal in enumerate(self.life_goals):
                        if goal[0] == 'travel_world':
                            self.completed_goals.append(goal)
                            self.life_goals.pop(i)
                            self.happiness += 40
                            self.log_event("Completed travel goal!")
                            break
    
    def handle_political_engagement(self):
        """Voting and political activity"""
        # Election day (simplified - every 2 years)
        if self.day % 730 == 0 and self.age >= 18:
            if random.random() < 0.6:  # 60% voting rate
                self.votes_cast += 1
                self.happiness += random.uniform(3, 10)
                self.stress += random.uniform(2, 8)
                
                if self.votes_cast % 5 == 0:
                    self.log_event(f"Voted in {self.votes_cast} elections")
    
    def handle_volunteering(self):
        """Volunteer work"""
        if random.random() < 0.01:
            hours = random.uniform(2, 8)
            self.volunteer_hours += hours
            self.happiness += random.uniform(5, 15)
            self.mental_health += random.uniform(3, 10)
            self.reputation += random.uniform(2, 8)
            self.social_support += random.uniform(2, 6)
            
            if self.volunteer_hours >= 100 and self.volunteer_hours % 100 < 8:
                self.log_event(f"Volunteered {int(self.volunteer_hours)} hours total!")
                self.life_milestones.append(f"Volunteered {int(self.volunteer_hours)} hours")
    
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
        
        # Pets
        self.handle_pets()
        
        # Natural disasters
        self.handle_natural_disasters()
        
        # Accidents
        self.handle_accidents()
        
        # Lottery
        self.handle_lottery()
        
        # Business
        self.handle_business_ownership()
        
        # Random inheritances
        self.handle_inheritance_events()
        
        # Mental health conditions
        self.handle_mental_health_conditions()
        
        # Skill development
        self.handle_skill_development()
        
        # Social media/fame
        self.handle_social_media_fame()
        
        # Education (reading, languages)
        self.handle_education_achievements()
        
        # Travel
        self.handle_travel()
        
        # Political engagement
        self.handle_political_engagement()
        
        # Volunteering
        self.handle_volunteering()
        
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
    
    print(f"\nPets:")
    if sim.pets:
        for pet in sim.pets:
            print(f"  {pet.name} ({pet.type}), age {pet.age:.1f}")
    else:
        print(f"  No pets")
    
    print(f"\nBusiness:")
    if sim.owns_business:
        print(f"  Type: {sim.business.type}")
        print(f"  Value: ${sim.business.value:,.0f}")
        print(f"  Monthly profit: ${sim.business.monthly_profit:,.0f}")
    else:
        print(f"  No business")
    
    print(f"\nMental Health:")
    conditions = []
    if sim.has_anxiety:
        conditions.append("Anxiety")
    if sim.has_depression:
        conditions.append("Depression")
    if sim.ptsd:
        conditions.append("PTSD")
    print(f"  Conditions: {', '.join(conditions) if conditions else 'None'}")
    
    print(f"\nSkills:")
    print(f"  Cooking: {sim.cooking_skill:.0f} | Fitness: {sim.fitness_level:.0f}")
    print(f"  Creativity: {sim.creativity:.0f} | Leadership: {sim.leadership:.0f}")
    
    print(f"\nAchievements:")
    print(f"  Books read: {sim.books_read}")
    print(f"  Languages: {len(sim.languages_learned)} - {', '.join(sim.languages_learned[:3])}")
    print(f"  Countries visited: {len(sim.countries_visited)}")
    print(f"  Volunteer hours: {sim.volunteer_hours:.0f}")
    print(f"  Fame level: {sim.fame_level:.0f}")
    
    print(f"\nMajor Events:")
    if sim.lottery_wins:
        print(f"  Lottery wins: {len(sim.lottery_wins)} (total: ${sum(sim.lottery_wins):,.0f})")
    if sim.inheritances_received:
        print(f"  Inheritances: {len(sim.inheritances_received)} (total: ${sum(sim.inheritances_received):,.0f})")
    if sim.natural_disasters_survived:
        print(f"  Natural disasters: {', '.join(sim.natural_disasters_survived)}")
    if sim.major_accidents:
        print(f"  Major accidents: {len(sim.major_accidents)}")
    if sim.viral_moments:
        print(f"  Viral moments: {len(sim.viral_moments)}")
    
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


# ==================== REINFORCEMENT LEARNING ENVIRONMENT ====================

class LifeEnvironment:
    """RL Environment wrapper for training AI agents"""
    
    def __init__(self, seed=None):
        self.sim = None
        self.seed = seed
        self.action_space_size = 15  # Expanded action space
        self.state_size = 64  # Expanded state representation with new features
        
    def reset(self):
        """Reset environment and return initial state"""
        self.sim = EnhancedLifeSimulation(seed=self.seed, verbose=False)
        return self.get_state()
    
    def get_state(self):
        """Get current state as normalized numpy array"""
        if not self.sim.alive:
            return np.zeros(self.state_size)
        
        # Core vitals
        state = [
            self.sim.age / 100.0,
            self.sim.health / 100.0,
            self.sim.mental_health / 100.0,
            self.sim.happiness / 100.0,
            self.sim.energy / 100.0,
            self.sim.stress / 100.0,
            
            # Physical
            self.sim.weight / 200.0,
            self.sim.bmi() / 50.0,
            1.0 if self.sim.sick else 0.0,
            len(self.sim.chronic_conditions) / 5.0,
            
            # Financial
            np.tanh(self.sim.money / 50000.0),  # Soft cap
            np.tanh(self.sim.debt / 50000.0),
            np.tanh(self.sim.student_loan_debt / 100000.0),
            np.tanh(self.sim.investments / 50000.0),
            np.tanh(self.sim.has_retirement_savings / 100000.0),
            self.sim.credit_score / 850.0,
            1.0 if self.sim.owns_home else 0.0,
            
            # Career
            1.0 if self.sim.has_job else 0.0,
            self.sim.job_stability / 100.0,
            self.sim.job_satisfaction / 100.0,
            self.sim.skill_level / 10.0,
            self.sim.years_experience / 20.0,
            self.sim.reputation / 100.0,
            1.0 if hasattr(self.sim, 'in_school') and self.sim.in_school else 0.0,
            
            # Social
            self.sim.social_support / 100.0,
            len(self.sim.friends) / 15.0,
            len([f for f in self.sim.family_members if f.alive]) / max(1, len(self.sim.family_members)),
            1.0 if self.sim.relationship_status == 'married' else 0.5 if self.sim.relationship_status == 'dating' else 0.0,
            self.sim.relationship_satisfaction / 100.0 if self.sim.relationship_status != 'single' else 0.0,
            len(self.sim.children) / 5.0,
            
            # Substances
            self.sim.alcohol_dependency / 100.0,
            self.sim.drug_dependency / 100.0,
            1.0 if self.sim.smoking else 0.0,
            1.0 if self.sim.in_recovery else 0.0,
            
            # Legal
            len(self.sim.criminal_record) / 10.0,
            1.0 if self.sim.probation else 0.0,
            1.0 if self.sim.in_jail else 0.0,
            
            # Assets
            1.0 if self.sim.car_working else 0.0,
            1.0 if self.sim.license_suspended else 0.0,
            1.0 if self.sim.has_health_insurance else 0.0,
            1.0 if self.sim.therapy else 0.0,
            1.0 if self.sim.medication else 0.0,
            1.0 if self.sim.gym_membership else 0.0,
            
            # Life progress
            len(self.sim.completed_goals) / 10.0,
            len(self.sim.life_goals) / 10.0,
            len(self.sim.hobbies) / 5.0,
            len(self.sim.life_milestones) / 20.0,
            
            # New features
            len(self.sim.pets) / 3.0,
            1.0 if self.sim.owns_business else 0.0,
            self.sim.fame_level / 100.0,
            1.0 if self.sim.has_anxiety else 0.0,
            1.0 if self.sim.has_depression else 0.0,
            1.0 if self.sim.ptsd else 0.0,
            self.sim.cooking_skill / 100.0,
            self.sim.fitness_level / 100.0,
            self.sim.creativity / 100.0,
            self.sim.leadership / 100.0,
            len(self.sim.countries_visited) / 20.0,
            len(self.sim.languages_learned) / 5.0,
            self.sim.books_read / 200.0,
            self.sim.volunteer_hours / 500.0,
            
            # Time
            (self.sim.day % 365) / 365.0,  # Time of year
            self.sim.day / 7300.0,  # Total time (20 years max)
        ]
        
        return np.array(state, dtype=np.float32)
    
    def step(self, action):
        """
        Execute action and return (next_state, reward, done, info)
        
        Actions (15 total):
        0: Focus on physical health (exercise, diet)
        1: Focus on mental health (therapy, meditation, self-care)
        2: Work hard (career advancement, skill building)
        3: Job search / Career change
        4: Study / Pursue education
        5: Save money / Invest conservatively
        6: Aggressive investing / Risk-taking
        7: Socialize / Build relationships
        8: Focus on family (spouse, children)
        9: Pursue hobbies / Personal interests
        10: Seek treatment (addiction, health issues)
        11: Reduce stress / Take break
        12: Make major purchase / Lifestyle upgrade
        13: Volunteer / Help others
        14: Default / Minimal action (let life happen)
        """
        if not self.sim.alive:
            return self.get_state(), 0, True, {'reason': 'already_dead'}
        
        # Apply action effects BEFORE daily routine
        self._apply_action(action)
        
        # Run daily routine
        self.sim.daily_routine()
        
        # Get results
        next_state = self.get_state()
        reward = self.sim.daily_rewards[-1] if self.sim.daily_rewards else 0
        done = not self.sim.alive or self.sim.day >= 7300  # Max 20 years
        
        info = {
            'day': self.sim.day,
            'age': self.sim.age,
            'cause_of_end': self.sim.cause_of_end if done else None,
            'total_reward': self.sim.total_reward,
            'net_worth': self.sim.money + self.sim.investments - self.sim.debt,
            'happiness': self.sim.happiness,
            'action_taken': action
        }
        
        return next_state, reward, done, info
    
    def _apply_action(self, action):
        """Apply the chosen action's effects"""
        
        if action == 0:  # Physical health focus
            if self.sim.energy > 20:
                self.sim.health += random.uniform(1.5, 4.0)
                self.sim.weight -= random.uniform(0.4, 1.0)
                self.sim.energy -= 25
                self.sim.happiness += random.uniform(5, 12)
                self.sim.stress -= random.uniform(5, 10)
                self.sim.mental_health += random.uniform(1, 3)
                
        elif action == 1:  # Mental health focus
            self.sim.mental_health += random.uniform(3, 8)
            self.sim.happiness += random.uniform(4, 12)
            self.sim.stress -= random.uniform(8, 18)
            self.sim.energy += random.uniform(5, 15)
            self.sim.money -= random.uniform(20, 100)
            
            if self.sim.mental_health < 40 and not self.sim.therapy:
                if random.random() < 0.5:
                    self.sim.therapy = True
                    self.sim.log_event("Started therapy (action)")
                    
        elif action == 2:  # Work hard
            if self.sim.has_job:
                self.sim.job_stability += random.uniform(2, 5)
                self.sim.skill_level += random.uniform(0.02, 0.08)
                self.sim.energy -= 20
                self.sim.stress += random.uniform(3, 8)
                self.sim.job_satisfaction += random.uniform(0.5, 3)
                
                # Bonus income chance
                if random.random() < 0.1:
                    bonus = random.uniform(500, 3000)
                    self.sim.money += bonus
                    self.sim.happiness += 10
            else:
                self.sim.stress += 5
                
        elif action == 3:  # Job search / Career change
            if not self.sim.has_job:
                # Higher success rate when actively searching
                if random.random() < 0.15:
                    self.sim.has_job = True
                    self.sim.monthly_income = self.sim.calculate_income()
                    self.sim.job_stability = 75
                    self.sim.job_satisfaction = random.uniform(60, 85)
                    self.sim.log_event(f"Found job: {self.sim.job_title}")
                    self.sim.happiness += 35
            else:
                # Career change
                if random.random() < 0.05:
                    old_income = self.sim.monthly_income
                    self.sim.monthly_income = self.sim.calculate_income() * random.uniform(1.1, 1.4)
                    self.sim.career_field = random.choice(list(CareerField))
                    self.sim.log_event(f"Career change! Income: ${self.sim.monthly_income:.0f}")
                    
        elif action == 4:  # Study / Education
            if not hasattr(self.sim, 'in_school'):
                self.sim.in_school = False
                
            if not self.sim.in_school and self.sim.education_level != EducationLevel.PHD:
                if self.sim.money > 5000 or random.random() < 0.3:
                    # Start education
                    if self.sim.education_level == EducationLevel.HIGH_SCHOOL:
                        self.sim.target_degree = EducationLevel.BACHELORS
                    elif self.sim.education_level == EducationLevel.BACHELORS:
                        self.sim.target_degree = EducationLevel.MASTERS
                    elif self.sim.education_level == EducationLevel.MASTERS:
                        self.sim.target_degree = EducationLevel.PHD
                    else:
                        return
                        
                    self.sim.in_school = True
                    self.sim.school_progress = 0
                    loan = random.uniform(15000, 50000)
                    self.sim.student_loan_debt += loan
                    self.sim.log_event(f"Started {self.sim.target_degree.value} program")
            else:
                # Study harder
                self.sim.skill_level += random.uniform(0.05, 0.15)
                self.sim.energy -= 15
                self.sim.stress += random.uniform(2, 6)
                
        elif action == 5:  # Save/Invest conservatively
            if self.sim.money > 1000:
                save_amount = self.sim.money * random.uniform(0.1, 0.25)
                self.sim.money -= save_amount
                
                # Split between savings and investments
                self.sim.investments += save_amount * 0.7
                self.sim.has_retirement_savings += save_amount * 0.3
                
                self.sim.mental_health += 3
                self.sim.stress -= 5
                self.sim.investment_knowledge += 0.5
                
        elif action == 6:  # Aggressive investing
            if self.sim.money > 2000:
                invest_amount = self.sim.money * random.uniform(0.2, 0.5)
                self.sim.money -= invest_amount
                
                # Risky investment
                if random.random() < 0.6:  # Success
                    gain = invest_amount * random.uniform(1.1, 2.0)
                    self.sim.investments += gain
                    self.sim.happiness += 15
                    self.sim.log_event(f"Investment success: +${gain:.0f}")
                else:  # Loss
                    loss = invest_amount * random.uniform(0.3, 0.8)
                    self.sim.investments += loss
                    self.sim.stress += 15
                    self.sim.happiness -= 10
                    self.sim.log_event(f"Investment loss: -${invest_amount - loss:.0f}")
                    
                self.sim.investment_knowledge += 1.0
                
        elif action == 7:  # Socialize
            self.sim.social_support += random.uniform(5, 15)
            self.sim.happiness += random.uniform(8, 20)
            self.sim.mental_health += random.uniform(3, 10)
            self.sim.stress -= random.uniform(5, 12)
            self.sim.energy -= 15
            self.sim.money -= random.uniform(30, 150)
            self.sim.reputation += random.uniform(1, 5)
            
            # Chance to make new friend
            if random.random() < 0.2 and len(self.sim.ai_npcs) > 0:
                npc = random.choice(self.sim.ai_npcs)
                npc.relationship_type = 'friend'
                self.sim.friends.append(npc)
                self.sim.ai_npcs.remove(npc)
                self.sim.log_event(f"Made new friend: {npc.name}")
                
            # Improve existing relationships
            if len(self.sim.friends) > 0:
                for friend in random.sample(self.sim.friends, min(3, len(self.sim.friends))):
                    friend.relationship_quality += random.uniform(2, 8)
                    
        elif action == 8:  # Focus on family
            if self.sim.relationship_status in ['married', 'dating']:
                self.sim.relationship_satisfaction += random.uniform(3, 10)
                self.sim.happiness += random.uniform(5, 15)
                self.sim.social_support += random.uniform(3, 8)
                self.sim.money -= random.uniform(50, 200)
                
            for child in self.sim.children:
                if child.alive:
                    child.health += random.uniform(1, 3)
                    child.mental_health += random.uniform(2, 5)
                    
            self.sim.stress -= random.uniform(3, 10)
            
        elif action == 9:  # Hobbies
            if len(self.sim.hobbies) > 0:
                hobby_name = random.choice(list(self.sim.hobbies.keys()))
                hobby = self.sim.hobbies[hobby_name]
                
                if self.sim.money > hobby.cost and self.sim.energy > 15:
                    self.sim.money -= hobby.cost
                    self.sim.energy -= 20
                    self.sim.happiness += hobby.happiness_gain * 1.5
                    self.sim.stress -= random.uniform(10, 20)
                    self.sim.mental_health += random.uniform(3, 8)
                    hobby.skill_level += hobby.skill_gain * 2
                    
                    # Better chance of earning from hobby
                    if hobby.skill_level > 80:
                        if random.random() < 0.15:
                            earnings = random.uniform(500, 5000)
                            self.sim.money += earnings
                            self.sim.reputation += 5
            else:
                # Start a new hobby
                if self.sim.money > 100:
                    new_hobby_name = random.choice([h for h in HOBBIES.keys() if h not in self.sim.hobbies])
                    self.sim.hobbies[new_hobby_name] = HOBBIES[new_hobby_name]
                    self.sim.log_event(f"Started new hobby: {new_hobby_name}")
                    
        elif action == 10:  # Seek treatment
            if self.sim.alcohol_dependency > 10 or self.sim.drug_dependency > 10:
                if not self.sim.in_recovery:
                    self.sim.in_recovery = True
                    cost = random.uniform(5000, 15000)
                    self.sim.money -= cost
                    self.sim.log_event("Entered recovery program (action)")
                    self.sim.mental_health += 10
                    self.sim.happiness += 5
                else:
                    # Continue recovery
                    self.sim.alcohol_dependency = max(0, self.sim.alcohol_dependency - 2.0)
                    self.sim.drug_dependency = max(0, self.sim.drug_dependency - 2.0)
                    self.sim.mental_health += 2
                    
            if len(self.sim.chronic_conditions) > 0 and not self.sim.medication:
                self.sim.medication = True
                self.sim.medication_cost_monthly = random.uniform(150, 600)
                self.sim.log_event("Started medication (action)")
                
            if self.sim.mental_health < 50 and not self.sim.therapy:
                self.sim.therapy = True
                self.sim.log_event("Started therapy (action)")
                
        elif action == 11:  # Reduce stress / Take break
            self.sim.stress -= random.uniform(15, 30)
            self.sim.energy += random.uniform(20, 40)
            self.sim.mental_health += random.uniform(5, 12)
            self.sim.happiness += random.uniform(8, 18)
            self.sim.money -= random.uniform(100, 500)
            
            if self.sim.has_job:
                self.sim.job_satisfaction += random.uniform(2, 6)
                
        elif action == 12:  # Major purchase
            if self.sim.money > 15000 and not self.sim.owns_home:
                # Try to buy house
                if self.sim.credit_score > 650 and random.random() < 0.3:
                    down_payment = random.uniform(25000, 60000)
                    if self.sim.money > down_payment:
                        self.sim.home_value = down_payment * random.uniform(4, 7)
                        self.sim.money -= down_payment
                        self.sim.owns_home = True
                        self.sim.mortgage_payment = self.sim.home_value * 0.004
                        self.sim.rent = 0
                        self.sim.happiness += 50
                        self.sim.log_event(f"Bought house! (action)")
                        
            elif self.sim.money > 5000 and random.random() < 0.5:
                # Other purchases
                purchase_cost = random.uniform(2000, 8000)
                self.sim.money -= purchase_cost
                self.sim.happiness += random.uniform(15, 30)
                self.sim.log_event(f"Major purchase: ${purchase_cost:.0f}")
                
        elif action == 13:  # Volunteer / Help others
            self.sim.reputation += random.uniform(5, 15)
            self.sim.happiness += random.uniform(10, 25)
            self.sim.mental_health += random.uniform(5, 12)
            self.sim.social_support += random.uniform(5, 12)
            self.sim.energy -= 20
            self.sim.money -= random.uniform(50, 200)
            
            # Chance to help family
            if len(self.sim.family_members) > 0:
                family_member = random.choice([f for f in self.sim.family_members if f.alive])
                family_member.health += random.uniform(2, 8)
                family_member.relationship_quality += random.uniform(5, 15)
                
        # Action 14 is "do nothing" - no effects
        
        # Clamp values after action
        self.sim.health = max(0, min(100, self.sim.health))
        self.sim.mental_health = max(0, min(100, self.sim.mental_health))
        self.sim.happiness = max(0, min(100, self.sim.happiness))
        self.sim.stress = max(0, min(100, self.sim.stress))
        self.sim.energy = max(0, min(100, self.sim.energy))


# ==================== DQN AGENT ====================

class DQNAgent:
    """Deep Q-Network with experience replay and target network"""
    
    def __init__(self, state_size=64, action_size=15, learning_rate=0.0005):
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow required for training")
        
        self.state_size = state_size
        self.action_size = action_size
        self.memory = []
        self.memory_size = 50000
        self.gamma = 0.97  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9975
        self.learning_rate = learning_rate
        self.batch_size = 128
        self.update_target_every = 5
        
        # Build networks
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()
        
        # Training stats
        self.training_step = 0
        
    def _build_model(self):
        """Build deep neural network"""
        model = models.Sequential([
            layers.Input(shape=(self.state_size,)),
            layers.Dense(256, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(256, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001)),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(128, activation='relu'),
            layers.Dense(self.action_size, activation='linear')
        ])
        
        model.compile(
            optimizer=optimizers.Adam(learning_rate=self.learning_rate),
            loss='huber'  # More stable than MSE
        )
        return model
    
    def update_target_model(self):
        """Copy weights to target network"""
        self.target_model.set_weights(self.model.get_weights())
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.append((state, action, reward, next_state, done))
        if len(self.memory) > self.memory_size:
            self.memory.pop(0)
    
    def act(self, state, training=True):
        """Epsilon-greedy action selection"""
        if training and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        
        state = np.reshape(state, [1, self.state_size])
        q_values = self.model.predict(state, verbose=0)
        return np.argmax(q_values[0])
    
    def replay(self):
        """Train on batch from memory"""
        if len(self.memory) < self.batch_size:
            return 0, 0
        
        # Sample batch
        batch = random.sample(self.memory, self.batch_size)
        
        states = np.array([exp[0] for exp in batch])
        actions = np.array([exp[1] for exp in batch])
        rewards = np.array([exp[2] for exp in batch])
        next_states = np.array([exp[3] for exp in batch])
        dones = np.array([exp[4] for exp in batch])
        
        # Double DQN: select action with main network, evaluate with target
        current_q = self.model.predict(states, verbose=0)
        next_q_main = self.model.predict(next_states, verbose=0)
        next_q_target = self.target_model.predict(next_states, verbose=0)
        
        # Calculate targets
        targets = current_q.copy()
        for i in range(self.batch_size):
            if dones[i]:
                targets[i][actions[i]] = rewards[i]
            else:
                # Double DQN update
                best_action = np.argmax(next_q_main[i])
                targets[i][actions[i]] = rewards[i] + self.gamma * next_q_target[i][best_action]
        
        # Train
        history = self.model.fit(states, targets, epochs=1, verbose=0, batch_size=self.batch_size)
        loss = history.history['loss'][0]
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        self.training_step += 1
        
        # Update target network periodically
        if self.training_step % self.update_target_every == 0:
            self.update_target_model()
        
        # Calculate average Q-value for monitoring
        avg_q = np.mean(current_q)
        
        return loss, avg_q
    
    def save(self, filepath):
        """Save model weights"""
        self.model.save_weights(filepath)
        print(f"Model saved to {filepath}")
    
    def load(self, filepath):
        """Load model weights"""
        self.model.load_weights(filepath)
        self.update_target_model()
        print(f"Model loaded from {filepath}")


# ==================== TRAINING FUNCTION ====================

def train_agent(episodes=200, max_days=3650, save_path='life_agent_v2.weights.h5', 
                render_every=10, save_every=25):
    """
    Train DQN agent to make optimal life decisions
    
    Args:
        episodes: Number of training episodes
        max_days: Max days per episode (10 years default)
        save_path: Where to save model weights
        render_every: Print progress every N episodes
        save_every: Save model every N episodes
    """
    if not TF_AVAILABLE:
        print("TensorFlow not available. Cannot train agent.")
        return None
    
    env = LifeEnvironment()
    agent = DQNAgent(state_size=64, action_size=15)
    
    # Tracking
    rewards_history = []
    days_survived_history = []
    losses = []
    avg_q_values = []
    net_worth_history = []
    happiness_history = []
    
    print(f"\n{'='*80}")
    print(f"TRAINING DQN AGENT - {episodes} EPISODES")
    print(f"State Size: {agent.state_size} | Action Size: {agent.action_size}")
    print(f"{'='*80}\n")
    
    best_reward = -float('inf')
    best_episode = 0
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        episode_losses = []
        episode_q_values = []
        day = 0
        
        for day in range(max_days):
            # Choose action
            action = agent.act(state, training=True)
            
            # Take step
            next_state, reward, done, info = env.step(action)
            
            # Store experience
            agent.remember(state, action, reward, next_state, done)
            
            # Train
            if len(agent.memory) >= agent.batch_size:
                loss, avg_q = agent.replay()
                episode_losses.append(loss)
                episode_q_values.append(avg_q)
            
            state = next_state
            total_reward += reward
            
            if done:
                break
        
        # Track metrics
        rewards_history.append(total_reward)
        days_survived_history.append(day)
        if episode_losses:
            losses.extend(episode_losses)
            avg_q_values.extend(episode_q_values)
        
        net_worth_history.append(info.get('net_worth', 0))
        happiness_history.append(info.get('happiness', 0))
        
        # Track best performance
        if total_reward > best_reward:
            best_reward = total_reward
            best_episode = episode
        
        # Print progress
        if episode % render_every == 0 or episode == episodes - 1:
            avg_reward = np.mean(rewards_history[-render_every:])
            avg_days = np.mean(days_survived_history[-render_every:])
            avg_loss = np.mean(episode_losses) if episode_losses else 0
            avg_q = np.mean(episode_q_values) if episode_q_values else 0
            avg_net_worth = np.mean(net_worth_history[-render_every:])
            
            print(f"Ep {episode:4d}/{episodes} | "
                  f"Days: {day:4d} | "
                  f"Reward: {total_reward:7.1f} | "
                  f"Avg-{render_every}: {avg_reward:7.1f} | "
                  f"NetWorth: ${avg_net_worth:8.0f} | "
                  f"Loss: {avg_loss:.4f} | "
                  f"Q: {avg_q:6.2f} | "
                  f"ε: {agent.epsilon:.3f}")
        
        # Save model periodically
        if episode > 0 and episode % save_every == 0:
            agent.save(save_path)
    
    # Final save
    agent.save(save_path)
    
    print(f"\n{'='*80}")
    print(f"TRAINING COMPLETE")
    print(f"Best Episode: {best_episode} with reward: {best_reward:.1f}")
    print(f"Final Epsilon: {agent.epsilon:.3f}")
    print(f"{'='*80}\n")
    
    # Plot training results
    plot_training_results(rewards_history, days_survived_history, losses, 
                          avg_q_values, net_worth_history, happiness_history)
    
    return agent


def plot_training_results(rewards, days, losses, q_values, net_worths, happiness):
    """Plot comprehensive training metrics"""
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    fig.suptitle('DQN Training Results', fontsize=16, fontweight='bold')
    
    # Rewards
    axes[0,0].plot(rewards, alpha=0.6, label='Episode Reward')
    if len(rewards) >= 10:
        window = min(20, len(rewards))
        ma = [np.mean(rewards[max(0, i-window):i+1]) for i in range(len(rewards))]
        axes[0,0].plot(ma, linewidth=2, label=f'MA-{window}')
    axes[0,0].set_title('Total Reward per Episode')
    axes[0,0].set_xlabel('Episode')
    axes[0,0].set_ylabel('Total Reward')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    # Days survived
    axes[0,1].plot(days, alpha=0.6, color='green', label='Days Survived')
    if len(days) >= 10:
        window = min(20, len(days))
        ma = [np.mean(days[max(0, i-window):i+1]) for i in range(len(days))]
        axes[0,1].plot(ma, linewidth=2, color='darkgreen', label=f'MA-{window}')
    axes[0,1].set_title('Days Survived per Episode')
    axes[0,1].set_xlabel('Episode')
    axes[0,1].set_ylabel('Days')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    # Training loss
    if losses:
        axes[1,0].plot(losses, alpha=0.4)
        if len(losses) >= 100:
            window = 100
            ma = [np.mean(losses[max(0, i-window):i+1]) for i in range(len(losses))]
            axes[1,0].plot(ma, linewidth=2, color='red')
        axes[1,0].set_title('Training Loss (Huber)')
        axes[1,0].set_xlabel('Training Step')
        axes[1,0].set_ylabel('Loss')
        axes[1,0].set_yscale('log')
        axes[1,0].grid(True, alpha=0.3)
    
    # Average Q-values
    if q_values:
        axes[1,1].plot(q_values, alpha=0.4)
        if len(q_values) >= 100:
            window = 100
            ma = [np.mean(q_values[max(0, i-window):i+1]) for i in range(len(q_values))]
            axes[1,1].plot(ma, linewidth=2, color='blue')
        axes[1,1].set_title('Average Q-Value')
        axes[1,1].set_xlabel('Training Step')
        axes[1,1].set_ylabel('Q-Value')
        axes[1,1].grid(True, alpha=0.3)
    
    # Net worth over episodes
    axes[2,0].plot(net_worths, alpha=0.6, color='purple', label='Final Net Worth')
    if len(net_worths) >= 10:
        window = min(20, len(net_worths))
        ma = [np.mean(net_worths[max(0, i-window):i+1]) for i in range(len(net_worths))]
        axes[2,0].plot(ma, linewidth=2, color='darkviolet', label=f'MA-{window}')
    axes[2,0].set_title('Net Worth at Episode End')
    axes[2,0].set_xlabel('Episode')
    axes[2,0].set_ylabel('Net Worth ($)')
    axes[2,0].legend()
    axes[2,0].grid(True, alpha=0.3)
    
    # Happiness over episodes
    axes[2,1].plot(happiness, alpha=0.6, color='orange', label='Final Happiness')
    if len(happiness) >= 10:
        window = min(20, len(happiness))
        ma = [np.mean(happiness[max(0, i-window):i+1]) for i in range(len(happiness))]
        axes[2,1].plot(ma, linewidth=2, color='darkorange', label=f'MA-{window}')
    axes[2,1].set_title('Happiness at Episode End')
    axes[2,1].set_xlabel('Episode')
    axes[2,1].set_ylabel('Happiness')
    axes[2,1].legend()
    axes[2,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/claude/training_results.png', dpi=150, bbox_inches='tight')
    plt.show()


def evaluate_agent(agent, episodes=10, render=True, max_days=3650):
    """Evaluate trained agent performance"""
    env = LifeEnvironment()
    
    results = []
    
    print(f"\n{'='*80}")
    print(f"EVALUATING TRAINED AGENT - {episodes} EPISODES")
    print(f"{'='*80}\n")
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        
        # Greedy policy (no exploration)
        old_epsilon = agent.epsilon
        agent.epsilon = 0
        
        action_counts = defaultdict(int)
        
        for day in range(max_days):
            action = agent.act(state, training=False)
            action_counts[action] += 1
            
            next_state, reward, done, info = env.step(action)
            state = next_state
            total_reward += reward
            
            if done:
                break
        
        agent.epsilon = old_epsilon
        
        result = {
            'episode': episode + 1,
            'days': day,
            'reward': total_reward,
            'net_worth': info['net_worth'],
            'happiness': info['happiness'],
            'alive': env.sim.alive,
            'cause': info['cause_of_end'],
            'action_distribution': dict(action_counts)
        }
        results.append(result)
        
        if render:
            print(f"Episode {episode+1:2d}: Days={day:4d} | "
                  f"Reward={total_reward:7.1f} | "
                  f"NetWorth=${info['net_worth']:8.0f} | "
                  f"Happy={info['happiness']:5.1f} | "
                  f"Status={'Alive' if env.sim.alive else info['cause_of_end']}")
    
    # Summary statistics
    print(f"\n{'='*80}")
    print(f"EVALUATION SUMMARY")
    print(f"{'='*80}")
    print(f"Avg Reward: {np.mean([r['reward'] for r in results]):7.1f} "
          f"± {np.std([r['reward'] for r in results]):6.1f}")
    print(f"Avg Days: {np.mean([r['days'] for r in results]):6.1f} "
          f"± {np.std([r['days'] for r in results]):5.1f}")
    print(f"Avg Net Worth: ${np.mean([r['net_worth'] for r in results]):8.0f} "
          f"± ${np.std([r['net_worth'] for r in results]):7.0f}")
    print(f"Avg Happiness: {np.mean([r['happiness'] for r in results]):5.1f} "
          f"± {np.std([r['happiness'] for r in results]):4.1f}")
    print(f"Survival Rate: {sum(1 for r in results if r['alive']) / len(results) * 100:.1f}%")
    
    # Action distribution
    all_actions = defaultdict(int)
    for r in results:
        for action, count in r['action_distribution'].items():
            all_actions[action] += count
    
    print(f"\nAction Distribution:")
    action_names = [
        "Physical Health", "Mental Health", "Work Hard", "Job Search",
        "Study", "Save/Invest", "Risky Invest", "Socialize",
        "Family", "Hobbies", "Treatment", "Reduce Stress",
        "Major Purchase", "Volunteer", "Default"
    ]
    total_actions = sum(all_actions.values())
    for action in range(15):
        pct = all_actions[action] / total_actions * 100 if total_actions > 0 else 0
        print(f"  {action:2d}. {action_names[action]:15s}: {pct:5.1f}%")
    
    print(f"{'='*80}\n")
    
    return results


def compare_trained_vs_random(trained_agent, episodes=20):
    """Compare trained agent vs random baseline"""
    print(f"\n{'='*80}")
    print(f"COMPARISON: TRAINED AGENT VS RANDOM BASELINE")
    print(f"{'='*80}\n")
    
    # Test trained agent
    print("Testing TRAINED agent...")
    trained_results = evaluate_agent(trained_agent, episodes=episodes, render=False)
    
    # Create random agent
    class RandomAgent:
        def __init__(self, action_size=15):
            self.action_size = action_size
            self.epsilon = 0
        def act(self, state, training=False):
            return random.randrange(self.action_size)
    
    print("\nTesting RANDOM baseline...")
    random_results = evaluate_agent(RandomAgent(), episodes=episodes, render=False)
    
    # Compare
    print(f"\n{'='*80}")
    print(f"COMPARISON RESULTS")
    print(f"{'='*80}")
    print(f"{'Metric':<20} {'Trained':<15} {'Random':<15} {'Improvement':<15}")
    print(f"{'-'*80}")
    
    metrics = [
        ('Avg Reward', 'reward'),
        ('Avg Days', 'days'),
        ('Avg Net Worth', 'net_worth'),
        ('Avg Happiness', 'happiness'),
    ]
    
    for name, key in metrics:
        trained_avg = np.mean([r[key] for r in trained_results])
        random_avg = np.mean([r[key] for r in random_results])
        improvement = (trained_avg - random_avg) / abs(random_avg) * 100 if random_avg != 0 else 0
        
        if key == 'net_worth':
            print(f"{name:<20} ${trained_avg:<14.0f} ${random_avg:<14.0f} {improvement:+.1f}%")
        else:
            print(f"{name:<20} {trained_avg:<15.1f} {random_avg:<15.1f} {improvement:+.1f}%")
    
    trained_survival = sum(1 for r in trained_results if r['alive']) / len(trained_results) * 100
    random_survival = sum(1 for r in random_results if r['alive']) / len(random_results) * 100
    
    print(f"{'Survival Rate':<20} {trained_survival:<15.1f}% {random_survival:<15.1f}% "
          f"{trained_survival - random_survival:+.1f}pp")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*80)
    print("ENHANCED LIFE SIMULATION WITH DEEP REINFORCEMENT LEARNING")
    print("="*80)
    
    # Show TensorFlow status
    if TF_AVAILABLE:
        print("✓ TensorFlow Status: AVAILABLE (All features enabled)")
    else:
        print("⚠ TensorFlow Status: NOT AVAILABLE")
        print("  RL training features are disabled, but simulations work perfectly!")
        print("\n  To enable TensorFlow on macOS (especially M1/M2/M3 Macs):")
        print("  1. Install via conda: conda install tensorflow")
        print("  2. Or use tensorflow-macos: pip install tensorflow-macos tensorflow-metal")
        print("  3. Or continue without training - single simulations work great!")
        if TF_ERROR_MESSAGE:
            print(f"\n  Error details: {TF_ERROR_MESSAGE}")
    
    print("\n" + "="*80)
    print("\nOptions:")
    print("1. Run single simulation (no training) ✓ Always available")
    
    if TF_AVAILABLE:
        print("2. Train RL agent ✓ TensorFlow available")
        print("3. Evaluate trained agent ✓ TensorFlow available")
        print("4. Compare trained vs random ✓ TensorFlow available")
    else:
        print("2. Train RL agent ✗ Requires TensorFlow")
        print("3. Evaluate trained agent ✗ Requires TensorFlow")
        print("4. Compare trained vs random ✗ Requires TensorFlow")
    
    print("="*80)
    
    choice = input("\nEnter choice (1-4, default=1): ").strip() or "1"
    
    if choice == "1":
        print("\nRunning single simulation...")
        sim, df = run_simulation(days=3650, seed=None, verbose=False)
        
    elif choice == "2":
        if not TF_AVAILABLE:
            print("\n❌ ERROR: TensorFlow is required for training.")
            print("Please install TensorFlow and try again.")
            print("\nFor macOS with Apple Silicon (M1/M2/M3):")
            print("  conda install -c apple tensorflow-deps")
            print("  pip install tensorflow-macos tensorflow-metal")
            print("\nFor other systems:")
            print("  pip install tensorflow")
            sys.exit(1)
        
        episodes = int(input("Enter number of episodes (default=200): ").strip() or "200")
        print(f"\nTraining agent for {episodes} episodes...")
        agent = train_agent(episodes=episodes, max_days=3650, save_path='life_agent_v2.weights.h5')
        
        # Evaluate after training
        if input("\nEvaluate trained agent? (y/n, default=y): ").strip().lower() != 'n':
            evaluate_agent(agent, episodes=10, render=True)
            
    elif choice == "3":
        if not TF_AVAILABLE:
            print("\n❌ ERROR: TensorFlow is required for evaluation.")
            print("Please install TensorFlow and try again.")
            sys.exit(1)
            
        model_path = input("Enter model path (default=life_agent_v2.weights.h5): ").strip() or "life_agent_v2.weights.h5"
        try:
            agent = DQNAgent(state_size=64, action_size=15)
            agent.load(model_path)
            evaluate_agent(agent, episodes=10, render=True)
        except Exception as e:
            print(f"Error loading model: {e}")
            
    elif choice == "4":
        if not TF_AVAILABLE:
            print("\n❌ ERROR: TensorFlow is required for comparison.")
            print("Please install TensorFlow and try again.")
            sys.exit(1)
            
        model_path = input("Enter model path (default=life_agent_v2.weights.h5): ").strip() or "life_agent_v2.weights.h5"
        try:
            agent = DQNAgent(state_size=64, action_size=15)
            agent.load(model_path)
            compare_trained_vs_random(agent, episodes=20)
        except Exception as e:
            print(f"Error loading model: {e}")
    else:
        print(f"Invalid choice: {choice}")
        sys.exit(1)