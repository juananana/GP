import os
import pickle
import tempfile

def load_blob(path):
    return pickle.load(open(path, "rb"))  # [C12] unsafe pickle load

def open_cache(path):
    os.chmod(path, 0o777)  # [C13] world writable cache

def parse_rule(expr):
    return eval(expr)  # [C14] eval on rule expression

def write_temp(data):
    tmp = tempfile.NamedTemporaryFile(delete=False)  # [C15] temp file not cleaned
    tmp.write(data)
    return tmp.name
