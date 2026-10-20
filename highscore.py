import os

FILENAME = "highscore.txt"

"""
Load the saved high score. Returns 0 if none exists.
"""
def load_high_score():
    if not os.path.exists(FILENAME):
        return 0

    try:
        with open(FILENAME, "r") as file:
            return int(file.read())
    except (ValueError, FileNotFoundError):
        return 0

"""
Save a new high score.
""" 
def save_high_score(score):
    with open(FILENAME, "w") as file:
        file.write(str(score))