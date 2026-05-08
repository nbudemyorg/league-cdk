import aws_cdk.aws_dynamodb as dynamodb
from aws_cdk import RemovalPolicy
from types_boto3_dynamodb.service_resource import Table


def valid_key(key_type: str, key: dict[str, str]) -> bool:
    name = key.get('name')
    type = key.get('type')
    if not name or not type:
        return False

    return type in dynamodb.AttributeType


def create_table(self, **kwargs) -> Table:
    print(kwargs)
    table_name = kwargs.get('table_name')
    removal_policy = kwargs.get('removal_policy', 'DESTROY')
    billing_mode = kwargs.get('billing_mode', 'PAY_PER_REQUEST')
    partition_key = kwargs.get('partition_key')
    sort_key = kwargs.get('sort_key')
    ttl_attr = kwargs.get('ttl_attr')

    if not table_name or not isinstance(table_name, str):
        raise TypeError(
            'Parameter table_name must be supplied and be of type str.'
        )

    if not isinstance(removal_policy, str):
        raise TypeError('table_name must be of type str.')

    if removal_policy not in RemovalPolicy:
        raise ValueError(
            f'Value {removal_policy} is not in RemovalPolicy Enum.'
        )

    if not isinstance(billing_mode, str):
        raise TypeError('billing_mode must be of type str.')

    if billing_mode not in dynamodb.BillingMode:
        raise ValueError(f'Value {billing_mode} is not in BillingMode Enum.')

    if not partition_key:
        raise ValueError('partition_key must be supplied.')

    if not isinstance(partition_key, dict):
        raise TypeError('partition_key must be of type dict.')

    if not valid_key('Partition', partition_key):
        raise ValueError('Supplied Partition Key is not valid.')

    pk_name = partition_key['name']
    pk_type = partition_key['type']
    pk_attribute = dynamodb.Attribute(
        name=pk_name, type=dynamodb.AttributeType[pk_type]
    )

    if sort_key:
        if not isinstance(sort_key, dict):
            raise TypeError('Sort Key must of type dict')
        if not valid_key('Sort', sort_key):
            raise ValueError('Supplied Sort Key is not valid.')
        sk_name = sort_key['name']
        sk_type = sort_key['type']
        sk_attribute = dynamodb.Attribute(
            name=sk_name, type=dynamodb.AttributeType[sk_type]
        )
    else:
        sk_attribute = None

    if ttl_attr and not isinstance(ttl_attr, str):
        raise ValueError('TTL attribute must be of type str')

    return dynamodb.Table(
        self,
        table_name,
        removal_policy=RemovalPolicy[removal_policy],
        table_name=table_name,
        billing_mode=dynamodb.BillingMode[billing_mode],
        partition_key=pk_attribute,
        sort_key=sk_attribute,
        time_to_live_attribute=ttl_attr,
    )
