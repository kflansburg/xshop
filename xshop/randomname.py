"""
RandomName Module

    Generates random names for folders and containers and images to
    allow parallel testing.
"""

import random
import string

def generate():
    return ''.join(random.choice(string.ascii_lowercase) for i in range(10))
