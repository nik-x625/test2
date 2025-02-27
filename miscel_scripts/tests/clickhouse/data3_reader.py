import clickhouse_connect
from datetime import datetime

client = clickhouse_connect.get_client(
    host='localhost', port='7010', username='default')
client.command('CREATE TABLE IF NOT EXISTS table1 (ts DATETIME, client_name String, param_name String, param_value Float64) ENGINE MergeTree ORDER BY client_name')

client_name = 'cpe1'
limit = 10
param_name = 'param1'
table_name = 'table1'
result = client.query("SELECT param_name, ts, param_value FROM {} WHERE client_name='{}' and param_name='{}' ORDER BY ts DESC LIMIT {}".format(
    table_name, client_name, param_name, limit))


print(result.result_set)
