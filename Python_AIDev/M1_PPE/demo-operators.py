print("=== 1. ARITHMETIC: LLM cost calculator ===")
input_tokens = 1500
output_tokens = 500
price_per_million_input = 3.0     # dollars (example numbers)
price_per_million_output = 15.0
 
cost_input = (input_tokens / 1_000_000) * price_per_million_input
cost_output = (output_tokens / 1_000_000) * price_per_million_output
cost_one_call = cost_input + cost_output
print(f"Cost of ONE call      : ${cost_one_call:.6f}")
 
calls_per_day = 100_000
print(f"Cost per day (100k)   : ${cost_one_call * calls_per_day:,.2f}")
print(f"Cost per 30 days      : ${cost_one_call * calls_per_day * 30:,.2f}")
 
print()
print("Other arithmetic friends:")
total_docs = 1000
batch_size = 64
print("Full batches  (//)    :", total_docs // batch_size)
print("Left over     (%)     :", total_docs % batch_size)
print("Power         (**)    : 2 ** 10 =", 2 ** 10, " <- why GPUs love powers of 2")
"""A beginner-friendly tour of Python operators.

Run this file to see how operators can help an AI app estimate costs,
check confidence, choose a response, check language support, and count tokens.
"""

print("PYTHON OPERATORS: HOW AN AI APP THINKS")
print("=" * 42)

# 1. Arithmetic: calculate an estimated request cost.
print("\n1) ARITHMETIC")
input_tokens = 800
output_tokens = 200
cost_per_1000_tokens = 0.02
total_tokens = input_tokens + output_tokens       # + adds
remaining_tokens = 1500 - total_tokens            # - subtracts
estimated_cost = total_tokens / 1000 * cost_per_1000_tokens  # / divides
whole_groups = total_tokens // 1000               # // gives whole groups
extra_tokens = total_tokens % 1000                 # % gives the remainder
double_cost = estimated_cost ** 2                 # ** raises to a power
print(f"Tokens used: {input_tokens} + {output_tokens} = {total_tokens}")
print(f"Estimated cost: ${estimated_cost:.3f}")
print(f"Tokens left: {remaining_tokens}; full groups of 1,000: {whole_groups}")
print(f"Remainder: {extra_tokens}; cost squared (just a demo): {double_cost:.6f}")

# 2. Comparisons: compare model confidence with a minimum target.
print("\n2) COMPARISON")
confidence = 0.82
minimum_confidence = 0.80
print(f"Confidence: {confidence}; minimum: {minimum_confidence}")
print("confidence == minimum:", confidence == minimum_confidence)  # equal?
print("confidence != minimum:", confidence != minimum_confidence)  # different?
print("confidence > minimum:", confidence > minimum_confidence)
print("confidence < minimum:", confidence < minimum_confidence)
print("confidence >= minimum:", confidence >= minimum_confidence)
print("confidence <= minimum:", confidence <= minimum_confidence)

# 3. Logical operators: combine conditions to decide what the app should do.
print("\n3) LOGICAL")
is_safe = True
is_confident = confidence >= minimum_confidence
if is_safe and is_confident:
	print("Send the reply: it is safe AND confident enough.")
elif not is_safe or not is_confident:
	print("Ask a human: it is unsafe OR not confident enough.")

# 4. Membership: check whether a requested language is supported.
print("\n4) MEMBERSHIP")
supported_languages = ["English", "Spanish", "French"]
requested_language = "Spanish"
print("Supported languages:", supported_languages)
print(requested_language, "in supported languages:", requested_language in supported_languages)
print("German not in supported languages:", "German" not in supported_languages)

# 5. Assignment: update a running token count.
print("\n5) ASSIGNMENT")
running_token_count = 0
running_token_count = input_tokens  # = sets a value
running_token_count += output_tokens  # += adds and saves the result
running_token_count -= 50  # -= subtracts and saves the result
print("Running token count after input, output, and a 50-token adjustment:", running_token_count)

print("\nTry changing the numbers and words above, then run the file again.")
