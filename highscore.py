import os
from pathlib import Path
from paths import data_path

# New high score location in AppData
HIGH_SCORE_FILE = Path(data_path("highscore.txt"))

# Original high score location in project folder
LEGACY_HIGH_SCORE_FILE = Path(__file__).resolve().parent / "highscore.txt"

"""
Load the saved high score. Returns 0 if none exists.
"""
def load_high_score():
    # Prefer the new AppData high score file
    if HIGH_SCORE_FILE.exists():
        file_to_load = HIGH_SCORE_FILE
    # Otherwise, check the original project folder
    elif LEGACY_HIGH_SCORE_FILE.exists():
        file_to_load = LEGACY_HIGH_SCORE_FILE
    else:
        return 0

    try:
        with open(file_to_load, "r", encoding="utf-8") as file:
            score = int(file.read().strip())
            
        # Ensure the score is not negative
        score = max(0, score)
        
        # Migrate the old high score to AppData
        if file_to_load == LEGACY_HIGH_SCORE_FILE:
            save_high_score(score)
            print("Existing high score migrated to AppData.")
        
        return score
    except (ValueError, OSError):
        return 0

"""
Save the high score to AppData.
""" 
def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as file:
            file.write(str(score))
    except OSError as error:
        print(f"Could not save high score: {error}")