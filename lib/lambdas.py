from pathlib import Path

from aws_cdk import Duration
from aws_cdk.aws_lambda import Code, Function, LayerVersion, Runtime

DEFAULT_RUNTIME = 'PYTHON_3_14'

def valid_runtime(runtime: str) -> bool:
    try:
        Runtime.from

def create_lambda(self, layers: list[LayerVersion] = [], **kwargs) -> Function:
    lambda_name = kwargs.get('lambda_name')
    handler = kwargs.get('handler')
    source_dir = kwargs.get('source_dir')
    runtime = kwargs.get('runtime', DEFAULT_RUNTIME)
    timeout = kwargs.get('timeout', 5)
    environment = kwargs.get('environment')

    if len(layers) > 0:
        for layer in layers:
            if not isinstance(layer, LayerVersion):
                raise TypeError('layers must be of type LayerVersion')

    if not lambda_name or not isinstance(lambda_name, str):
        raise TypeError('lambda_name must be provided and be of type str.')

    if not handler or not isinstance(handler, str):
        raise TypeError('handler must be provided and be of type str.')

    if not source_dir or not isinstance(source_dir, str):
        raise TypeError('source_dir must be provided and be of type str.')

    source_path = Path(source_dir)

    if not source_path.is_dir():
        raise ValueError('source_dir is not a valid, relative directory.')

    if not isinstance(runtime, str):
        raise TypeError('runtime must be provided and be of type string.')

    if not Runtime.is_
        raise ValueError('Supplied runtime is not a valid Runtime.')

    if not isinstance(timeout, int):
        raise TypeError('timeout is not of type int.')

    if 0 > timeout > 900:
        raise ValueError('timeout must be > 0 and less than 900 seconds.')

    if not isinstance(environment, dict):
        raise TypeError('environment must be of type dict.')

    return Function(
        self,
        lambda_name,
        function_name=lambda_name,
        handler=handler,
        runtime=Runtime[runtime],
        code=Code.from_asset(path=source_dir),
        timeout=Duration.seconds(timeout),
        layers=layers,
    )
