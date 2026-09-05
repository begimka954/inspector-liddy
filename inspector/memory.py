from collections import deque, Counter

class Memory:
    # A deque because memory, like Inspector Liddy's patience with incompetence,
    # has a hard and well-considered limit.
    def __init__(self, short_term_size=10):
        self.short_term = deque(maxlen=short_term_size)
        self.long_term  = []

    def remember(self, entry):
        # She remembers everything. This remembers the last ten. There is a gap between them.
        self.short_term.append(entry)
        self.long_term.append(entry)

    def recent(self, n=5):
        return list(self.short_term)[-n:]

    def all_entries(self):
        return list(self.long_term)

    def weapons_seen(self):
        return [e["weapon"] for e in self.long_term if e.get("weapon")]

    def most_seen_weapon(self):
        seen = self.weapons_seen()
        if not seen:
            return None
        return Counter(seen).most_common(1)[0][0]

    def rooms_detected(self):
        return [e["room"] for e in self.long_term if e.get("room")]

    def most_likely_room(self):
        seen = self.rooms_detected()
        if not seen:
            return None
        return Counter(seen).most_common(1)[0][0]

    def total_suspects_spotted(self):
        return sum(e.get("suspect_count", 0) for e in self.long_term)

    def to_dict(self):
        return {
            "short_term": list(self.short_term),
            "long_term":  self.long_term,
        }
