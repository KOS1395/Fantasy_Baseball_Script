"""
aliases.py — Defines custom nicknames, slang, and rules for matching player names on Reddit.
"""

# If a player's last name is in this list, we WILL NOT count mentions of just their last name.
# This prevents "Will Smith" from getting a point every time someone says "Smith just struck out".
# They must be referred to by their full name or a specific custom alias.
COMMON_LAST_NAMES = {
    "Smith", "Jones", "Williams", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson",
    "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark",
    "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright",
    "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter", "Mitchell",
    "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins",
    "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey",
    "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez",
    "James", "Watson", "Brooks", "Kelly", "Sanders", "Price", "Bennett", "Wood", "Barnes", "Ross",
    "Henderson", "Coleman", "Jenkins", "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores",
    "Washington", "Butler", "Simmons", "Foster", "Gonzales", "Bryant", "Alexander", "Russell", "Griffin",
    "Diaz", "Hayes", "Cruz", "Gomez", "Tucker", "Sale", "May", "Story", "Lowe", "Ray", "France", "Pena", "Soto", 
    "García", "Sánchez", "Ramírez", "Ryan", "López", "Pérez", "Hernández", "González", "Díaz", "Martínez", 
    "Rodríguez", "Peña", "Gómez", "Marte", "Álvarez", "Suárez", "Johnson", "Holmes",  "Suarez", "Alvarez", "Ashcraft"
}

# Mapping of Full Player Name to a list of allowed aliases/nicknames.
# This ensures we catch slang like "CES" or "J-Rod".
PLAYER_ALIASES = {
    "Christian Encarnacion-Strand": ["CES", "Encarnacion-Strand"],
    "Julio Rodriguez": ["J-Rod", "JRod", "Julio", "JuRod"],
    "Shohei Ohtani": ["Shohei"],
    "Vladimir Guerrero Jr.": ["Vlad", "Vladdy"],
    "Ronald Acuna Jr.": ["Acuna"],
    "Fernando Tatis Jr.": ["Tatis"],
    "Corbin Carroll": ["Corbin"],
    "Elly De La Cruz": ["Elly", "EDLC"],
    "Paul Goldschmidt": ["Goldy"],
    "Pete Alonso": ["Polar Bear"],
    "Aaron Judge": ["All Rise"], # "Judge" is usually their last name, which works if not common
    "Randy Arozarena": ["Randy"],
    "Jazz Chisholm Jr.": ["Jazz"],
    "Francisco Lindor": ["Lindor"],
    "Spencer Strider": ["Strider"], # His last name is caught mostly, but good to ensure
    "Gunnar Henderson": ["Gunnar"],
    "Adley Rutschman": ["Adley"],
    "Mookie Betts": ["Mookie"],
    "Yordan Alvarez": ["Yordan", "Yordong"],
    "Bo Bichette": ["Bo", "Bobo"],
    "Ozzie Albies": ["Ozzie"],
    "Jose Ramirez": ["JoRam", "J-Ram"],
    "Luis Robert Jr.": ["LuBob", "Luis Robert"],
    "Zack Greinke": ["Greinke"],
    "Michael Harris II": ["Harris II", "MH2", "Money Mike"],
    "Oneil Cruz": ["Oneil"],
    "Cal Raleigh": ["Big Dumper"],
}

def get_search_terms(full_name: str) -> list[str]:
    """
    Given a player's full name, return a list of valid string tokens
    to search for in Reddit comments.
    """
    terms = [full_name]
    
    # Add custom aliases if any
    if full_name in PLAYER_ALIASES:
        terms.extend(PLAYER_ALIASES[full_name])
        
    # Extract last name
    parts = full_name.split()
    if len(parts) >= 2:
        last_name = parts[-1].strip(".,'")
        # Handle suffixes like "Jr.", "II", "III"
        if last_name.lower() in {"jr", "jr.", "sr", "sr.", "ii", "iii"} and len(parts) >= 3:
            last_name = parts[-2].strip(".,'")
            
        # Only use last name if it's not super common and > 3 letters (avoiding short bursts)
        # Or if it's explicitly allowed.
        if last_name not in COMMON_LAST_NAMES and len(last_name) >= 4:
            # We don't want to duplicate if it's already an alias
            if last_name not in terms:
                terms.append(last_name)
                
    return terms
