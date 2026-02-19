import os

path = r'd:\PROJECTS\wildsight1 - Copy\backend\app\services\intelligence.py'
if not os.path.exists(path):
    print(f"Error: {path} not found")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Look for the block around 678
# Target is lines 678 to 697 (1-indexed) -> index 677 to 696
# We want to remove one leading space from each of these lines IF they start with at least 14 spaces.

new_lines = []
for i, line in enumerate(lines):
    # i is 0-indexed, so line 678 is index 677
    if i >= 677 and i <= 696:
        if line.startswith('              '): # 14 spaces
             new_lines.append(line[1:]) # Remove one space
        else:
             new_lines.append(line)
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Repair complete.")
