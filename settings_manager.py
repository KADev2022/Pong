import json
from pathlib import Path

from paths import data_path

# Store settings in the user's application data folder
SETTINGS_FILE = Path(data_path("settings.json"))

# Existing settings file in the project folder
LEGACY_SETTINGS_FILE = Path(__file__).resolve().parent / "settings.json"

# Default settings
DEFAULT_SETTINGS = {
    "music_volume": 0.4,
    "sound_volume": 0.8,
    "difficulty": "Medium",
    "fullscreen": False
}

def load_settings():
    # Prefer the new settings file if it already exists
    if SETTINGS_FILE.exists():
        file_to_load = SETTINGS_FILE
    # Otherwise, use the existing project settings file
    elif LEGACY_SETTINGS_FILE.exists():
        file_to_load = LEGACY_SETTINGS_FILE
    else:
        return DEFAULT_SETTINGS.copy()
        

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            saved_settings = json.load(file)
        
        if not isinstance(saved_settings, dict):
            raise ValueError("Invalid settings format")
        
        # Merge saved settings with defaults
        loaded_settings = DEFAULT_SETTINGS.copy()
        loaded_settings.update(saved_settings)
        
        # Validate volume values
        for key in ("music_volume", "sound_volume"):
            value = loaded_settings[key]
            
            if type(value) not in (int, float):
                raise ValueError("Invalid volume value")
            
            loaded_settings[key] = max(0.0, min(1.0, float(value)))
            
        # Validate difficulty
        if loaded_settings["difficulty"] not in ("Easy", "Medium", "Hard"):
            loaded_settings["difficulty"] = "Medium"
        
        # Validate fullscreen preference
        if type(loaded_settings["fullscreen"]) is not bool:
            loaded_settings["fullscreen"] = False
        
        # Migrate existing settings to AppData
        if file_to_load == LEGACY_SETTINGS_FILE:
            try:
                with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
                    json.dump(loaded_settings, file, indent=4)
                
                print("Existing settings migrated successfully.")
            except OSError as error:
                print(f"Could not migrate settings: {error}")
        
        return loaded_settings
    except (OSError, ValueError, TypeError):
        return DEFAULT_SETTINGS.copy()

def save_settings(music_volume, sound_volume, difficulty, fullscreen=False):
    data = {
        "music_volume": music_volume,
        "sound_volume": sound_volume,
        "difficulty": difficulty,
        "fullscreen": fullscreen
    }
    
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except OSError as error:
        print(f"Could not save settings: {error}")