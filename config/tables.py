ddb_tables = {
    'USERS': {
        'table_name': 'Users',
        'partition_key': {'name': 'player_id', 'type': 'STRING'},
    },
    'SESSIONS': {
        'table_name': 'Sessions',
        'partition_key': {'name': 'player_id', 'type': 'STRING'},
        'sort_key': {'name': 'session_id', 'type': 'STRING'},
        'ttl_attr': 'ttl',
    },
    'RESET': {
        'table_name': 'PasswordReset',
        'partition_key': {'name': 'reset_id', 'type': 'STRING'},
        'ttl_attr': 'ttl',
    },
}
