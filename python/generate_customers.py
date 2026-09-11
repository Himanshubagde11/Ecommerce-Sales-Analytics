"""
Vectorized generation of 100,000+ realistic customer records for Veyra E-Commerce.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from config import (
    RAW_DATA_DIR,
    NUM_CUSTOMERS,
    RANDOM_SEED,
    ACQUISITION_CHANNELS,
    ACQUISITION_WEIGHTS,
    setup_logger
)

logger = setup_logger("generate_customers")

def generate_customers(num_customers: int = NUM_CUSTOMERS) -> pd.DataFrame:
    """Generates customer profiles with realistic demographics, locations, and signup dates."""
    logger.info(f"Generating {num_customers:,} customer records...")
    rng = np.random.default_rng(RANDOM_SEED)

    # Name Pools
    first_names_m = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
        "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth",
        "Kevin", "Brian", "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan", "Jacob",
        "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin",
        "Samuel", "Gregory", "Alexander", "Patrick", "Frank", "Raymond", "Jack", "Dennis", "Jerry", "Tyler",
        "Aaron", "Jose", "Adam", "Nathan", "Henry", "Douglas", "Zachary", "Peter", "Kyle", "Walter",
        "Ethan", "Jeremy", "Harold", "Keith", "Christian", "Roger", "Noah", "Gerald", "Carl", "Terry",
        "Sean", "Austin", "Arthur", "Lawrence", "Jesse", "Dylan", "Bryan", "Joe", "Jordan", "Billy",
        "Bruce", "Albert", "Willie", "Gabriel", "Logan", "Alan", "Juan", "Wayne", "Roy", "Ralph",
        "Randy", "Eugene", "Vincent", "Russell", "Louis", "Philip", "Bobby", "Johnny", "Bradley", "Lucas",
        "Liam", "Oliver", "Elijah", "Mateo", "Leo", "Theo", "Ezra", "Hudson", "Luca", "Asher",
        "Aarav", "Vihaan", "Aditya", "Sai", "Arjun", "Rohan", "Vivaan", "Reyansh", "Krishna", "Kabir"
    ]
    first_names_f = [
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
        "Lisa", "Nancy", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle",
        "Carol", "Amanda", "Dorothy", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia",
        "Kathleen", "Amy", "Angela", "Shirley", "Anna", "Brenda", "Pamela", "Emma", "Nicole", "Helen",
        "Samantha", "Katherine", "Christine", "Debra", "Rachel", "Carolyn", "Janet", "Maria", "Heather", "Diane",
        "Virginia", "Julie", "Joyce", "Victoria", "Olivia", "Kelly", "Christina", "Lauren", "Joan", "Evelyn",
        "Judith", "Megan", "Andrea", "Cheryl", "Hannah", "Jacqueline", "Martha", "Gloria", "Teresa", "Ann",
        "Sara", "Madison", "Frances", "Kathryn", "Janice", "Jean", "Abigail", "Alice", "Julia", "Judy",
        "Sophia", "Grace", "Chloe", "Camila", "Penelope", "Aria", "Riley", "Zoey", "Nora", "Lily",
        "Eleanor", "Hannah", "Lillian", "Addison", "Aubrey", "Ellie", "Stella", "Natalie", "Zoe", "Leah",
        "Aanya", "Diya", "Saanvi", "Ananya", "Pari", "Isha", "Navya", "Riya", "Myra", "Avani"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
        "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
        "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
        "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
        "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
        "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
        "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Mendoza", "Castillo", "Hughes", "Price",
        "Alvarez", "Castillo", "Sanders", "Patel", "Sharma", "Verma", "Rao", "Gupta", "Singh", "Kumar",
        "Davies", "Evans", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Dubois", "Moreau"
    ]

    # Geographic Hierarchies
    geo_locations = [
        # USA (North America)
        {"city": "New York", "state": "New York", "country": "United States", "region": "North America", "weight": 0.12},
        {"city": "Los Angeles", "state": "California", "country": "United States", "region": "North America", "weight": 0.10},
        {"city": "Chicago", "state": "Illinois", "country": "United States", "region": "North America", "weight": 0.07},
        {"city": "Houston", "state": "Texas", "country": "United States", "region": "North America", "weight": 0.06},
        {"city": "Phoenix", "state": "Arizona", "country": "United States", "region": "North America", "weight": 0.04},
        {"city": "Philadelphia", "state": "Pennsylvania", "country": "United States", "region": "North America", "weight": 0.04},
        {"city": "Dallas", "state": "Texas", "country": "United States", "region": "North America", "weight": 0.04},
        {"city": "Seattle", "state": "Washington", "country": "United States", "region": "North America", "weight": 0.04},
        {"city": "Atlanta", "state": "Georgia", "country": "United States", "region": "North America", "weight": 0.03},
        {"city": "Miami", "state": "Florida", "country": "United States", "region": "North America", "weight": 0.03},
        # Canada (North America)
        {"city": "Toronto", "state": "Ontario", "country": "Canada", "region": "North America", "weight": 0.05},
        {"city": "Vancouver", "state": "British Columbia", "country": "Canada", "region": "North America", "weight": 0.03},
        # UK (Europe)
        {"city": "London", "state": "Greater London", "country": "United Kingdom", "region": "Europe", "weight": 0.07},
        {"city": "Manchester", "state": "Greater Manchester", "country": "United Kingdom", "region": "Europe", "weight": 0.03},
        {"city": "Birmingham", "state": "West Midlands", "country": "United Kingdom", "region": "Europe", "weight": 0.02},
        # Germany (Europe)
        {"city": "Berlin", "state": "Berlin", "country": "Germany", "region": "Europe", "weight": 0.04},
        {"city": "Munich", "state": "Bavaria", "country": "Germany", "region": "Europe", "weight": 0.03},
        {"city": "Frankfurt", "state": "Hesse", "country": "Germany", "region": "Europe", "weight": 0.02},
        # France (Europe)
        {"city": "Paris", "state": "Île-de-France", "country": "France", "region": "Europe", "weight": 0.04},
        {"city": "Lyon", "state": "Auvergne-Rhône-Alpes", "country": "France", "region": "Europe", "weight": 0.02},
        # India (Asia-Pacific)
        {"city": "Mumbai", "state": "Maharashtra", "country": "India", "region": "Asia-Pacific", "weight": 0.04},
        {"city": "Bengaluru", "state": "Karnataka", "country": "India", "region": "Asia-Pacific", "weight": 0.03},
        {"city": "Delhi", "state": "Delhi", "country": "India", "region": "Asia-Pacific", "weight": 0.03},
        # Australia (Asia-Pacific)
        {"city": "Sydney", "state": "New South Wales", "country": "Australia", "region": "Asia-Pacific", "weight": 0.03},
        {"city": "Melbourne", "state": "Victoria", "country": "Australia", "region": "Asia-Pacific", "weight": 0.02},
        # Latin America
        {"city": "São Paulo", "state": "São Paulo", "country": "Brazil", "region": "Latin America", "weight": 0.03},
        {"city": "Mexico City", "state": "CDMX", "country": "Mexico", "region": "Latin America", "weight": 0.02}
    ]

    # Normalize geo weights
    geo_weights = np.array([g["weight"] for g in geo_locations])
    geo_weights = geo_weights / geo_weights.sum()

    # Generate Gender
    genders = rng.choice(["Male", "Female", "Non-Binary"], size=num_customers, p=[0.48, 0.49, 0.03])

    # Assign First Names based on Gender
    male_count = np.sum(genders == "Male")
    female_count = np.sum(genders == "Female")
    nb_count = np.sum(genders == "Non-Binary")

    chosen_first_names = np.empty(num_customers, dtype=object)
    chosen_first_names[genders == "Male"] = rng.choice(first_names_m, size=male_count)
    chosen_first_names[genders == "Female"] = rng.choice(first_names_f, size=female_count)
    all_firsts = first_names_m + first_names_f
    chosen_first_names[genders == "Non-Binary"] = rng.choice(all_firsts, size=nb_count)

    chosen_last_names = rng.choice(last_names, size=num_customers)
    full_names = np.char.add(np.char.add(chosen_first_names.astype(str), " "), chosen_last_names.astype(str))

    # Age (Realistic normal distribution between 18 and 72)
    ages = np.clip(np.round(rng.normal(36, 11, size=num_customers)), 18, 72).astype(int)

    # Geo Sampling
    geo_indices = rng.choice(len(geo_locations), size=num_customers, p=geo_weights)
    cities = [geo_locations[i]["city"] for i in geo_indices]
    states = [geo_locations[i]["state"] for i in geo_indices]
    countries = [geo_locations[i]["country"] for i in geo_indices]
    regions = [geo_locations[i]["region"] for i in geo_indices]

    # Acquisition Channels
    channels = rng.choice(ACQUISITION_CHANNELS, size=num_customers, p=ACQUISITION_WEIGHTS)

    # Signup Dates: 2021-01-01 to 2025-10-31 with compounding growth
    start_ts = pd.Timestamp("2021-01-01").value // 10**9
    end_ts = pd.Timestamp("2025-10-31").value // 10**9
    # Power law / beta distribution towards more recent years
    time_fractions = rng.power(1.6, size=num_customers)
    signup_timestamps = start_ts + time_fractions * (end_ts - start_ts)
    signup_dates = pd.to_datetime(signup_timestamps, unit='s').strftime('%Y-%m-%d')

    # Emails
    customer_ids = np.arange(1, num_customers + 1)
    domains = ["gmail.com", "yahoo.com", "outlook.com", "icloud.com", "protonmail.com", "corporate.org"]
    chosen_domains = rng.choice(domains, size=num_customers, p=[0.50, 0.18, 0.18, 0.08, 0.04, 0.02])
    
    clean_firsts = np.char.lower(np.char.replace(chosen_first_names.astype(str), " ", ""))
    clean_lasts = np.char.lower(np.char.replace(chosen_last_names.astype(str), " ", ""))
    emails = [f"{f}.{l}.{cid}@{dom}" for f, l, cid, dom in zip(clean_firsts, clean_lasts, customer_ids, chosen_domains)]

    df = pd.DataFrame({
        "CustomerID": customer_ids,
        "CustomerName": full_names,
        "Gender": genders,
        "Age": ages,
        "SignupDate": signup_dates,
        "Email": emails,
        "City": cities,
        "State": states,
        "Country": countries,
        "Region": regions,
        "AcquisitionChannel": channels
    })

    out_file = RAW_DATA_DIR / "customers.csv"
    df.to_csv(out_file, index=False)
    logger.info(f"Successfully generated {len(df):,} customers -> {out_file}")
    return df

if __name__ == "__main__":
    generate_customers()
