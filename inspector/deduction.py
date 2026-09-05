# Bayesian update. Could've used a neural net. Could've also lit a candle and hoped.
# This is faster than both and only slightly less mystical.

from game.world import SUSPECTS, WEAPONS, ROOMS

def uniform_priors():
    # Everyone is equally suspicious at the start. Inspector Liddy finds this amusing.
    return {
        "suspects": {s: 1.0 / len(SUSPECTS) for s in SUSPECTS},
        "weapons":  {w: 1.0 / len(WEAPONS)  for w in WEAPONS},
        "rooms":    {r: 1.0 / len(ROOMS)    for r in ROOMS},
    }

def _normalize(d):
    # The one function in this codebase that treats everyone fairly. She does not.
    total = sum(d.values())
    return {k: v / total for k, v in d.items()} if total else d

def update_weapon(probs, weapon_name, boost=2.5):
    # A bottle on the floor is not ambiance. The boost reflects that.
    if weapon_name in probs["weapons"]:
        probs["weapons"][weapon_name] *= boost
        probs["weapons"] = _normalize(probs["weapons"])
    return probs

def update_suspects(probs, count, boost=1.4):
    # More faces in the frame means more people who had something to lose.
    # Rich get richer. Suspicious get more suspicious. Same principle.
    suspects = list(probs["suspects"].keys())
    if count <= 0 or count > len(suspects):
        return probs
    top_n = sorted(suspects, key=lambda s: probs["suspects"][s], reverse=True)[:count]
    for s in top_n:
        probs["suspects"][s] *= boost
    probs["suspects"] = _normalize(probs["suspects"])
    return probs

def update_room(probs, room_name, boost=3.0):
    # When YOLO sees a bed, Inspector Liddy does not think "Drawing Room."
    # She is thorough, not delusional.
    if room_name in probs["rooms"]:
        probs["rooms"][room_name] *= boost
        probs["rooms"] = _normalize(probs["rooms"])
    return probs

def top(probs, category):
    return max(probs[category], key=lambda k: probs[category][k])

def confidence(probs):
    # Average of the three category maxima. Crude but honest. Like most confessions.
    return (
        max(probs["suspects"].values()) +
        max(probs["weapons"].values()) +
        max(probs["rooms"].values())
    ) / 3
