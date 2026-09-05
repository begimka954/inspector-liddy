import json
import os
from inspector.memory import Memory
from inspector.deduction import uniform_priors, top, confidence
from inspector.narrative import LLMNarrator, intro, on_deduction, on_accusation
from inspector.skills import observe, forensics, interrogate
from game import state as st

class InspectorLiddy:
    """
    Inspector Liddy. Brilliant. Methodical. She solved the Ashworth case in eleven minutes.
    The local inspector took three weeks and got the wrong man.
    She has not forgotten this. Neither has the local inspector.
    """
    def __init__(self, mystery, session_id=None):
        self.mystery    = mystery
        self.memory     = Memory()
        self.probs      = uniform_priors()
        self.narrator   = LLMNarrator()
        self.log        = []
        self.scan_count = 0

        # She initialises the database the same way she enters a room -- first, and without asking.
        st.init()
        self.session_id = session_id or st.start_session(mystery)

        self.log.append(intro())

    def scan(self, detections):
        """
        Feed one round of camera detections to Inspector Liddy.
        She processes them in under a second. The Bayesian math takes slightly longer.
        """
        self.scan_count += 1
        narration, self.probs = observe(detections, self.memory, self.probs)

        # Every third scan she surfaces a conclusion. She is not hasty. She is thorough.
        # There is a difference and she will explain it if you have the time.
        if self.scan_count % 3 == 0:
            suspect = top(self.probs, "suspects")
            weapon  = top(self.probs, "weapons")
            room    = top(self.probs, "rooms")

            summary = (
                f"Recent observations: {[e['raw'] for e in self.memory.recent()]}. "
                f"Leading suspect: {suspect}. Likely weapon: {weapon}. Likely room: {room}."
            )
            llm_line  = self.narrator.speak(summary)
            deduction = llm_line if llm_line else on_deduction(suspect, weapon, room)
            narration = narration + " " + deduction
            st.log_deduction(self.probs["suspects"], self.probs["weapons"], self.probs["rooms"])

        self.log.append(narration)
        return narration

    def run_forensics(self):
        self.probs, note = forensics(self.memory, self.probs)
        self.log.append(note)
        return note

    def interrogate(self, suspect_name):
        self.probs, note = interrogate(suspect_name, self.probs)
        self.log.append(note)
        return note

    def accuse(self):
        suspect = top(self.probs, "suspects")
        weapon  = top(self.probs, "weapons")
        room    = top(self.probs, "rooms")
        conf    = confidence(self.probs)

        statement = on_accusation(suspect, weapon, room)
        self.log.append(statement)

        correct = (
            suspect == self.mystery["culprit"]
            and weapon == self.mystery["weapon"]
            and room   == self.mystery["room"]
        )

        if self.session_id:
            st.close_session(self.session_id, correct)

        return {
            "suspect":    suspect,
            "weapon":     weapon,
            "room":       room,
            "confidence": conf,
            "correct":    correct,
            "actual":     self.mystery,
            "statement":  statement,
        }

    def state(self):
        return {
            "probs":      self.probs,
            "suspect":    top(self.probs, "suspects"),
            "weapon":     top(self.probs, "weapons"),
            "room":       top(self.probs, "rooms"),
            "confidence": confidence(self.probs),
            "scans":      self.scan_count,
            "log":        self.log,
            "llm_ready":  self.narrator.available,
        }

    def export(self, path="data/case_report.json"):
        # She writes the case report the same way she writes everything -- completely and without mercy.
        os.makedirs("data", exist_ok=True)
        report = {
            "inspector": "Inspector Liddy",
            "mystery":   self.mystery,
            "evidence":  self.memory.to_dict(),
            "final_deduction": {
                "suspect":    top(self.probs, "suspects"),
                "weapon":     top(self.probs, "weapons"),
                "room":       top(self.probs, "rooms"),
                "confidence": confidence(self.probs),
            },
            "thought_log": self.log,
        }
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
        return path
