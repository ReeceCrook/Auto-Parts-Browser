import time

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f'Task {func.__name__} took {elapsed:.2f} seconds')
        return result
    return wrapper
