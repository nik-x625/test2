import random
import string

def build_token(n):
    char_set = string.ascii_uppercase + string.digits + string.ascii_lowercase
    return ''.join(random.sample(char_set*n, n))