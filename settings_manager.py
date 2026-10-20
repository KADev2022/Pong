import json
from pathlib import Path

# Store settings beside this Python file
SETTINGS_FILE = Path(__file__).resolve().parent / "settings.json"

# Default settings
DEFAULT_SETTINGS = {
    "music_volume": 0.4,
    "sound_volume": 0.8,
    "difficulty": "Medium",
    "fullscreen": False
}

def load_settings():
    # Return defaults if no settings file exists
    if not SETTINGS_FILE.exists():
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, "r") as file:
            saved_settings = json.load(file)
        
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
        with open(SETTINGS_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except OSError as error:
        print(f"Could not save settings: {error}")