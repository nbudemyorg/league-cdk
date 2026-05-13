ddb_tables = {
    'tables': [
        {
            'table_name': 'Users',
            'partition_key': {'name': 'player_id', 'type': 'STRING'},
        },
        {
            'table_name': 'Sessions',
            'partition_key': {'name': 'player_id', 'type': 'STRING'},
            'sort_key': {'name': 'session_id', 'type': 'STRING'},
            'ttl_attr': 'ttl',
        },
        {
            'table_name': 'Resets',
            'partition_key': {'name': 'reset_id', 'type': 'STRING'},
            'ttl_attr': 'ttl',
        },
    ]
}
