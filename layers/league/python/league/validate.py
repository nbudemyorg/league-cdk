import re


def valid_player_id(supplied_id: str) -> bool:
    """Verify supplied player id conforms to either PSN or Xbox restrictions"""
    return bool(valid_psn_id(supplied_id) or valid_xbox_id(supplied_id))


def valid_psn_id(supplied_id: str) -> bool:
    """
    Does the supplied id confirm to PSN restrictions:
    Length: 3-16 characters
    Must start with a letter of the Alphabet
    Characters: Alphanumeric + underscore + hyphens, NO SPACES
    """
    expression = r'^[a-zA-Z][\w-]{2,15}$'

    return bool(re.match(expression, supplied_id))


def valid_xbox_id(supplied_id: str) -> bool:
    """
    Does the supplied id confirm to Xbox Gamertag restrictions:
    Length: 3-12 characters
    Must start with a letter of the Alphabet
    Characters: Alphanumeric + space, NO HYPHEN OR UNDERSCORE
    """
    expression = r'^[a-zA-Z][0-9a-zA-Z\s]{2,11}$'

    return bool(re.match(expression, supplied_id))


def password_meets_criteria(
    supplied_password: str, supplied_player: str
) -> bool:
    """Verifies the supplied password conforms to defined password standards"""

    if len(supplied_password) < 10:
        return False

    if re.search('[0-9]', supplied_password) is None:
        return False

    if re.search('[A-Z]', supplied_password) is None:
        return False

    return not re.search(supplied_player.lower(), supplied_password.lower())
