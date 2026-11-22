"""Educational Caesar-shift demonstration, not a security or SIM-verification tool."""

import string

# Characters used by the educational shift
ASCII_ALPHANUMERIC = string.ascii_letters + string.digits
CHARACTERS = string.ascii_letters + string.digits + "!@#$%^&*-_"
SHIFT = 7  # Caesar cipher shift value


def is_valid_reference_id(reference_id):
    """
    Check whether the Reference ID is valid:
    - Must be exactly 12 characters
    - Must contain only ASCII letters and numbers
    """
    if len(reference_id) != 12:
        return False

    return all(character in ASCII_ALPHANUMERIC for character in reference_id)


def encrypt_reference_id(reference_id):
    """
    Apply an educational Caesar shift to the Reference ID.
    Letters, numbers and selected special characters are shifted.
    """
    encrypted = ""

    for character in reference_id:
        if character in CHARACTERS:
            index = CHARACTERS.index(character)
            new_index = (index + SHIFT) % len(CHARACTERS)
            encrypted += CHARACTERS[new_index]
        else:
            encrypted += character

    return encrypted


def decrypt_reference_id(encrypted_id):
    """
    Reverse the educational Caesar shift.
    """
    decrypted = ""

    for character in encrypted_id:
        if character in CHARACTERS:
            index = CHARACTERS.index(character)
            new_index = (index - SHIFT) % len(CHARACTERS)
            decrypted += CHARACTERS[new_index]
        else:
            decrypted += character

    return decrypted


def main():
    print("===== LifeTel Telecom Caesar-Shift Demo (Educational Only) =====")
    reference_id = input("Enter your 12-character Reference ID: ").strip()

    if not is_valid_reference_id(reference_id):
        print("Invalid Reference ID.")
        print("It must be exactly 12 characters and contain only ASCII letters and numbers.")
        return

    encrypted_id = encrypt_reference_id(reference_id)

    print("\nReference ID format accepted; this is not real verification.")
    print(f"Original Reference ID:  {reference_id}")
    print(f"Shifted Reference ID:   {encrypted_id}")

    decrypt_option = input("\nDo you want to decrypt it? (yes/no): ").strip().lower()

    if decrypt_option == "yes":
        decrypted_id = decrypt_reference_id(encrypted_id)
        print(f"Unshifted Reference ID: {decrypted_id}")
    else:
        print("Decryption skipped.")


if __name__ == "__main__":
    main()