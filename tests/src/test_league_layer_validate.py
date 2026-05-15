import pytest

from layers.league.python.league.validate import (
    valid_player_id,
    valid_psn_id,
    valid_xbox_id,
)

CROSS_PLATFORM_INVALID_IDS = [
    ('', False),
    ('No', False),
    ('Invalid+plyr', False),
    ('Invalid&plyr', False),
    ('Invalid@plyr', False),
    ('Invalid#plyr', False),
    ('Invalid*plyr', False),
    ('Invalid=plyr', False),
    ('2not_allowed', False),
]

PSN_INVALID_IDS = [('Invalid space', False), ('Longer_than_16___', False)]

XBOX_INVALID_IDS = [
    ('Invalid_plyr', False),
    ('Invalid-plyr', False),
    ('Too long 1234', False),
]

CROSS_PLATFORM_VALID_IDS = [
    ('Val', True),
    ('V12', True),
    ('val', True),
    ('Valid1234ply', True),
]

PSN_VALID_IDS = [
    ('Valid_player1', True),
    ('valid_player2', True),
    ('Valid-player3', True),
    ('valid-player4', True),
]

XBOX_VALID_IDS = [('Valid player', True), ('valid player', True)]

PASSWORD_VARIATIONS = [
    ('tooshort', 'PlayerOne', False),
    ('missing_upper_number', 'PlayerOne', False),
    ('Missing_number', 'PlayerOne', False),
    ('missing_upper1', 'PlayerOne', False),
    ('PlayerOne123', 'PlayerOne', False),
    ('playerone1a', 'PlayerOne', False),
    ('PLAYERONE1a', 'PlayerOne', False),
]


@pytest.mark.parametrize(
    'player_id, expected_result', CROSS_PLATFORM_INVALID_IDS + PSN_INVALID_IDS
)
@pytest.mark.validation
def test_valid_psn_id_invalid_ply(
    player_id: str, expected_result: bool
) -> None:
    """Test all PSN ID character restrictions are enforced"""

    assert valid_psn_id(player_id) is expected_result


@pytest.mark.parametrize(
    'player_id, expected_result', CROSS_PLATFORM_INVALID_IDS + XBOX_INVALID_IDS
)
@pytest.mark.validation
def test_valid_xbox_id_invalid_ply(
    player_id: str, expected_result: bool
) -> None:
    """Test all Xbox Gamer Tag character restrictions are enforced"""

    assert valid_xbox_id(player_id) is expected_result


@pytest.mark.parametrize(
    'player_id, expected_result', CROSS_PLATFORM_VALID_IDS + PSN_VALID_IDS
)
@pytest.mark.validation
def test_valid_psn_id_valid_ply(player_id: str, expected_result: bool) -> None:
    """Test valid PSN IDs are accepted"""

    assert valid_psn_id(player_id) is expected_result


@pytest.mark.parametrize(
    'player_id, expected_result', CROSS_PLATFORM_VALID_IDS + XBOX_VALID_IDS
)
@pytest.mark.validation
def test_valid_xbox_id_valid_ply(
    player_id: str, expected_result: bool
) -> None:
    """Test valid Xbox Gamer Tags are accepted"""

    assert valid_xbox_id(player_id) is expected_result


@pytest.mark.parametrize(
    'player_id, expected_result',
    CROSS_PLATFORM_VALID_IDS + PSN_VALID_IDS + XBOX_VALID_IDS,
)
@pytest.mark.validation
def test_valid_player_id_valid_ply(
    player_id: str, expected_result: bool
) -> None:
    """Test both valid PSN and Xbox player Ids return True"""

    assert valid_player_id(player_id) is expected_result


@pytest.mark.parametrize(
    'player_id, expected_result', CROSS_PLATFORM_INVALID_IDS
)
@pytest.mark.validation
def test_valid_player_id_invalid_ply(
    player_id: str, expected_result: bool
) -> None:
    """Test both invalid PSN and Xbox player Ids return False"""

    assert valid_player_id(player_id) is expected_result


@pytest.mark.parametrize(
    'password, player, expected_result', PASSWORD_VARIATIONS
)
@pytest.mark.validation
def test_password_meets_criteria(
    password: str,
    player: str,
    expected_result: bool,
) -> None:
    """Tests to make sure supplied password conforms to defined standard"""

    from layers.league.python.league.validate import (
        password_meets_criteria,
    )

    assert password_meets_criteria(password, player) is expected_result
