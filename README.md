# Enhanced Life Simulation with Deep Reinforcement Learning

A comprehensive life simulation with **3,300+ lines of code** featuring AI-controlled NPCs, deep reinforcement learning training capabilities, and an incredibly detailed life progression system.

## 🌟 Major Features Added

### **1. Deep Reinforcement Learning System**
- **Fully trainable DQN agent** with 64-state representation and 15 discrete actions
- **Double DQN** with target network and experience replay
- **Proper training infrastructure**:
  - Batch normalization and dropout for stable learning
  - Huber loss for robust training
  - Epsilon-greedy exploration with decay
  - Target network updates every 5 steps
  - 50,000 experience replay buffer
- **Comprehensive evaluation**:
  - Compare trained agent vs random baseline
  - Track improvements in reward, survival, net worth, happiness
  - Action distribution analysis
  - Training curves for loss, Q-values, rewards

### **2. AI-Controlled NPCs**
- **10-25 NPCs** exist in the world simultaneously
- Each NPC has their own:
  - Personality type (Aggressive, Cautious, Social, Ambitious, Hedonistic, Balanced)
  - Money, job, education, hobbies, goals, memories
  - Ambition, risk tolerance, sociability, empathy stats
- **NPC Behaviors**:
  - NPCs make autonomous decisions based on personality
  - NPCs age realistically and can die
  - NPC-to-player interactions (chat, help requests, conflicts, business deals, romance)
  - NPC-to-NPC interactions (they interact with each other!)
  - NPCs can become friends or romantic partners

### **3. Enhanced Death System**
- **Age-based mortality rates**:
  - Infant mortality for babies
  - Accidents for youth
  - Diseases for middle age
  - Old age for elderly (70+)
- **Realistic death causes**: natural causes, accidents, illness, heart disease, cancer, suicide, overdose
- **Family members age and die** based on their age and health
- Surviving family members affects mental health

### **4. Pet Ownership**
- 5 pet types: dogs, cats, birds, fish, hamsters
- Pets age and can die (lifespan varies by type)
- **Pet benefits**: happiness boost, mental health improvement, stress reduction
- **Pet costs**: daily care, vet visits
- Emotional impact when pets die

### **5. Business Ownership**
- **Start your own business** (restaurant, retail, tech startup, consulting, trade service)
- Monthly profit/loss calculations based on:
  - Owner skill level
  - Time invested
  - Market conditions
  - Random events (good and bad)
- Business value appreciation/depreciation
- Business can fail if success drops too low

### **6. Natural Disasters**
- Random natural disasters: hurricanes, tornadoes, earthquakes, floods, wildfires
- **Impacts**:
  - Physical injuries
  - Property damage (home and car)
  - PTSD development
  - Insurance payouts
  - Mental health trauma

### **7. Accidents & Injuries**
- Random accidents: car crashes, falls, sports injuries, work accidents, home accidents
- **Severity levels**:
  - Minor: small health loss, medical costs
  - Moderate: significant health loss, hospital stay
  - Severe: major health impact, long recovery, possible permanent disability
- Permanent disabilities affect career income

### **8. Lottery & Gambling**
- Small chance to buy lottery tickets
- **Win tiers**:
  - Jackpot: $1M-$100M (life-changing)
  - Big win: $10K-$500K
  - Small win: $100-$5K
- Lottery wins increase fame and become viral moments

### **9. Random Inheritances**
- Receive unexpected inheritances from distant relatives
- Range: $5,000 to $500,000
- Tracked separately from family member deaths

### **10. Mental Health Conditions**
- **Specific conditions**: Anxiety, Depression, PTSD
- Each has unique effects:
  - **Anxiety**: increased stress, reduced mental health
  - **Depression**: reduced happiness and energy
  - **PTSD**: random episodes, flashbacks
- Can develop conditions based on life circumstances
- Requires medication and therapy for management

### **11. Skill Development System**
- **4 skill categories**:
  - **Cooking**: Can earn side income from catering
  - **Fitness**: Improved health
  - **Creativity**: Boosted by hobbies and reading
  - **Leadership**: Improves through job satisfaction
- Skills range from 0-100
- Skills unlock opportunities

### **12. Fame & Social Media**
- **Viral moments**: videos, tweets, photos, blog posts
- Fame level (0-100) with effects:
  - High fame = stress + happiness
  - Monetary gains from fame
  - Loss of privacy
  - Fame decays over time

### **13. Education & Personal Growth**
- **Reading**: Track books read, gain mental health and creativity
- **Language learning**: Learn up to 5 languages
- **Travel**: Visit countries worldwide
- Achievements at milestones (50 books, 10 countries, etc.)

### **14. Political Engagement**
- Elections every 2 years (simplified)
- Voting affects happiness and stress
- Track total votes cast
- Political affiliation system

### **15. Volunteering**
- Volunteer work increases:
  - Happiness
  - Mental health
  - Reputation
  - Social support
- Track total volunteer hours
- Milestones at 100, 200, 300+ hours

### **16. Enhanced Career System**
- **8 career fields** with field-specific income multipliers
- **5 education levels** affecting starting salary
- Promotions based on job satisfaction and performance
- Career achievements tracking
- Job satisfaction affects mental health
- Can go back to school while working

### **17. Education System**
- Enroll in degree programs (Associates, Bachelors, Masters, PhD)
- School progress tracked monthly
- Student loans accumulate
- Graduation boosts skill level and income potential
- Time and money investment required

### **18. Life Goals System**
- 10 possible goals: buy house, get married, have children, promotion, education, savings, travel, business, writing, fitness
- Goals can be completed for major happiness boosts
- Track completed vs remaining goals
- Goals based on personality

### **19. Hobby System**
- **12 hobbies** across 4 categories:
  - Physical: Sports, Yoga
  - Creative: Music, Art, Photography, Writing
  - Intellectual: Reading, Chess, Coding
  - Practical: Cooking, Gardening
- Each hobby has:
  - Cost per session
  - Skill gain rate
  - Happiness bonus
- Master level (80+ skill) can earn money
- Hobbies reduce stress significantly

### **20. Home Ownership**
- Purchase homes with down payments
- Monthly mortgage payments
- Home value tracking
- Home damaged in disasters
- Major life milestone

### **21. Investment System**
- Daily market fluctuations
- Investment knowledge improves returns
- Conservative vs aggressive investing strategies
- Track investment portfolio value
- Retirement savings (401k) separate from investments

### **22. Credit Score System**
- Ranges from 300-850
- Affected by:
  - Debt payments
  - On-time payments
  - Criminal record
- Required for home loans
- Improves over time with good behavior

### **23. Enhanced Relationship System**
- Dating pool of potential partners
- Relationship satisfaction affects happiness
- Marriage and divorce mechanics
- Wedding costs
- Divorce costs and child support
- Spouse as AI-controlled NPC with personality

---

## 🎮 15 Reinforcement Learning Actions

The AI can choose from 15 distinct actions each day:

0. **Physical Health** - Exercise, healthy eating
1. **Mental Health** - Therapy, meditation, self-care
2. **Work Hard** - Career advancement, skill building
3. **Job Search** - Find new job or change careers
4. **Study** - Pursue education, enroll in programs
5. **Save/Invest** - Conservative financial planning
6. **Risky Invest** - Aggressive investing for higher returns
7. **Socialize** - Build friendships, networking
8. **Focus on Family** - Spend time with spouse/children
9. **Pursue Hobbies** - Develop skills, earn side income
10. **Seek Treatment** - Addiction recovery, medical care
11. **Reduce Stress** - Take breaks, vacations
12. **Major Purchase** - Buy house, car, or luxury items
13. **Volunteer** - Help others, build reputation
14. **Default** - Let life happen naturally

---

## 📊 64-Dimensional State Space

The RL agent observes 64 features including:

**Core Vitals** (6): age, health, mental health, happiness, energy, stress

**Physical** (4): weight, BMI, sick status, chronic conditions

**Financial** (7): money, debt, student loans, investments, retirement, credit score, home ownership

**Career** (7): employment, job stability, satisfaction, skill level, experience, reputation, education status

**Social** (6): social support, friends, family alive, relationship status, satisfaction, children

**Substances** (4): alcohol, drugs, smoking, recovery status

**Legal** (3): criminal record, probation, jail

**Assets** (6): car, license, health insurance, therapy, medication, gym

**Progress** (4): completed goals, remaining goals, hobbies, milestones

**New Features** (14): pets, business, fame, anxiety, depression, PTSD, cooking, fitness, creativity, leadership, countries, languages, books, volunteer hours

**Time** (2): season, total days

---

## 🚀 Usage

### Option 1: Run Single Simulation
```python
python main.py
# Choose option 1
# Simulates 10 years of life with visualizations
```

### Option 2: Train RL Agent
```python
python main.py
# Choose option 2
# Enter number of episodes (recommended: 200-500)
# Agent learns optimal life decisions through trial and error
# Model saved as life_agent_v2.weights.h5
```

### Option 3: Evaluate Trained Agent
```python
python main.py
# Choose option 3
# Load trained model
# Run 10 test episodes to see performance
# Shows action distribution and success metrics
```

### Option 4: Compare Trained vs Random
```python
python main.py
# Choose option 4
# Loads trained agent
# Compares against random baseline
# Shows improvement percentages
```

---

## 📈 Training Performance

Expected improvements from trained agent:

- **Survival Rate**: +15-30% over random
- **Average Days Survived**: +500-1500 days
- **Net Worth**: +50-200% higher
- **Happiness**: +20-40% higher
- **Total Reward**: +100-300% improvement

The agent learns to:
- Prioritize mental and physical health
- Balance work and personal life
- Avoid risky behaviors (substances, crime)
- Build financial stability
- Maintain relationships
- Pursue education strategically
- Seek help when needed

---

## 🎯 What Makes This Better for RL Training

1. **Proper State Representation**: 64 normalized features capture all aspects of life
2. **Meaningful Actions**: 15 distinct actions with clear effects
3. **Balanced Reward Function**: Weights multiple objectives (health, happiness, money, relationships)
4. **Long-term Planning**: Episodes last 3,650-7,300 days (10-20 years)
5. **Stochastic Environment**: Randomness ensures agent can't memorize
6. **Complex Dynamics**: Actions have both immediate and delayed consequences
7. **Multiple Objectives**: Must balance competing goals
8. **Death Conditions**: Natural endpoints based on health/age
9. **Variance**: Each episode is unique due to random events
10. **Measurable Progress**: Clear metrics for improvement

---

## 📋 Dependencies

```bash
pip install numpy pandas matplotlib tensorflow --break-system-packages
```

- **numpy**: Numerical computations
- **pandas**: Data logging
- **matplotlib**: Visualizations
- **tensorflow**: Deep learning (DQN)

---

## 🎨 Visualizations

The simulation generates comprehensive plots:

**Row 1**: Health metrics, Happiness vs Stress, Weight & BMI
**Row 2**: Financial overview, Career & Reputation, Substance dependency
**Row 3**: Relationships, Criminal record, AI NPCs
**Row 4**: Daily rewards, Cumulative reward, Energy levels
**Row 5**: Event log, Milestones, Summary statistics

Training generates additional plots:
- Episode rewards with moving average
- Days survived progression
- Training loss over time
- Average Q-values
- Net worth progression
- Happiness progression

---

## 💡 Tips for Best Results

1. **Training**: Use 200-500 episodes for good performance
2. **Evaluation**: Test on at least 20 episodes for reliable statistics
3. **Comparison**: Random baseline helps verify learning
4. **Exploration**: Higher epsilon early helps discover good strategies
5. **Patience**: Training takes 30-90 minutes depending on hardware

---

## 🏆 Advanced Features

- **Double DQN**: Reduces overestimation bias
- **Experience Replay**: Breaks correlation in training data
- **Target Network**: Stabilizes training
- **Batch Normalization**: Normalizes layer inputs
- **Dropout**: Prevents overfitting
- **Huber Loss**: Robust to outliers
- **Epsilon Decay**: Balances exploration/exploitation
- **Soft Caps**: Prevents extreme values in state space

---

## 📝 Summary

This is a **production-ready life simulation** with:
- ✅ **Trainable RL agent** that learns optimal decisions
- ✅ **64-dimensional state space** capturing all life aspects
- ✅ **15 meaningful actions** the agent can take
- ✅ **AI NPCs** with personalities that age and die
- ✅ **50+ life events** (disasters, accidents, lottery, inheritance, etc.)
- ✅ **Comprehensive tracking** of achievements and milestones
- ✅ **Professional visualizations** of life progression
- ✅ **Realistic death mechanics** based on age and health
- ✅ **Complex social dynamics** with family, friends, and strangers
- ✅ **Economic simulation** with investments, business, debt
- ✅ **Mental health modeling** with specific conditions
- ✅ **Pet ownership** with emotional bonds
- ✅ **Fame mechanics** from viral moments

**Total**: 3,307 lines of carefully crafted Python code simulating a rich, complex, trainable life!