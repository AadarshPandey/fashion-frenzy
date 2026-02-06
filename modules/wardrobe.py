import os
import shutil
from PIL import Image

# Define the root directory for the wardrobe
WARDROBE_ROOT = "user_wardrobe"

# Define categories and their folder mappings
CATEGORIES = {
    "Head/Hair": "above_head",
    "Face (Glasses/Masks)": "on_face",
    "Neck": "on_neck",
    "Upper Body": "upper_body",
    "Lower Body": "lower_body",
    "Feet": "feet",
    "Special: Saree/Drapes (Overlap)": "special_overlap" 
}

def init_wardrobe():
    """Ensures all necessary folders exist."""
    if not os.path.exists(WARDROBE_ROOT):
        os.makedirs(WARDROBE_ROOT)
    
    for folder in CATEGORIES.values():
        path = os.path.join(WARDROBE_ROOT, folder)
        if not os.path.exists(path):
            os.makedirs(path)

def save_uploaded_item(uploaded_file, category):
    """Saves the uploaded image to the correct folder."""
    if uploaded_file is None:
        return None

    folder_name = CATEGORIES.get(category, "misc")
    save_path = os.path.join(WARDROBE_ROOT, folder_name)
    
    # Ensure directory exists (redundancy check)
    os.makedirs(save_path, exist_ok=True)

    # Create a full file path
    file_path = os.path.join(save_path, uploaded_file.name)
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def get_wardrobe_inventory():
    """Returns a text summary of what is in the wardrobe for the LLM context."""
    inventory = []
    if os.path.exists(WARDROBE_ROOT):
        for category, folder in CATEGORIES.items():
            path = os.path.join(WARDROBE_ROOT, folder)
            if os.path.exists(path):
                files = os.listdir(path)
                if files:
                    inventory.append(f"Category {category}: {', '.join(files)}")
    return "\n".join(inventory)

def delete_item(file_path):
    """Deletes an item from the wardrobe given its full file path."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True, f"Deleted {os.path.basename(file_path)}"
        else:
            return False, "File not found."
    except Exception as e:
        return False, f"Error deleting file: {str(e)}"