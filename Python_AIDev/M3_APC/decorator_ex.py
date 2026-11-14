import time


def log_request(func):
    def wrapper(prompt):
        print(f"User: {prompt}")
        start = time.time()

        result = func(prompt)

        print(f"Time: {time.time() - start:.2f}s")
        return result

    return wrapper


@log_request
def ask_ai(prompt):
    return f"AI: {prompt}"


print(ask_ai("What is AI?"))