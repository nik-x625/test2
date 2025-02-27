import clickhouse_connect
from logger_custom import get_module_logger
from datetime_converter import datetime_to_elapsed
from mongodb_module import timezone_read, verify_and_notify

from flask import session
# for timezone management, ref: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-dates-and-times
from momentjs import momentjs
# from qlines import app
from pprint import pprint
logger = get_module_logger(__name__)

CLICKHOUSE_SERVER = "127.0.0.1"
CLICKHOUSE_PORT = "7010"

client_handler = clickhouse_connect.get_client(
    host=CLICKHOUSE_SERVER,
    port=CLICKHOUSE_PORT,
    username='default',
    query_limit=0
    )

def update_clickhouse(data):
    try:
        client = ClickhouseClient(CLICKHOUSE_SERVER)
        query = f"INSERT INTO table1 VALUES (%s, %s, %s, %s, %s)"
        client.execute(query, data)
        logger.debug('Inserted data into ClickHouse: %s', data)
    except Exception as e:
        logger.error('Error inserting data into ClickHouse: %s', e)


def fetch_ts_data_per_param(user_name, client_name, param_name, limit, table_name='table1'):
    try:
        query_string = "SELECT param_name, ts, param_value FROM {} WHERE user_name='{}' and client_name='{}' and param_name='{}' ORDER BY ts DESC LIMIT {}".format(
            table_name, user_name, client_name, param_name, limit)

        # logger.debug('# query string: '+str(query_string))
        res = client_handler.query(query_string)
        # logger.debug('# query res: '+str(res.result_set))

        return res

    except Exception as e:
        logger.debug('# fetch_ts_data_per_param error: '+str(e))
        return ''


def fetch_device_overview_clickhouse(table_name, user_name, search_like, start, length, order):

    try:
        # todo: add try/except here

        # logger.debug('# in fetch_device_overview, username: '+str(user_name))

        browser_timezone = timezone_read(user_name)
        logger.debug(
            '# in fetch_device_overview_clickhouse function, user_timezone is: '+str(browser_timezone))

        order_by = order[0]['column_name']
        order_direction = order[0]['direction']

        # to get the number for 'recordsTotal'
        try:
            res_total = client_handler.query(
                f"select count(distinct(client_name)) from {table_name} where user_name='{user_name}'")
            recordsTotal = res_total.result_set
        except Exception as e:
            recordsTotal = [[0]]

        # to do the main query to get the filtered data
        # res_filtered = client_handler.query("select count(*) OVER () AS TotalRecords, user_name, client_name, min(ts) as first_message, max(ts) as last_message \
        # from {} where user_name='{}' and (client_name like '%{}%' OR user_name like '%{}%') group by client_name, user_name order by {} {} offset {} rows fetch next {} rows only"
        #                                    .format(table_name, user_name, search_like, search_like, order_by, order_direction, start, length))

        # to do the main query to get the filtered data
        query_string = f"select count(*) OVER () AS TotalRecords, user_name, client_name, min(ts) \
                        as first_message, max(ts) as last_message from {table_name} where \
                        user_name='{user_name}' and client_name like '%{search_like}%' \
                        group by client_name, user_name \
                        order by {order_by} {order_direction} \
                        offset {start} rows fetch next {length} rows only"

        try:
            res_filtered = client_handler.query(query_string)
            query_res = res_filtered.result_set
        except Exception as e:
            logger.debug(
                '# in fetch_device_overview_clickhouse, exception: '+str(e))
            query_res = []

        # verify with MongoDB if the devices are already registered, otherwise removes it from the list and notifies the admin by email
        logger.debug('# before verify_and_notify,  query_res: '+str(query_res))
        query_res = verify_and_notify(query_res, user_name, search_like)
        logger.debug('# after verify_and_notify,  query_res: '+str(query_res))

        data = []
        count = 0
        for row in query_res:
            data_row = {}
            data_row['user_name'] = row[1]
            data_row['client_name'] = "<a href='/devices/{}'>{}</a>".format(
                row[2], row[2])
            data_row['first_message'] = tz_converter(
                row[3], browser_timezone) if row[3] is not '' else 'No contact yet'
            data_row['last_message'] = tz_converter(
                row[4], browser_timezone) if row[4] is not '' else 'No contact yet'

            count = row[0]

            data.append(data_row)

        res = {
            'data': data,
            'recordsFiltered': count,  # recordsFiltered[0][0],
            'recordsTotal': recordsTotal[0][0],
        }

        logger.debug('# in fetch_device_overview_clickhouse, res: '+str(res))

    except Exception as e:
        logger.debug(
            '# in fetch_device_overview_clickhouse, exception: '+str(e))
        res = {
            'data': [],
            'recordsFiltered': 0,
            'recordsTotal': 0,
        }

    return res


if __name__ == '__main__':
    # res = fetch_device_overview('table1', 'a@b.c', 'cpex66', 10
    res = fetch_device_overview(
        'table1', 'a@b.c', '', 0, 10, [{'column_name': 'last_message', 'direction': 'desc'}])
    pprint('res is: '+str(res))

    ''' 
    clickhouse cli direct command here:
    
    select user_name, client_name, min(ts) as first_message, max(ts) as last_message from table1 where user_name='a@b.c' and client_name like '%cpe%' group by client_name, user_name order by last_message desc limit 20
    
    '''
