import random

# Templates for when the LLM decides it has better things to do.
# She speaks in certainties. The templates do their humble best impression.

INTRO = [
    "Inspector Liddy. Called in because the local authorities are, as usual, decorative.",
    "I observe. I remember. I deduce. In that order. Not negotiable.",
    "Sir Edmund Hartley is dead. Someone in this house is responsible. I intend to make their evening considerably worse.",
    "You have a problem. I have a method. The method has never failed. The problem has never survived it.",
    "I did not come here to speculate. I came here to know. There is a difference.",
]

OBSERVATION = [
    "The {obj} is here. That is not nothing. In fact, that is quite something.",
    "A {obj} in plain sight. Either brazen or careless. Both are useful to me.",
    "I note the {obj}. It will matter later. Everything matters later.",
    "One does not leave a {obj} about without reason. I am very interested in the reason.",
    "The {obj}. Interesting placement. Very interesting. She files it away.",
]

ROOM_DEDUCTION = [
    "This is the {room}. She has catalogued it. The walls have already told her more than they intended.",
    "The {room}. Of course. Sir Edmund had reasons to be here. Someone had reasons to follow.",
    "She stands in the {room} and sees it immediately.the room knows what happened.",
    "The {room}. She makes a note. Not a long note. She rarely needs long notes.",
]

DEDUCTION = [
    "{suspect} rises in her estimation. Not fondly.",
    "The evidence circles back to {suspect}. As she suspected it would.",
    "A {weapon} is not a weapon of impulse. This was deliberate. She respects deliberate.",
    "The {room}.of course. She wonders why it took the evidence this long to say what she already knew.",
    "She does not guess. She deduces. And she deduces {suspect}.",
    "The {weapon} implicates someone who understood exactly what they were doing. Most suspects do not.",
    "Her files on {suspect} are beginning to look rather damning. She had a feeling.",
]

FORENSICS = [
    "The pattern holds. The suspect does not yet know that she has seen it.",
    "Cross-referencing. She does this the way other people breathe.automatically, and without congratulating herself.",
    "Everything points somewhere. She follows the finger while everyone else stares at it.",
    "The forensic picture is forming. It is not a flattering portrait. It was never going to be.",
]

ACCUSATION = (
    "Her conclusion is not a guess. It is a certainty assembled from evidence, "
    "from observation, and from forty years of understanding what people do "
    "when they believe no one is watching. "
    "{suspect}, with the {weapon}, in the {room}. "
    "She is rarely wrong. She is not wrong now."
)


def intro():
    return random.choice(INTRO)

def on_observation(objects):
    if not objects:
        return "Nothing of note in the immediate frame. She continues. Patience is not a virtue to her.it is a tool."
    line = random.choice(OBSERVATION)
    return line.format(obj=objects[0])

def on_room_deduction(room):
    line = random.choice(ROOM_DEDUCTION)
    return line.format(room=room)

def on_deduction(suspect, weapon, room):
    line = random.choice(DEDUCTION)
    return line.format(suspect=suspect, weapon=weapon, room=room)

def on_forensics():
    return random.choice(FORENSICS)

def on_accusation(suspect, weapon, room):
    return ACCUSATION.format(suspect=suspect, weapon=weapon, room=room)


class LLMNarrator:
    """
    Qwen2.5-0.5B. Small enough to fit on a laptop. Opinionated enough to play Inspector Liddy.
    If it fails to load, she falls back to templates and no one is the wiser.
    """
    def __init__(self):
        self.model     = None
        self.tokenizer = None
        self.available = False
        self._load()

    def _load(self):
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            model_id = "Qwen/Qwen2.5-0.5B-Instruct"
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float32)
            self.model.eval()
            self.available = True
        except Exception:
            # Templates it is. Inspector Liddy would not approve of the fallback. She uses it anyway.
            self.available = False

    def speak(self, evidence_summary):
        if not self.available:
            return None

        prompt = (
            "You are Inspector Liddy, a sharp Victorian woman detective, brilliant and sardonic. "
            "Given the following evidence, write exactly 2 short sentences in her voice. "
            "She speaks in the third person, present tense, dry and precise. No em dashes. No pleasantries.\n\n"
            f"Evidence: {evidence_summary}\n\nInspector Liddy:"
        )

        try:
            import torch
            inputs = self.tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=80,
                    do_sample=True,
                    temperature=0.75,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            text = self.tokenizer.decode(output[0], skip_special_tokens=True)
            generated = text[len(prompt):].strip()
            sentences = [s.strip() for s in generated.split(".") if s.strip()]
            return ". ".join(sentences[:2]) + "." if sentences else None
        except Exception:
            return None
