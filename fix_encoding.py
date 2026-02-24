

import os

path = os.path.join(os.path.dirname(__file__), 'templates', 'owner', 'draft_billing.html')

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Show before counts
print("Before replacements:")
print("  â‚¹ count:", content.count('â\u201a¹'))
print("  â€\" count:", content.count('â\u20ac\u201d'))
print("  Ã— count:", content.count('Ã\u00d7'))

# Fix garbled characters
content = content.replace('â\u201a¹', '₹')        # ₹ rupee sign
content = content.replace('â\u20ac\u201d', '\u2014')  # — em dash
content = content.replace('Ã\u00d7', '\u00d7')        # × multiplication sign

print("After replacements done. Writing file...")

with open(path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)

print("Done! File saved with correct UTF-8 encoding.")
