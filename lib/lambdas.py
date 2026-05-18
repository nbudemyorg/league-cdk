from pathlib import Path
from typing import Any

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


def create_policy(
    actions: list[str], resource_arn: str, sid: str
) -> PolicyStatement:

    return PolicyStatement(
        effect=Effect.ALLOW,
        actions=actions,
        resources=[resource_arn],
        sid=sid,
    )


def get_table_arn(stack_tables: dict[str, Table], table: str) -> str:
    stack_table = stack_tables.get(table)
    if not stack_table:
        raise ValueError(f'Dynamodb Table {table} not found in config.')
    return stack_table.table_arn


def generate_sid(lambda_name: str, res_type: str, res_name: str) -> str:
    return f'{lambda_name}{res_name.capitalize()}{res_type.capitalize()}'


def get_policy_actions(
    resource_type: str, policy: dict[str, Any], name: str
) -> str:
    resource_actions = policy.get('actions')
    if resource_actions is None:
        raise ValueError(
            f'Lambda {name}: No policy actions defined for {resource_type}.'
        )
    return resource_actions


def get_policy_resource(
    resource_type: str, policy: dict[str, Any], name: str
) -> str:
    resource_name = policy.get('name')
    if resource_name is None:
        raise ValueError(
            f'Lambda {name}: No name defined for {resource_type} in policy.'
        )
    return resource_name


def create_lambda(
    self,
    stack_layers: dict[str, LayerVersion],
    stack_secrets: dict[str, str],
    stack_tables: dict[str, Table],
    events_arn: str,
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
        code=Code.from_asset(path=source_dir),
        environment=environment,
        function_name=lambda_name,
        handler=handler,
        layers=layer_list,
        runtime=DEFAULT_RUNTIME,
        timeout=Duration.seconds(timeout),
    )

    if iam_policies is not None:
        if 'tables' in iam_policies:
            table_policies = iam_policies['tables']
            res = 'table'
            for policy in table_policies:
                table_name = get_policy_resource(res, policy, lambda_name)
                table_actions = get_policy_actions(res, policy, lambda_name)
                table_arn = get_table_arn(stack_tables, table_name)
                sid = generate_sid(lambda_name, res, table_name)
                new_policy = create_policy(table_actions, table_arn, sid)
                new_lambda.add_to_role_policy(new_policy)

        if 'secrets' in iam_policies:
            secret_policies = iam_policies['secrets']
            res = 'secret'
            for policy in secret_policies:
                secret_name = get_policy_resource(res, policy, lambda_name)
                secret_actions = get_policy_actions(res, policy, lambda_name)
                secret_arn = stack_secrets[secret_name]
                sid = generate_sid(lambda_name, res, secret_name)
                new_policy = create_policy(secret_actions, secret_arn, sid)
                new_lambda.add_to_role_policy(new_policy)

        if 'events' in iam_policies:
            events_policies = iam_policies['events']
            res = 'events'
            for policy in events_policies:
                events_name = get_policy_resource(res, policy, lambda_name)
                events_actions = get_policy_actions(res, policy, lambda_name)
                sid = generate_sid(lambda_name, res, events_name)
                new_policy = create_policy(events_actions, events_arn, sid)
                new_lambda.add_to_role_policy(new_policy)

    return new_lambda
