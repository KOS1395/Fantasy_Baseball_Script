import json
from mlb_stats import get_active_mlb_players
import collections
players = get_active_mlb_players()

last_names = collections.defaultdict(int)

for p in players:
    parts = p['name'].split()
    if len(parts) >= 2:
        last_name = parts[-1].strip(".,'")
        if last_name.lower() in {'jr', 'jr.', 'sr', 'sr.', 'ii', 'iii'} and len(parts) >= 3:
            last_name = parts[-2].strip(".,'")
        if len(last_name) >= 3:
            last_names[last_name] += 1

common = {k for k, v in last_names.items() if v >= 2}

with open("out.txt", "w", encoding="utf-8") as f:
    f.write('COMMON_LAST_NAMES = {\n    ')
    items = sorted(list(common))
    lines = []
    for i in range(0, len(items), 10):
        lines.append(', '.join(f'"{name}"' for name in items[i:i+10]))
    f.write(',\n    '.join(lines))
    f.write('\n}\n')
