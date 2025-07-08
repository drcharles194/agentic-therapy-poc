"""
Friendly name generator for demo users.
Generates randomized but realistic first and last name combinations.
"""

import random
from typing import List, Tuple

# Curated lists of common first and last names for demo users
FIRST_NAMES: List[str] = [
    # Female names
    "Emma", "Olivia", "Sophia", "Isabella", "Mia", "Charlotte", "Amelia", "Harper", "Evelyn", "Abigail",
    "Emily", "Elizabeth", "Sofia", "Avery", "Ella", "Scarlett", "Grace", "Victoria", "Riley", "Aria",
    "Lily", "Aubrey", "Zoey", "Penelope", "Lillian", "Addison", "Layla", "Natalie", "Camila", "Hannah",
    
    # Male names  
    "Liam", "Noah", "Oliver", "William", "Elijah", "James", "Benjamin", "Lucas", "Mason", "Ethan",
    "Alexander", "Henry", "Jacob", "Michael", "Daniel", "Logan", "Jackson", "Sebastian", "Jack", "Aiden",
    "Owen", "Samuel", "Matthew", "Joseph", "Levi", "Mateo", "David", "John", "Wyatt", "Carter",
    
    # Gender-neutral names
    "Alex", "Jordan", "Taylor", "Casey", "Riley", "Avery", "Quinn", "River", "Sage", "Rowan",
    "Charlie", "Finley", "Emery", "Parker", "Blake", "Hayden", "Reese", "Cameron", "Drew", "Skylar"
]

LAST_NAMES: List[str] = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
    "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper"
]


def generate_friendly_name() -> str:
    """
    Generate a friendly human name by combining a random first and last name.
    
    Returns:
        str: A friendly name like "Emma Johnson" or "Alex Martinez"
    """
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    return f"{first_name} {last_name}"


def generate_name_components() -> Tuple[str, str]:
    """
    Generate first and last name components separately.
    
    Returns:
        Tuple[str, str]: (first_name, last_name)
    """
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    return first_name, last_name


def is_name_available(name: str, existing_names: List[str]) -> bool:
    """
    Check if a generated name is available (not already in use).
    
    Args:
        name: The name to check
        existing_names: List of names already in use
        
    Returns:
        bool: True if the name is available, False otherwise
    """
    return name.lower() not in [existing.lower() for existing in existing_names]


def generate_unique_name(existing_names: List[str], max_attempts: int = 50) -> str:
    """
    Generate a unique friendly name that doesn't conflict with existing names.
    
    Args:
        existing_names: List of names already in use
        max_attempts: Maximum number of generation attempts before giving up
        
    Returns:
        str: A unique friendly name
        
    Raises:
        ValueError: If unable to generate unique name after max_attempts
    """
    for _ in range(max_attempts):
        name = generate_friendly_name()
        if is_name_available(name, existing_names):
            return name
    
    # If we can't find a unique combination, append a number
    base_name = generate_friendly_name()
    counter = 1
    while f"{base_name} {counter}" in existing_names and counter < 100:
        counter += 1
    
    return f"{base_name} {counter}" 