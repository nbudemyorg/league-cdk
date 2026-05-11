from pathlib import Path

from aws_cdk import Duration
from aws_cdk.aws_iam import Effect, PolicyStatement
from aws_cdk.aws_lambda import Code, Function, LayerVersion, Runtime
from types_boto3_dynamodb.service_resource import Table

DEFAULT_RUNTIME = Runtime.PYTHON_3_14


def create_layer_list(
    requested_layers: list[str],
    stack_layers: list[dict[str, LayerVersion]],
) -> list[LayerVersion] | None:

    layers = []
    for requested_layer in requested_layers:
        if not isinstance(requested_layer, str):
            raise TypeError('Lambda layer names must be of type str.')
        if requested_layer in stack_layers:
            layers.append(stack_layers[requested_layer])
        else:
            raise ValueError(f'Lambda layer {requested_layer} not found.')

    return layers


def get_table_arn(stack_tables: dict[str, Table], table: str) -> str:
    stack_table = stack_tables.get(table)
    if not stack_table:
        raise ValueError(f'Dynamodb Table {table} not found in config.')
    return stack_table.table_arn


def generate_sid(lambda_name: str, res_type: str, res_name: str) -> str:
    return f'{lambda_name}{res_name.capitalize()}{res_type.capitalize()}'


def create_policy(
    actions: list[str], resource_arn: str, sid: str
) -> PolicyStatement:

    return PolicyStatement(
        effect=Effect.ALLOW,
        actions=actions,
        resources=[resource_arn],
        sid=sid,
    )


# def add_policy_to_lambda(_lambda: Function, )


def create_lambda(
    self,
    stack_layers: dict[str, LayerVersion] = None,
    stack_tables: dict[str, Table] = None,
    **kwargs,
) -> Function:

    lambda_name = kwargs.get('lambda_name')
    handler = kwargs.get('handler')
    source_dir = kwargs.get('source_dir')
    timeout = kwargs.get('timeout', 5)
    environment = kwargs.get('environment')
    requested_layers = kwargs.get('layers')
    iam_policies = kwargs.get('policies')

    if not lambda_name or not isinstance(lambda_name, str):
        raise TypeError('lambda_name must be provided and be of type str.')

    if not handler or not isinstance(handler, str):
        raise TypeError('handler must be provided and be of type str.')

    if not source_dir or not isinstance(source_dir, str):
        raise TypeError('source_dir must be provided and be of type str.')

    source_path = Path(source_dir)

    if not source_path.is_dir():
        raise ValueError('source_dir is not a valid, relative directory.')

    if not isinstance(timeout, int):
        raise TypeError('timeout is not of type int.')

    if 0 > timeout > 900:
        raise ValueError('timeout must be > 0 and less than 900 seconds.')

    # if not isinstance(environment, dict):
    #    raise TypeError('environment must be of type dict.')

    if isinstance(requested_layers, list):
        layer_list = create_layer_list(requested_layers, stack_layers)
    else:
        layer_list = None

    new_lambda = Function(
        self,
        lambda_name,
        function_name=lambda_name,
        handler=handler,
        runtime=DEFAULT_RUNTIME,
        code=Code.from_asset(path=source_dir),
        timeout=Duration.seconds(timeout),
        layers=layer_list,
    )

    if iam_policies is not None and 'tables' in iam_policies:
        table_policies = iam_policies['tables']
        for policy in table_policies:
            table_name = policy.get('name')
            table_actions = policy.get('actions')

            if table_actions is None:
                raise ValueError('Policy Table actions are not defined.')
            if table_name is None:
                raise ValueError('No Table name found in Policy definition')

            table_arn = get_table_arn(stack_tables, table_name)
            policy_sid = generate_sid(lambda_name, 'table', table_name)
            new_policy = create_policy(table_actions, table_arn, policy_sid)

            new_lambda.add_to_role_policy(new_policy)

    return new_lambda
