import random
import json
from config import LEARNING_RATE, DISCOUNT, EPSILON

ACTIONS = ["forward", "left", "right", "backward"]

class QLearningAgent:
    def __init__(self, q_table_path="q_table.json"):
        self.q_table_path = q_table_path
        self.q_table = self._load()

    def _load(self):
        try:
            with open(self.q_table_path) as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save(self):
        with open(self.q_table_path, "w") as f:
            json.dump(self.q_table, f)

    def _get_q(self, state, action):
        return self.q_table.get(state, {}).get(action, 0.0)

    def choose_action(self, state, suggested_action=None):
        """Epsilon-greedy, but bias toward the symbol's suggestion."""
        if suggested_action and random.random() > EPSILON:
            return suggested_action                      # follow the symbol
        if random.random() < EPSILON:
            return random.choice(ACTIONS)               # explore
        # Exploit: pick best known action
        q_vals = {a: self._get_q(state, a) for a in ACTIONS}
        return max(q_vals, key=q_vals.get)

    def update(self, state, action, reward, next_state):
        current_q = self._get_q(state, action)
        max_next_q = max(self._get_q(next_state, a) for a in ACTIONS)
        new_q = current_q + LEARNING_RATE * (reward + DISCOUNT * max_next_q - current_q)

        if state not in self.q_table:
            self.q_table[state] = {}
        self.q_table[state][action] = new_q
