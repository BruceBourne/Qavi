import hashlib

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def verify_pw(plain, hashed):
    return hash_pw(plain) == hashed
