# model.py
import json
import pickle
import random
from pathlib import Path
from typing import Dict, List

class VocabularyModel:
    """
    Q-learning (contextual bandit-style) for hint selection per word.

    - Q[(word_id)][hint_type] = confidence this hint helps on this word
    - update(): Q <- Q + alpha * (reward - Q)     (bandit form; gamma not used)
    - get_best_hint_for_word(): epsilon-greedy using `exploration_rate`
    - get_ranked_hints_for_word(): sorted by Q with a small exploration bump
    """

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.root = self.config_path.parent

        # ---- load config ----
        with open(self.config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        self.words_file: str = cfg.get("words_file", "words.json")
        self.hint_types: List[str] = cfg.get("hint_types", ["dialogue","context","story","gif"])

        # hyperparameters (use your keys)
        self.alpha: float = float(cfg.get("alpha", 0.05))
        self.gamma: float = float(cfg.get("gamma", 0.0))  # kept for future use
        self.epsilon: float = float(cfg.get("exploration_rate", 0.2))
        self.initial_q: float = float(cfg.get("initial_q_value", 0.1))

        rewards_cfg = cfg.get("rewards", {"correct": 1.0, "incorrect": -0.5})
        self.reward_correct: float = float(rewards_cfg.get("correct", 1.0))
        self.reward_incorrect: float = float(rewards_cfg.get("incorrect", -0.5))

        # persistence (pickle)
        self.q_path = self.root / cfg.get("q_table_file", "q_table.pkl")
        self.q: Dict[str, Dict[str, float]] = self._load_q_table(self.q_path)

        # optional words (not required for learning; helpful for sanity)
        words_path = self.root / self.words_file
        try:
            with open(words_path, "r", encoding="utf-8") as f:
                self.words = json.load(f)  # dict keyed by "1","2",...
        except Exception:
            self.words = {}

    # ---------- persistence ----------
    def _load_q_table(self, path: Path) -> Dict[str, Dict[str, float]]:
        if path.exists():
            try:
                with open(path, "rb") as f:
                    data = pickle.load(f)
                # ensure floats and ensure all hint keys exist
                for wid, row in data.items():
                    for h in list(row.keys()):
                        row[h] = float(row[h])
                return data
            except Exception:
                pass
        return {}  # start empty

    def save_q_table(self) -> None:
        self.q_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.q_path, "wb") as f:
            pickle.dump(self.q, f)

    # ---------- helpers ----------
    def _key(self, word_id: int) -> str:
        return str(int(word_id))

    def _ensure_row(self, word_id: int) -> Dict[str, float]:
        k = self._key(word_id)
        if k not in self.q:
            self.q[k] = {h: float(self.initial_q) for h in self.hint_types}
        else:
            # add newly-configured hint types if missing
            for h in self.hint_types:
                self.q[k].setdefault(h, float(self.initial_q))
        return self.q[k]

    # ---------- API used by server.py ----------
    def get_best_hint_for_word(self, word_id: int) -> str:
        """
        Epsilon-greedy: with prob epsilon (exploration_rate) pick random hint,
        else choose argmax Q for this word.
        """
        row = self._ensure_row(word_id)

        # exploration
        if random.random() < self.epsilon:
            return random.choice(self.hint_types)

        # exploitation (break ties randomly)
        max_q = max(row[h] for h in self.hint_types)
        best = [h for h in self.hint_types if row[h] == max_q]
        return random.choice(best)

    def get_ranked_hints_for_word(self, word_id: int) -> List[str]:
        """
        Rank by descending Q; with small chance, promote a lower item
        to encourage exploration in list displays.
        """
        row = self._ensure_row(word_id)
        ranked = sorted(self.hint_types, key=lambda h: row[h], reverse=True)

        # small exploration bump (epsilon/2)
        if random.random() < (self.epsilon * 0.5) and len(ranked) > 1:
            j = random.randrange(1, len(ranked))
            ranked[0], ranked[j] = ranked[j], ranked[0]
        return ranked

    def update(self, word_id: int, hint_type: str, is_correct: bool) -> None:
        """
        Contextual bandit update:
            Q <- Q + alpha * (reward - Q)
        reward = rewards.correct if is_correct else rewards.incorrect (can be negative)
        """
        row = self._ensure_row(word_id)
        if hint_type not in row:
            row[hint_type] = float(self.initial_q)

        reward = self.reward_correct if is_correct else self.reward_incorrect
        old_q = row[hint_type]

        # bandit-style target (gamma unused here; left for future multi-step extensions)
        target = reward
        new_q = old_q + self.alpha * (target - old_q)
        row[hint_type] = float(new_q)
