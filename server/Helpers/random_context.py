import random
from fake_useragent import UserAgent

def get_random_context_params():
    try:
        ua = UserAgent()
        user_agent = ua.random
    except Exception as e:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                     "(KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"

    viewport = {
        "width": random.choice([1280, 1366, 1440, 1600, 1920]),
        "height": random.choice([720, 768, 900, 1080])
    }
    return user_agent, viewport
