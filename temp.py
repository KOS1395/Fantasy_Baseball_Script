import json
from mlb_stats import get_active_mlb_players
import collections

# Get all players
players = get_active_mlb_players()

last_names = collections.defaultdict(int)

for p in players:
    parts = p['name'].split()
    if len(parts) >= 2:
        last_name = parts[-1].strip(".,'")
        # Handle suffixes
        if last_name.lower() in {'jr', 'jr.', 'sr', 'sr.', 'ii', 'iii'} and len(parts) >= 3:
            last_name = parts[-2].strip(".,'")
            
        if len(last_name) >= 3:
            last_names[last_name] += 1

# Filter to names with 2 or more players
common = {k for k, v in last_names.items() if v >= 2}

# Output as a formatted python set
print("NEW_COMMON_LAST_NAMES = {")
items = sorted(list(common))
for i in range(0, len(items), 10):
    line = "    " + ", ".join(f'"{name}"' for name in items[i:i+10]) + ","
    print(line)
print("}")
