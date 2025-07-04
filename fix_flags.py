import os
import shutil

def fix_flag_images():
    """Create properly named flag images by creating copies with expected names."""
    
    # Path to the flags directory
    flags_dir = os.path.join("static", "img", "flags")
    
    # Define the mappings of existing files to names that should exist
    flag_mappings = {
        # Map current files to their expected names
        "jap.jpg": ["japan.jpg"],
        "aus.jpg": ["australia.jpg"],
        "britian.jpg": ["great_britain.jpg"],
        "saudi.jpg": ["saudi_arabia.jpg"],
        "emilia.jpg": ["emilia_romagna.jpg"],
        "us.jpg": ["united_states.jpg"],
        "sao_paulo.jpg": ["brazil.jpg"],
        "abu_dhabi.jpg": ["abu_dhabi.jpg"],
    }
    
    # Create a backup directory
    backup_dir = os.path.join(flags_dir, "backup")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Copy files to create properly named versions
    for source, destinations in flag_mappings.items():
        source_path = os.path.join(flags_dir, source)
        
        # Check if source file exists
        if os.path.exists(source_path):
            print(f"Processing {source}...")
            
            # Create each of the destination files
            for destination in destinations:
                dest_path = os.path.join(flags_dir, destination)
                
                # Skip if already exists and is not the same file
                if os.path.exists(dest_path) and os.path.samefile(source_path, dest_path):
                    print(f"  Skipping {destination} (same file)")
                    continue
                    
                # Skip if already exists as a different file
                if os.path.exists(dest_path):
                    print(f"  Backing up existing {destination}")
                    backup_path = os.path.join(backup_dir, destination)
                    shutil.copy2(dest_path, backup_path)
                
                # Create a copy with the correct name
                print(f"  Creating {destination}")
                shutil.copy2(source_path, dest_path)
        else:
            print(f"Warning: Source file {source} not found")
    
    print("Flag image corrections completed!")

if __name__ == "__main__":
    fix_flag_images() 