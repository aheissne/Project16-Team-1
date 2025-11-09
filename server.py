# server.py
# Minimal API to serve GIF hints + collect outcomes.
# - Uses sponsor Q-learning model if available (model.VocabularyModel)
# - Falls back to a simple policy if the model can't be imported yet

import json
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

# ---------- Config / data ----------
ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CFG = json.load(f)

WORDS_PATH = ROOT / CFG.get("words_file", "words.json")
with open(WORDS_PATH, "r", encoding="utf-8") as f:
    WORDS = json.load(f)  # dict keyed by string ids "1","2",...

HINT_TYPES = CFG.get("hint_types", ["gif"])  # e.g., ["gif"] or ["gif_a","gif_b","gif_c"]

# ---------- Try to load sponsor model (optional) ----------
QMODEL = None
try:
    # Your sponsor's model; adjust import if the class is elsewhere
    from model import VocabularyModel  # noqa: E402

    QMODEL = VocabularyModel(config_path=str(CONFIG_PATH))
except Exception as e:
    print("[server] Q-learning model not loaded, using fallback.", e)

# ---------- App ----------
app = Flask(__name__)
CORS(app)  # allow browser calls from your pages

def _normalize_word_id(word_id):
    # We store keys as strings in words.json
    return str(int(word_id))

def _available_hint_types_for_word(word_id):
    """Return which hint keys exist for this word, filtered by CFG['hint_types']."""
    w = WORDS.get(_normalize_word_id(word_id), {})
    hints = (w.get("hints") or {})
    # Keep only those keys that appear in config hint types
    avail = [h for h in HINT_TYPES if h in hints]
    # If none matched, try common 'gif' key as a default
    if not avail and "gif" in hints:
        avail = ["gif"]
    return avail

def _best_hint_type(word_id):
    """Choose a hint type using Q-model if available; else fallback to first available."""
    avail = _available_hint_types_for_word(word_id)
    if not avail:
        return None
    if QMODEL:
        # Ask the model which hint to use, but clamp to available set for this word
        try:
            ht = QMODEL.get_best_hint_for_word(int(word_id))
            if ht in avail:
                return ht
        except Exception as e:
            print("[server] QMODEL.get_best_hint_for_word failed, fallback.", e)
    # Fallback: pick the first configured/available hint
    return avail[0]

def _hint_payload(word_id, hint_type):
    """Return the actual GIF URL/path for the chosen hint type."""
    w = WORDS.get(_normalize_word_id(word_id), {})
    hints = (w.get("hints") or {})
    return {
        "word": w.get("word"),
        "hint_type": hint_type,
        "gif_url": hints.get(hint_type) or hints.get("gif")  # safest default
    }

@app.post("/get_best_hint_type")
def get_best_hint_type():
    data = request.get_json(force=True) or {}
    word_id = data.get("word_id")
    if word_id is None:
        return jsonify({"error": "word_id required"}), 400

    hint_type = _best_hint_type(word_id)
    if not hint_type:
        return jsonify({"error": "No hint available for this word"}), 404

    return jsonify(_hint_payload(word_id, hint_type))

@app.post("/get_ranked_hint_type")
def get_ranked_hint_type():
    data = request.get_json(force=True) or {}
    word_id = data.get("word_id")
    if word_id is None:
        return jsonify({"error": "word_id required"}), 400

    # If model can rank, use it; else just return available list
    if QMODEL:
        try:
            ranked = QMODEL.get_ranked_hints_for_word(int(word_id))
            # Keep only those that exist for this word
            ranked = [r for r in ranked if r in _available_hint_types_for_word(word_id)]
            if ranked:
                return jsonify({"ranked_hint_types": ranked})
        except Exception as e:
            print("[server] QMODEL.get_ranked_hints_for_word failed, fallback.", e)

    return jsonify({"ranked_hint_types": _available_hint_types_for_word(word_id)})

@app.post("/update_model")
def update_model():
    data = request.get_json(force=True) or {}
    word_id = data.get("word_id")
    hint_type = data.get("hint_type")
    is_correct = bool(data.get("is_correct", False))

    if word_id is None or not hint_type:
        return jsonify({"error": "word_id and hint_type required"}), 400

    if QMODEL:
        try:
            QMODEL.update(word_id=int(word_id), hint_type=hint_type, is_correct=is_correct)
            QMODEL.save_q_table()
        except Exception as e:
            print("[server] QMODEL.update/save failed (continuing).", e)

    # Even if Q-model is absent, we accept the call (so your UI flow never breaks)
    return jsonify({"ok": True})

if __name__ == "__main__":
    # pip install flask flask-cors
    app.run(host="0.0.0.0", port=5001, debug=True)
