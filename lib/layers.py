import subprocess
from pathlib import Path

from aws_cdk.aws_lambda import Code, LayerVersion


def create_lambda_layer(
    self, stack_name: str, layer_name: str, layer_source: str
) -> LayerVersion:

    layer_id = f'{stack_name}-{layer_name}-dependencies'

    supplied_path = Path(layer_source)

    if supplied_path.is_file():
        output_dir = './build'
        subprocess_string = (
            f'pip install -r {layer_source} -t {output_dir}/python'
        )
        subprocess.check_call(subprocess_string.split())
        layer_code = Code.from_asset(output_dir)

    elif supplied_path.is_dir():
        layer_code = Code.from_asset(layer_source)

    else:
        raise ValueError('Path supplied must be to a valid file or directory.')

    return LayerVersion(
        self,
        id=layer_id,
        code=layer_code,
    )
