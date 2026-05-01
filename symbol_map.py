# Symbol label → (suggested_action, reward_value)
SYMBOL_MAP = {
    "arrow_forward":  ("forward",  0),
    "arrow_left":     ("left",     0),
    "arrow_right":    ("right",    0),
    "arrow_back":     ("backward", 0),
    "reward_gold":    ("forward",  +10),
    "reward_silver":  ("forward",  +5),
    "penalty_trap":   ("stop",     -5),
    "goal":           ("stop",     +100),
    "wall":           ("backward", -1),
    "unknown":        (None,        0),   # RL agent decides
}
