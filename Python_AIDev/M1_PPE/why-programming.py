import time
 
# ---------------------------------------------------------------
# STEP 1: The data (in real life this comes from a database / file)
# ---------------------------------------------------------------
reviews = [
    "Loved the product, amazing quality",
    "Worst delivery ever, very disappointed",
    "Great value, will buy again",
    "Terrible packaging and bad support",
    "Excellent service, super happy",
    "Not good, the item was broken",
    "Fantastic experience, loved it",
    "Awful quality, waste of money"
]
 
happy_words = ["loved", "amazing", "great", "excellent", "happy", "fantastic"]
angry_words = ["worst", "disappointed", "terrible", "bad", "broken", "awful", "waste"]
# ---------------------------------------------------------------
# STEP 2: Teach the computer ONE simple rule, then let it repeat
# ---------------------------------------------------------------
happy_count = 0
angry_count = 0
 
for review in reviews:                 # "for every review in my list..."
    text = review.lower()
    is_happy = False
    is_angry = False
 
    for word in happy_words:
        if word in text:
            is_happy = True
    for word in angry_words:
        if word in text:
            is_angry = True
 
    if is_happy and not is_angry:
        happy_count = happy_count + 1
        print(f"HAPPY  -> {review}")
    else:
        angry_count = angry_count + 1
        print(f"ANGRY  -> {review}")
 
print()
print(f"Result: {happy_count} happy customers, {angry_count} angry customers")