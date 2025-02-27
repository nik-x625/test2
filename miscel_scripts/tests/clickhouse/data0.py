import clickhouse_connect
client = clickhouse_connect.get_client(host='localhost', port='8123', username='default')
#client.command('CREATE TABLE new_table (key UInt32, value String, metric Float64) ENGINE MergeTree ORDER BY key')


row1 = [1500, 'String Value 1000', 5.233]
row2 = [2600, 'String Value 2000', -107.04]
data = [row1, row2]
client.insert('new_table', data, column_names=['key', 'value', 'metric']) 




result = client.query('SELECT * FROM new_table')
print(result)
print(dir(result))
print()
print(result.summary)
print(result.result_set)
