EFFECT_HANDLERS = {}

def register_effect(name : str):
    def decorator(func):
        EFFECT_HANDLERS[name] = func
        return func
    return decorator