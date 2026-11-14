import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError as e:
        logging.error("Division by zero error: %s", e)
        return None
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        return None
    else:
        logging.info("Division successful: %s / %s = %s", a, b, result)
        return result

if __name__ == "__main__":
    divide(10, 2)
    divide(10, 0)
    divide("10", 2)