# app/utils/validators.py

import re
import validators # This library is in your requirements.txt

def validate_email(email):
    """
    Validates an email address format.
    Uses the 'validators' library.
    """
    return validators.email(email)

def validate_password(password):
    """
    Validates password strength.
    Requires at least 8 characters, one uppercase, one lowercase, one digit, one special character.
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False # No uppercase
    if not re.search(r"[a-z]", password):
        return False # No lowercase
    if not re.search(r"\d", password):
        return False # No digit
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False # No special character
    return True

# Add more validators as needed (e.g., validate_phone_number, validate_name)
