import random
import json
import os
from game.world import SUSPECTS, WEAPONS, ROOMS

def generate(room_override=None):
    # Random culprit and weapon. Room is discovered from the camera unless overridden.
    # If the player is in their bedroom, Sir Edmund died in the Guest Chamber. Tragic.
    return {
        "culprit": random.choice(list(SUSPECTS.keys())),
        "weapon":  random.choice(list(WEAPONS.keys())),
        "room":    room_override or random.choice(ROOMS),
    }

def save(mystery, path="data/mystery.json"):
    os.makedirs("data", exist_ok=True)
    with open(path, "w") as f:
        json.dump(mystery, f)

def load(path="data/mystery.json"):
    with open(path, "r") as f:
        return json.load(f)
