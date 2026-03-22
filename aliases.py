"""
aliases.py — Defines custom nicknames, slang, and rules for matching player names on Reddit.
"""

# If a player's last name is in this list, we WILL NOT count mentions of just their last name.
# This prevents "Will Smith" from getting a point every time someone says "Smith just struck out".
# They must be referred to by their full name or a specific custom alias.
COMMON_LAST_NAMES = {
    "Abreu", "Acuña", "Adams", "Alexander", "Allen", "Alvarado", "Alvarez", "Anderson", "Ashcraft", "Bailey",
    "Baker", "Baldwin", "Barnes", "Beck", "Bell", "Bennett", "Berroa", "Brooks", "Brown", "Bryant",
    "Burke", "Butler", "Campbell", "Carter", "Castillo", "Chapman", "Clark", "Clarke", "Cole", "Coleman",
    "Collins", "Contreras", "Cook", "Cooper", "Cox", "Crawford", "Cruz", "Davis", "Diaz", "Duran",
    "Díaz", "Edwards", "Estrada", "Evans", "Festa", "Flores", "Foster", "France", "Freeland", "Freeman",
    "Garcia", "García", "Gilbert", "Gomez", "Gonzales", "Gonzalez", "González", "Gray", "Green", "Greene",
    "Griffin", "Gómez", "Hall", "Harris", "Hayes", "Henderson", "Hernandez", "Hernández", "Hicks", "Hill",
    "Holmes", "Howard", "Hughes", "Jackson", "James", "Jansen", "Jenkins", "Johnson", "Jones", "Jung",
    "Keller", "Kelly", "Kim", "King", "Lee", "Leiter", "Lewis", "Long", "Lopez", "Lowe",
    "López", "Marte", "Martin", "Martinez", "Martínez", "May", "Miller", "Mitchell", "Montgomery", "Moore",
    "Morgan", "Morris", "Muncy", "Murphy", "Muñoz", "Myers", "Naylor", "Nelson", "Ortiz", "Parker",
    "Patterson", "Pena", "Peralta", "Perez", "Perry", "Peterson", "Peña", "Phillips", "Powell", "Price",
    "Pérez", "Raley", "Ramirez", "Ramos", "Ramírez", "Ray", "Reed", "Richardson", "Rivera", "Roberts",
    "Robinson", "Rodriguez", "Rodríguez", "Rogers", "Ross", "Ruiz", "Russell", "Ryan", "Sale", "Sanchez",
    "Sanders", "Santana", "Scott", "Seymour", "Simmons", "Smith", "Soriano", "Sosa", "Soto", "Stephenson",
    "Stewart", "Story", "Suarez", "Suárez", "Sánchez", "Taylor", "Thomas", "Thompson", "Torres", "Tucker",
    "Turner", "Vargas", "Varland", "Walker", "Ward", "Washington", "Watson", "Webb", "Wells", "White",
    "Williams", "Williamson", "Wilson", "Winn", "Wood", "Wright", "Young", "Álvarez", "Spring", "Springs"
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
