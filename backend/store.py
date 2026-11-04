import json
import threading
from pathlib import Path
from config import DB_FILE

_lock = threading.Lock()
_DEFAULT = {'users': [], 'activities': [], 'files': [], 'questions': [], 'logs': []}

def read_db():
    with _lock:
        if not DB_FILE.exists():
            DB_FILE.write_text(json.dumps(_DEFAULT, indent=2), encoding='utf-8')
        try:
            return json.loads(DB_FILE.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            return {k: list(v) for k, v in _DEFAULT.items()}

def write_db(data):
    with _lock:
        temp = DB_FILE.with_suffix('.tmp')
        temp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        temp.replace(DB_FILE)

def next_id(items, key):
    return max((int(x.get(key, 0)) for x in items), default=0) + 1
