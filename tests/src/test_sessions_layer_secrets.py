import sys

import boto3
import pytest
from moto import mock_aws
from types_boto3_secretsmanager.client import SecretsManagerClient


@pytest.fixture(scope='function')
def invitation_secret(aws_credentials):
    """Provide Secrets Manager client with a predefined invitation secret"""
    with mock_aws():
        sm_client = boto3.client(
            service_name='secretsmanager', region_name='eu-west-1'
        )
        sm_client.create_secret(
            Name='league/invitation_key', SecretString='CorrectValue'
        )
        yield sm_client


@pytest.mark.registration
def test_invitation_key_import(
    invitation_secret: SecretsManagerClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test valid_invitation_key returns True when valid key provided"""
    monkeypatch.setenv('INVITE_KEY', 'league/invitation_key')
    monkeypatch.setenv('REGION', 'eu-west-1')

    import layers.sessions.python.league.aws_secrets as aws_secrets

    assert aws_secrets.INVITE_SECRET == 'CorrectValue'


@pytest.mark.registration
def test_invitation_import_env_missing_region(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test valid_invitation_key returns True when valid key provided"""

    with pytest.raises(RuntimeError) as exc_info:
        sys.modules.pop('layers.sessions.python.league.aws_secrets', None)
        monkeypatch.setenv('INVITE_KEY', 'league/invitation_key')
        from layers.sessions.python.league.aws_secrets import INVITE_SECRET

        print(INVITE_SECRET)  #  Ruff check fudge

    assert exc_info.type is RuntimeError
    assert (
        exc_info.value.args[0] == 'Environment variable AWS_REGION is not set.'
    )


@pytest.mark.registration
def test_invitation_import_env_missing_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test valid_invitation_key returns True when valid key provided"""

    with pytest.raises(RuntimeError) as exc_info:
        sys.modules.pop('layers.sessions.python.league.aws_secrets', None)
        monkeypatch.setenv('REGION', 'eu-west-1')
        from layers.sessions.python.league.aws_secrets import INVITE_SECRET

        print(INVITE_SECRET)  #  Ruff check fudge

    assert exc_info.type is RuntimeError
    assert (
        exc_info.value.args[0] == 'Environment variable INVITE_KEY is not set.'
    )
