from collections import Counter
from game.world import YOLO_TO_WEAPON, YOLO_TO_ROOM
from inspector import deduction as ded
from inspector import narrative as nar
from game import state as st

def observe(detections, memory, probs):
    """
    Observe. The most important skill. The one every other detective skips
    in favour of having a hunch. Inspector Liddy does not have hunches.
    She has observations. The distinction is the difference between her and them.
    """
    weapons_found = []
    rooms_found   = []
    suspect_count = sum(1 for d in detections if d["class"] == "person")

    for det in detections:
        label = det["class"]
        conf  = det["confidence"]

        weapon = YOLO_TO_WEAPON.get(label)
        if weapon:
            weapons_found.append(weapon)
            probs = ded.update_weapon(probs, weapon, boost=1.8 + conf)
            st.log_clue(label, weapon, suspect_count, conf)

        room = YOLO_TO_ROOM.get(label)
        if room:
            rooms_found.append(room)
            probs = ded.update_room(probs, room, boost=3.0)

    if suspect_count > 0:
        probs = ded.update_suspects(probs, suspect_count)

    detected_room = Counter(rooms_found).most_common(1)[0][0] if rooms_found else None

    memory.remember({
        "weapon":        weapons_found[0] if weapons_found else None,
        "room":          detected_room,
        "suspect_count": suspect_count,
        "raw":           [d["class"] for d in detections],
    })

    room_narration = ""
    if detected_room:
        room_narration = " " + nar.on_room_deduction(detected_room)

    narration = nar.on_observation(weapons_found or [d["class"] for d in detections])
    return narration + room_narration, probs


def forensics(memory, probs):
    """
    Cross-referencing clues like she has done it before. She has.
    More times than anyone in this room would be comfortable knowing.
    """
    weapon = memory.most_seen_weapon()
    note   = nar.on_forensics()

    if weapon:
        probs = ded.update_weapon(probs, weapon, boost=1.6)
        note += f" The {weapon} keeps surfacing. She does not believe in coincidence."

    room = memory.most_likely_room()
    if room:
        probs = ded.update_room(probs, room, boost=1.4)
        note += f" The {room} recurs in the evidence. She notes it without surprise."

    return probs, note


def interrogate(suspect_name, probs):
    """
    Manually implicating a suspect. She disapproves of doing this without cause.
    You are doing it anyway, which tells her something about you too.
    """
    if suspect_name in probs["suspects"]:
        probs["suspects"][suspect_name] *= 2.0
        total = sum(probs["suspects"].values())
        probs["suspects"] = {k: v / total for k, v in probs["suspects"].items()}

    note = f"{suspect_name}. She has questions. They have answers they would prefer to keep."
    return probs, note
