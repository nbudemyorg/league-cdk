import bcrypt


def generate_password_hash(supplied_password: str) -> str:
    """Generates a bcrypt hash with salt of the supplied password"""

    password_bytes = supplied_password.encode('utf-8')
    password_salt = bcrypt.gensalt()

    password_bytes = bcrypt.hashpw(password_bytes, password_salt)

    return password_bytes.decode()
