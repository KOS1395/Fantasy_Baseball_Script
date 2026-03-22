import json
import re
import sys

# Read aliases.py to get the old COMMON_LAST_NAMES list
with open('aliases.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Extract the block
match = re.search(r'COMMON_LAST_NAMES\s*=\s*\{([^}]+)\}', code)
if not match:
    print("Could not find COMMON_LAST_NAMES in aliases.py")
    sys.exit(1)

old_block = match.group(1)
old_names = set(re.findall(r'"([^"]+)"', old_block))

# Read out.txt
with open('out.txt', 'r', encoding='utf-8') as f:
    text = f.read()

new_names = set(re.findall(r'"([^"]+)"', text))

combined = old_names.union(new_names)

out = 'COMMON_LAST_NAMES = {\n    '
items = sorted(list(combined))
out_lines = []
for i in range(0, len(items), 10):
    out_lines.append(', '.join(f'"{name}"' for name in items[i:i+10]))
out += ',\n    '.join(out_lines)
out += '\n}\n'

code = re.sub(r'COMMON_LAST_NAMES\s*=\s*\{[^}]+\}', out.strip(), code, count=1)

with open('aliases.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Successfully merged and updated aliases.py")
