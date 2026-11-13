# LifeTel Telecom - Secure Reference ID Verification System

import string

# Characters allowed for encryption and decryption
CHARACTERS = string.ascii_letters + string.digits + "!@#$%^&*-_"
SHIFT = 7  # Caesar cipher shift value


def is_valid_reference_id(reference_id):
    """
    Check whether the Reference ID is valid:
    - Must be exactly 12 characters
    - Must contain only letters and numbers
    """
    if len(reference_id) != 12:
        return False

    return reference_id.isalnum()


def encrypt_reference_id(reference_id):
    """
    Encrypt the Reference ID using a Caesar cipher.
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
    Decrypt an encrypted Reference ID.
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
    print("===== LifeTel Telecom SIM Verification =====")
    reference_id = input("Enter your 12-character Reference ID: ").strip()

    if not is_valid_reference_id(reference_id):
        print("Invalid Reference ID.")
        print("It must be exactly 12 characters and contain only letters and numbers.")
        return

    encrypted_id = encrypt_reference_id(reference_id)

    print("\nReference ID verified successfully.")
    print(f"Original Reference ID:  {reference_id}")
    print(f"Encrypted Reference ID: {encrypted_id}")

    decrypt_option = input("\nDo you want to decrypt it? (yes/no): ").strip().lower()

    if decrypt_option == "yes":
        decrypted_id = decrypt_reference_id(encrypted_id)
        print(f"Decrypted Reference ID: {decrypted_id}")
    else:
        print("Decryption skipped.")


if __name__ == "__main__":
    main()