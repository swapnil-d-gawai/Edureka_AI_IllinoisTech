import re

#------------------------------
# The Assistant's information
#------------------------------
assistant = {
	"name": "HelpBuddy",
    "version": "1.0",
    "price_per_token": 0.00004
}

positive_words = ["awesome", "good", "great", "happy", "love", "perfect", "thanks","excellent", "helpful", "satisfied","fantastic", "wonderful", "amazing", "brilliant", "delightful", "joyful", "pleased", "content", "cheerful", "optimistic"]
negative_words = ["angry", "bad", "broken", "disappointed", "frustrated", "hate","issue", "problem", "terrible", "unacceptable", "upset", "wrong","awful", "dreadful", "horrible", "miserable", "unhappy", "unfortunate","regretful", "resentful", "sorrowful"]

#------------------------------
# Talk to the human user
#------------------------------
print(f"Hello! I am {assistant['name']} (version {assistant['version']}). How can I assist you today?")
user_name = input("What is your name? ")
message = input(f"Hi {user_name}, tell me about your experience with our product. ").strip()

#------------------------------
# Analyze the message
#------------------------------
text = message.lower()
tokens = re.findall(r"[a-z]+", text)
positive_count = sum(word in positive_words for word in tokens)
negative_count = sum(word in negative_words for word in tokens)

if positive_count > negative_count:
    sentiment = "positive"
elif negative_count > positive_count:
    sentiment = "negative"
else:
    sentiment = "neutral"

print(f"Your message sentiment is: {sentiment}")