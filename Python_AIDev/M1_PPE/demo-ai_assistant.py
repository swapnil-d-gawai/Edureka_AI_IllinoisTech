"""A small rule-based assistant demonstrating input, processing, decisions, and output."""

import re


HAPPY_WORDS = {
	"awesome", "good", "great", "happy", "love", "perfect", "thanks",
	"thank", "wonderful", "excellent", "helpful", "satisfied",
}
ANGRY_WORDS = {
	"angry", "bad", "broken", "disappointed", "frustrated", "hate",
	"issue", "problem", "terrible", "unacceptable", "upset", "wrong",
}
ESCALATION_WORDS = {
	"cancel", "chargeback", "complaint", "lawsuit", "manager", "refund",
	"urgent",
}

# Example prices in USD per million tokens, used only for an illustrative estimate.
INPUT_PRICE_PER_MILLION = 0.15
OUTPUT_PRICE_PER_MILLION = 0.60


def estimate_tokens(text):
	"""Approximate token count by counting words; this is not a tokenizer."""
	return len(re.findall(r"\b[\w'-]+\b", text))


def respond(message):
	"""Return a mood/escalation decision, reply, token counts, and estimated cost."""
	words = re.findall(r"\b[\w'-]+\b", message.lower())
	word_set = set(words)
	happy_score = sum(word in HAPPY_WORDS for word in words)
	angry_score = sum(word in ANGRY_WORDS for word in words)

	if word_set & ESCALATION_WORDS:
		decision = "ESCALATE"
		reply = "I'll pass this to a support specialist so they can help you directly."
	elif angry_score > happy_score:
		decision = "ANGRY"
		reply = "I'm sorry this has been frustrating. Tell me a little more so I can help."
	elif happy_score:
		decision = "HAPPY"
		reply = "I'm glad to hear that! What else can I help you with?"
	else:
		decision = "NEUTRAL"
		reply = "Thanks for reaching out. How can I help you?"

	input_tokens = estimate_tokens(message)
	output_tokens = estimate_tokens(reply)
	cost = (
		input_tokens * INPUT_PRICE_PER_MILLION
		+ output_tokens * OUTPUT_PRICE_PER_MILLION
	) / 1_000_000
	return decision, reply, input_tokens, output_tokens, cost


def main():
	print("Mini AI Assistant — type 'quit' to exit.")
	print("This demo uses keyword rules; token counts and costs are illustrative.\n")

	while True:
		try:
			message = input("You: ").strip()
		except (EOFError, KeyboardInterrupt):
			print("\nGoodbye!")
			break

		if message.lower() in {"quit", "exit", "q"}:
			print("Goodbye!")
			break
		if not message:
			print("Please enter a message.\n")
			continue

		decision, reply, input_tokens, output_tokens, cost = respond(message)
		print(f"Decision: {decision}")
		print(f"Assistant: {reply}")
		print(
			f"Estimated usage: {input_tokens} input + {output_tokens} output tokens "
			f"| estimated cost: ${cost:.8f}\n"
		)


if __name__ == "__main__":
	main()
