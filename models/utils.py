def isunsignedint(value):
    if not isinstance(value, int):
        return False
    if value < 1:
        return False
    return True
