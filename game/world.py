# Victorian names because "Mr. Green" is what you call a suspect at a children's party.

SUSPECTS = {
    "Lord Blackwood": {
        "description": "The host. Charming. Too charming.",
        "color_hint": "navy",
    },
    "Lady Ashford": {
        "description": "Widow. Third time. Interesting.",
        "color_hint": "purple",
    },
    "Dr. Pembrooke": {
        "description": "Physician. Knows poisons. How convenient for him.",
        "color_hint": "green",
    },
    "Colonel Ravenswood": {
        "description": "Retired. Restless. Armed.",
        "color_hint": "red",
    },
    "Miss Thorne": {
        "description": "Secretary. Observant. Too quiet by half.",
        "color_hint": "teal",
    },
    "Graves the Butler": {
        "description": "Loyal. To someone, at any rate.",
        "color_hint": "grey",
    },
}

WEAPONS = {
    "Candlestick":   "A blunt instrument dressed up for dinner.",
    "Letter Opener": "Seven inches of Sheffield steel. Not just for letters.",
    "Poison Vial":   "Odorless. Tasteless. Efficient.",
    "Silk Cord":     "Strong enough. No mess.",
    "Revolver":      "Loud. Desperate. Decisive.",
    "Iron Poker":    "Always by the fireplace. Never noticed until now.",
}

# These are the rooms as Inspector Liddy calls them.
# Your bedroom is a Guest Chamber. Your bathroom is Servants Quarters.
# She is not being rude. That is simply what they are.
ROOMS = [
    "Drawing Room",
    "Library",
    "Conservatory",
    "Billiard Room",
    "Kitchen",
    "Wine Cellar",
    "Study",
    "Ballroom",
    "Guest Chamber",
    "Servants Quarters",
]

# What YOLO sees -> what Inspector Liddy calls it.
# A bottle is not a bottle. It is a Poison Vial with ambitions.
YOLO_TO_WEAPON = {
    "knife":      "Letter Opener",
    "scissors":   "Letter Opener",
    "bottle":     "Poison Vial",
    "wine glass": "Poison Vial",
    "cup":        "Candlestick",
    "cell phone": "Revolver",
    "remote":     "Revolver",
    "umbrella":   "Iron Poker",
    "baseball bat": "Iron Poker",
    "tie":        "Silk Cord",
}

# What YOLO sees -> which room Inspector Liddy decides she is standing in.
# Your couch is not a clue. Your couch is a geographical statement.
YOLO_TO_ROOM = {
    "bed":          "Guest Chamber",
    "couch":        "Drawing Room",
    "tv":           "Drawing Room",
    "chair":        "Drawing Room",
    "refrigerator": "Kitchen",
    "oven":         "Kitchen",
    "sink":         "Kitchen",
    "microwave":    "Kitchen",
    "toaster":      "Kitchen",
    "book":         "Library",
    "laptop":       "Study",
    "keyboard":     "Study",
    "mouse":        "Study",
    "clock":        "Study",
    "potted plant": "Conservatory",
    "vase":         "Conservatory",
    "wine glass":   "Wine Cellar",
    "dining table": "Ballroom",
    "toilet":       "Servants Quarters",
    "toothbrush":   "Servants Quarters",
    "pool table":   "Billiard Room",
}

VICTIM_NAME = "Sir Edmund Hartley"
