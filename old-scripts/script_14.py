
# Now create individual files that can be downloaded
import os

# Write all files
for filepath, content in files.items():
    # Create directory structure
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Created: {filepath}")

print(f"\n{'='*60}")
print(f"Successfully created all {len(files)} files!")
print(f"{'='*60}")
