from pymongo import MongoClient, DESCENDING, ASCENDING

import datetime
from logger_custom import get_module_logger
from email_module import send_general_text_email
from redis_utils import enqueue_long_running_function
from zoneinfo import ZoneInfo


logger = get_module_logger(__name__)

client = MongoClient('mongo',username='root',password='example') # mongo container/service
db = client['platform']
# sensor_collection = db['sensor_data']
# contact_submission = db['contact_submission']


class ChartSettings:
    def __init__(self, collection, user_name, client_name):
        self.collection = db[collection]

    def save(self, chart_name, chart_config):
        data = {'chart_name': chart_name, 'chart_config': chart_config}
        self.collection.insert_one(data)

    def get_all(self):
        return list(self.collection.find({}))

    def get_by_id(self, chart_id):
        return self.collection.find_one({'_id': ObjectId(chart_id)})



def tz_converter(time, browser_timezone):

    # not sure why I added this line, but was giving wrong time zone that's why I skipped it
    # utc_time = time.replace(tzinfo=ZoneInfo('UTC'))

    if not time:
      return ''
    
    logger.debug('time: '+str(time))
    tz_time = time.astimezone(ZoneInfo(browser_timezone))


    res = tz_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    return res

def update_profile_in_db(key, doc):
    # client = MongoClient('127.0.0.1', 22022)
    # db = client.platform
    coll = db.pages
    # contact_submission = db['contact_submission']

    doc['ts'] = datetime.datetime.now()
    coll.update(key, doc, upsert=True)


def read_user_doc(email):
    users = db['users']
    user_doc = users.find_one({'email': email})
    return user_doc


def write_to_user_doc(key, item):
    users = db['users']
    users.update_one(
        key,
        {
            "$set": item,
            "$currentDate": {"lastModified": True}
        }
    )


def timezone_write(username, tz):
    logger.debug(
        '# going to update the tz {} for user {}: '.format(tz, username))
    write_to_user_doc({'email': username}, {'tz': tz})
    return None


def timezone_read(username):
    try:
        user_doc = read_user_doc(username)
        if user_doc:
            tz = user_doc['tz']
            return tz
        else:
            return ''
    except Exception as e:
        logger.debug('# error: '+str(e))
        return


def update_sensor_data(doc):
    sensor_collection.insert_one(doc)


def contact_submission_update(doc):
    # logit('going to write in db')
    contact_submission.insert_one(doc)
    # logit('db writing is done')
    return True


def create_new_user(doc):
    # todo: don't keep the whole doc received from form submission, this is security threat
    users = db["users"]
    if users.find_one({'email': doc['email']}):
        return False
    else:
        users.insert_one(doc)
        return True


def fetch_device_overview_mongodb(user_name, search_like, start, length, order):
    logger.debug('# user_name: '+str(user_name))
    logger.debug('# search_like: '+str(search_like))
    logger.debug('# order: '+str(order))
    logger.debug('# start: '+str(start))
    logger.debug('# length: '+str(length))
    
    collection = db['devices']
    try:
        # Construct the query for MongoDB
        query = {
            "user_name": user_name,
            "client_name": {"$regex": search_like}
        }
        
        start = int(start)
        length = int(length)
        

        # Sort the results
        sort_field = order[0]['column_name']
        sort_direction = 1 if order[0]['direction'] == 'asc' else -1
        sort = [(sort_field, sort_direction)]

        # Perform the query
        logger.debug('# query: '+str(query))
        logger.debug('# sort: '+str(sort))
        query_res = collection.find(query, projection={"_id": 0}).sort(sort).skip(start).limit(length)
        
        logger.debug('# query_res: '+str(query_res))

        # Count the total records
        total_records = collection.count_documents(query)

        data = []
        browser_timezone = timezone_read(user_name)

        for row in query_res:
            data_row = {}
            data_row['user_name'] = row['user_name']
            data_row['client_name'] = "<a href='/devices/{}'>{}</a>".format(
                row['client_name'], row['client_name'])
            data_row['first_message'] = tz_converter(
                row['ts_registered'], browser_timezone) if 'ts_registered' in row else 'No contact yet'
            data_row['last_message'] = tz_converter(
                row['ts_last_message'], browser_timezone) if 'ts_last_message' in row else 'No contact yet'

            data.append(data_row)

        res = {
            'data': data,
            'recordsFiltered': len(data),
            'recordsTotal': total_records,
        }

    except Exception as e:
        res = {
            'data': [],
            'recordsFiltered': 0,
            'recordsTotal': 0,
        }
        
        logger.debug('# error: '+str(e))

    return res


def verify_and_notify(clickhouse_data, user_name, search_like):
    # logger.debug('# in verify_and_notify, clickhouse_data: ' +
    #             str(clickhouse_data))
    device_collection = db['devices']
    unregistered_devices = []

    # Go through the found devices in clickhouse and check if it is registered in MongoDB
    for data in clickhouse_data:
        # user_name = data[1]
        client_name = data[2]
        existing_device = device_collection.find_one(
            {'client_name': client_name, 'user_name': user_name})
        if existing_device is None:

            logger.debug('# in verify_and_notify, client_name: '+str(client_name) +
                         ' is missing in MongoDB for user: '+str(user_name))

            # Device not found in MongoDB, add to list of unregistered devices
            unregistered_devices.append(client_name)

    # Remove any unregistered devices from the clickhouse_data list
    clickhouse_data = [
        data for data in clickhouse_data if data[2] not in unregistered_devices]

    # Some devices are registered in MongoDB but not in found ClickHouse, these also
    # should be displayed in the device overview but with None values for the
    # first_message and last_message
    devices = device_collection.find({'user_name': user_name})

    clickhouse_client_names = set([row[2] for row in clickhouse_data])
    device_client_names = [device['client_name']
                           for device in devices if search_like in device['client_name']]
    logger.debug('# in verify_and_notify, devices: '+str(device_client_names))

    new_rows = []
    for name in device_client_names:
        if name not in clickhouse_client_names:
            new_row = ('', user_name, name, '', '')
            new_rows.append(new_row)

    clickhouse_data.extend(new_rows)

    # notify the admin about the unregistered devices
    if unregistered_devices:
        email_message_text = f"clients: {str(unregistered_devices)} \
        user_name: {user_name} \
        is not registered in MongoDB"
        enqueue_long_running_function(
            send_general_text_email, email_message_text, 'Unregistered devices found in ClickHouse')

    # Return the shortened list of clickhouse_data
    return clickhouse_data


def verify_and_notify_v2(clickhouse_data):
    logger.debug('# in verify_and_notify, clickhouse_data: ' +
                 str(clickhouse_data))
    device_collection = db['devices']
    unregistered_devices = []

    # Go through the found devices in clickhouse and check if it is registered in MongoDB
    for data in clickhouse_data:
        user_name = data[1]
        client_name = data[2]
        existing_device = device_collection.find_one(
            {'client_name': client_name, 'user_name': user_name})
        if existing_device is None:
            logger.debug('# in verify_and_notify, client_name: ' + str(client_name) +
                         ' is missing in MongoDB for user: ' + str(user_name))
            # Device not found in MongoDB, add to list of unregistered devices
            unregistered_devices.append(client_name)

    # Remove any unregistered devices from the clickhouse_data list
    clickhouse_data = [
        data for data in clickhouse_data if data[2] not in unregistered_devices]

    # Add devices in the `devices` collection that aren't in `clickhouse_data` yet
    user_name = clickhouse_data[0][1]
    device_client_names = [device['client_name']
                           for device in device_collection.find({'user_name': user_name})]
    new_rows = [(None, user_name, name, None, None)
                for name in set(device_client_names) - set(clickhouse_data)]
    clickhouse_data.extend(new_rows)

    # Notify the admin about the unregistered devices
    if unregistered_devices:
        email_message_text = f"clients: {str(unregistered_devices)} user_name: {user_name} is not registered in MongoDB"
        enqueue_long_running_function(
            send_general_text_email, email_message_text, 'Unregistered devices found in ClickHouse')

    # Return the shortened list of clickhouse_data
    return clickhouse_data


def create_new_device(client_name, user_name, device_token, ts_registered):
    devices = db['devices']
    if devices.find_one({'client_name': client_name}):
        return False
    else:
        devices.insert_one({'client_name': client_name,
                           'user_name': user_name, 'device_token': device_token, 'ts_registered': ts_registered})
        return True


def read_device_info(client_name, user_name):
    devices = db['devices']
    device_info = devices.find_one(
        {'client_name': client_name, 'user_name': user_name})
    if not device_info:
        return False
    else:
        return device_info


def update_device_info(client_name, user_name, keyvalue):
    devices = db['devices']

    # Check if the user_name and client_name exist
    filter_criteria = {"client_name": client_name, "user_name": user_name}
    existing_document = devices.find_one(filter_criteria)

    if existing_document is None:
        return False  # User or client not found

    # Construct the filter to identify the specific document to update
    filter_criteria["_id"] = existing_document["_id"]

    # Update only the specified keyvalue
    update_data = {
        "$set": keyvalue,
        "$currentDate": {"lastModified": True}
    }

    # Perform the update
    result = devices.update_one(filter_criteria, update_data)

    if result.modified_count == 1:
        return True  # Update successful
    else:
        return False  # Update not successful
    


def add_chart_to_db(client_name, user_name, chart_name, chart_config, chart_unique_id, params):
    # Connect to the MongoDB server
    # client = MongoClient('mongodb://localhost:27017')  # Replace with your MongoDB connection string
    # db = client.your_database_name  # Replace with your database name
    devices = db.devices

    # Find the device with the given client_name and user_name
    device = devices.find_one({"client_name": client_name, "user_name": user_name})

    if device:
        # Device exists, retrieve the current highest position_id or set to 0 if no charts yet
        position_id = device.get("highest_position_id", 0)

        # Create a new chart with the next position_id
        new_chart = {
            "chart_name" : chart_name,
            "chart_unique_id" : chart_unique_id,
            "chart_config": chart_config,
            "position_id": position_id,
            "params":params
        }

        # Append the new chart to the device's charts list
        devices.update_one(
            {"_id": device["_id"]},
            {
                "$push": {"charts": new_chart},
                "$set": {"highest_position_id": position_id + 1}
            }
        )

        return True
    else:
        return False
    
    

def get_chart_from_db(client_name, user_name):
    # Connect to the MongoDB server
    # client = MongoClient('mongodb://localhost:27017')  # Replace with your MongoDB connection string
    # db = client.your_database_name  # Replace with your database name
    devices = db.devices

    # Find the device with the given client_name and user_name
    device = devices.find_one({"client_name": client_name, "user_name": user_name})
    
    if device:
        # Find the chart with the specified position_id
        charts = device.get("charts", [])
        
        return charts
        # for chart in charts:
        #     if chart.get("position_id") == position_id:
        #         chart_config = chart.get("chart_config")
                
        #         return chart_config
    
    return None


def update_device_params(user_name, client_name, timestamp, param_subtree):

    try:
        collection = db['device_params']
        data = {
            'user_name': user_name,
            'client_name': client_name,
            'timestamp': timestamp,
            'param_subtree': param_subtree
        }
        collection.insert_one(data)
        return True
    except Exception as e:
        logger.debug('# in update_device_parameter, exception: '+str(e))
        return False


def get_chart_data(user_name, client_name, chart_unique_ids, limit=30):
    # Establish a connection to the MongoDB database
    
    
    devices = db["devices"]
    device_params = db["device_params"]

    # Check if the user and client exist in the 'devices' collection
    device = devices.find_one({"user_name": user_name, "client_name": client_name})
    if not device:
        return "User or client not found in 'devices' collection."

    # Fetch the params list from the 'devices' collection
    
    params_list = device.get("params", [])
    
    logger.debug('params_list: '+str(params_list))

    result = {}

    for chart_unique_id in chart_unique_ids:
        chart_data = []
        for chart in device.get("charts", []):
            if chart.get("chart_unique_id") == chart_unique_id:
                params_list = chart.get("params", [])
                for param in params_list:
                    param_data = device_params.find({
                        "user_name": user_name,
                        "client_name": client_name,
                        "param_subtree." + param: {"$exists": True}
                    }).limit(limit).sort("timestamp", -1)

                    chart_data.extend([{
                        'timestamp': doc["timestamp"],
                        'param_subtree': {
                            param: doc["param_subtree"][param]
                        }
                    } for doc in param_data])

        result[chart_unique_id] = chart_data

    return result


def read_users_collection():
    return db['users'].find()


if __name__ == '__main__':

    '''
    read_user_doc('test_user_name')

    to_store = {'car': 'ford'}
    write_to_user_doc({'username': 'test_user_name'}, to_store)

    print
    "After updating the user document: "
    print
    read_user_doc('test_user_name')
    user = read_user_doc('test_user_name')
    print
    #'user car is: ', user['car']
    new_user = {'username': 'New boy', 'car': 'Nissa'}
    create_new_user(new_user)


    print
    "After adding new user:"
    print
    read_user_doc('New boy')

    # sample to print the whole collection docs
    for i in read_users_collection():
        print
        "Items from users collection: ", i

    #update_sensor_data({'aa': 10, 'bb': 20})
    create_new_device('fff')
    '''

    res = read_device_info('mx', 'a@a.a')
    print(res)
