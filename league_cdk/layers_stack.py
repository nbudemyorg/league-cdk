from pathlib import Path

import yaml
from aws_cdk import NestedStack
from constructs import Construct

from lib import layers


class LayersStack(NestedStack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        with Path.open('./config/layers.yaml') as layers_yaml:
            layers_config = yaml.load(layers_yaml, yaml.FullLoader)

        stack_layers = {}

        for layer in layers_config['layers']:
            new_layer = layers.create_lambda_layer(
                self,
                layer_name=layer['name'],
                layer_source=layer['source'],
            )

            stack_layers.update({layer['name']: new_layer.layer_version_arn})

        self.layers = stack_layers
