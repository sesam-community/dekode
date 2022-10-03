from flask import Flask, request, jsonify, Response
import json
import requests
import os
import sys
from sesamutils import VariablesConfig, sesam_logger

app = Flask(__name__)
logger = sesam_logger("Steve the logger", app=app)

## Logic for running program in dev
try:
    with open("helpers.json", "r") as stream:
        logger.info("Setting env vars via helpers.json")
        env_vars = json.load(stream)
        os.environ['dekode_password'] = env_vars['dekode-password']
        os.environ['dekode_base_url'] = env_vars['dekode-base-url']
        os.environ['active_users_base_url'] = env_vars['active_users_base_url']
except OSError as e:
    logger.info("Using env vars defined in SESAM")

## Helpers
required_env_vars = ['dekode_password', 'dekode_base_url']
optional_env_vars = ["page_size"]
password = os.getenv('dekode_password')
base_url = os.getenv('dekode_base_url')
active_users_base_url = os.getenv('active_users_base_url')

## Helper functions
def stream_json(clean):
    first = True
    yield '['
    for i, row in enumerate(clean):
        if not first:
            yield ','
        else:
            first = False
        yield json.dumps(row)
    yield ']'

@app.route('/')
def index():
    output = {
        'service': 'Dekode is running',
        'remote_addr': request.remote_addr
    }
    return jsonify(output)

@app.route('/get_user_id', methods=['GET', 'POST'])
def get():
    ## Validating env vars
    config = VariablesConfig(required_env_vars, optional_env_vars)
    if not config.validate():
        sys.exit(1)

    request_data = request.get_data()
    json_data = json.loads(str(request_data.decode("utf-8")))

    # Helpers
    user_id = None
    headers = {
        "Accept": "application/json",
        "Authorization": f"{password}",
        "Content-type": "application/json"
    }

    try:
        actor_id = json_data[0].get('aktorid')
        data = requests.get(f"{active_users_base_url}?actor_id={actor_id}", headers=headers)
        decoded_data = json.loads(data.content.decode('utf-8-sig'))
        if decoded_data.get('success') == True:
            user_id = decoded_data.get('user_id')
        else:
            logger.info('Setting user_id to None, as user was not found in Dekode.')
            user_id = None

    except Exception as e:
        logger.warning(f"Could not get aktorid from SESAM. Failed with error: {e}")
     
    transform_response = []
    if json_data[0].get("_id"):
        return_dictionary = {
        "_id": f"{json_data[0].get('_id')}",
        "actor_id": actor_id,
        "user_id": user_id
        }
        transform_response.append(return_dictionary)
    else:
        logger.error(f"No _id provided in payload... Skipping entity")
        pass

    return Response(stream_json(transform_response), mimetype='application/json')


@app.route('/post', methods=['GET','POST'])
def post():
    ## Validating env vars
    config = VariablesConfig(required_env_vars, optional_env_vars)
    if not config.validate():
        sys.exit(1)

    headers = {
        "Accept": "application/json",
        "Authorization": f"{password}",
        "Content-type": "application/json"
    }
    
    request_data = request.get_data()
    json_data = json.loads(str(request_data.decode("utf-8")))

    for element in json_data:
        function = element['properties']
        del element['properties']
        if '/' in function:
            logger.info('trying to update user')
            update_response = requests.post(f"{base_url}/{function}", headers=headers, data=json.dumps(element))
            if update_response.status_code == 200:
                logger.info(f"User {element['email']} has been updated!")
            else:
                logger.error(f"Failed to update user {element['email']}, with error: {update_response.content}")
        
        if function == "users":
            logger.info('trying to create user')
            create_response = requests.post(f"{base_url}/{function}", headers=headers, data=json.dumps(element))
            if create_response.status_code == 201:
                logger.info(f"User {element['email']} has been created!")
            else:
                logger.error(f"Failed to create user {element['email']}, with error: {create_response.content}")

        else:
            logger.info('Nothing to do...')

    return jsonify({'Steve reporting': "work complete..."})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)