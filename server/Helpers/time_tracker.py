import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        if isinstance(result, dict):
            result["overall_time"] = f"{elapsed:.2f}"
            return result
        return {"result": result, "overall_time": f"{elapsed:.2f}"}
    return wrapper
