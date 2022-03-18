from instagram_private_api import Client, ClientError, ClientLoginError, ClientCookieExpiredError, ClientLoginRequiredError
import yaml
from yaml.loader import FullLoader, Loader
import sys
import os
import codecs
import json
import argparse
from tqdm import tqdm

def get_password():
        try:
            password = yaml.load(open('./creds/creds.yml'), Loader=FullLoader)
            passwd = password['password']
            if passwd:
                return str(passwd)
            else:
                print("Error in creds.yml. Are your credentials in the correct format? \nusername: <username> \npassword: <password>")
                sys.exit()
        except FileNotFoundError:
            print("Error: file not found")
            print("\n")
        except TypeError as e:
            if str(e) == "string indices must be integers":
                print("Error in creds.yml. Are your credentials in the correct format? \nusername: <username> \npassword: <password>")
                sys.exit()

def get_username():
    try:
        username = yaml.load(open('./creds/creds.yml'), Loader=FullLoader)
        user = username['username']
        if user:
            return str(user)
        else:
            print("Error in creds.yml. Are your credentials in the correct format? \nusername: <username> \npassword: <password>")
            sys.exit()
    except FileNotFoundError:
        print("Error: file not found")
        print("\n")
    except TypeError as e:
        if str(e) == "string indices must be integers":
                print("Error in creds.yml. Are your credentials in the correct format? \nusername: <username> \npassword: <password>")
                sys.exit()

def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')

    
def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        print('SAVED: {0!s}'.format(new_settings_file))

def login():
    username = get_username()
    password = get_password()
    

    settings_file_path = "./creds/settings.json"
    device_id = None
    try:

            settings_file = settings_file_path
            if not os.path.isfile(settings_file):
                # settings file does not exist
                print('Unable to find file: {0!s}'.format(settings_file))

                # login new
                api = Client(
                    username, password,
                    on_login=lambda x: onlogin_callback(x, settings_file_path))
            else:
                with open(settings_file) as file_data:
                    cached_settings = json.load(file_data, object_hook=from_json)
                print('Reusing settings: {0!s}'.format(settings_file))

                device_id = cached_settings.get('device_id')
                # reuse auth settings
                api = Client(
                    username, password,
                    settings=cached_settings)

    except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
        print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

        # Login expired
        # Do relogin but use default ua, keys and such
        api = Client(
            username, password,
            device_id=device_id,
            on_login=lambda x: onlogin_callback(x, settings_file_path))

    except ClientError as err:
            e = json.loads(err.error_response)
            print(e['message'])
            print(err.msg)
            print("\n")
            if 'challenage' in e:
                print("Please follow link to complete the challange " + e['challange']['url'])
            sys.exit()

    return api


def check_following(target_id):
    if str(target_id) == api.authenticated_user_id:
        return True
    endpoint = 'users/{user_id!s}/full_detail_info/'.format(**{'user_id' : target_id})
    return api._call_api(endpoint)['user_detail']['user']['friendship_status']['following']

def get_followers(username):
    content =   api.username_info(username)
    target_id = content['user']['pk']
    is_private = content['user']['is_private']
    following = check_following(target_id)
    if is_private and not following:
        print(f"Not following @{username}. Cannot retrieve followers.")
    else:
        get_followers = []
        followers = []
        
        rank_token = api.generate_uuid()
        data = api.user_followers(str(target_id), rank_token=rank_token)
        
        get_followers.extend(data.get('users', []))
        tq.update(len(data.get('users', [])))
        
        next_max_id = data.get('next_max_id')
        while next_max_id:
            results = api.user_followers(str(target_id), rank_token=rank_token, max_id=next_max_id)
            get_followers.extend(results.get('users', []))
            tq.update(len(results.get('users', [])))
            next_max_id = results.get('next_max_id')
        
        for user in get_followers:
            users = {
                'id': user['pk'],
                'username':user['username'],
                'full_name': user['full_name']
            }
            followers.append(users["username"]) # I have left it like this is for future development purposes.

        return followers

def get_number_of_followers(username):
    content =   api.username_info(username)
    target_id = content['user']['pk']
    content = api.user_info(str(target_id))
    return int(content["user"]["follower_count"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Information about any airport from all over the world.")
    parser.add_argument('-u', '--users', type=str, default=None, help="List of usernames which the user follows. Use \" 's.")
    args = parser.parse_args()

    if args.users:
        api = login()
        users_string = args.users
        users = users_string.split(" ")
        db = []
        total_followers = 0
        for username in users:
            total_followers += get_number_of_followers(username)

        tq = tqdm(total=total_followers,desc="Fetching followers")

        for username in users:
            followers = get_followers(username)
            db.append(followers)

        tq.update(total_followers-tq.n) # Just in case total_followers is more than the progress of the bar.
        tq.close() # finish bar


        result = set(db[0])
        for s in db[1:]:
            result.intersection_update(s)
        
        print(f"\nFound {len(result)} mutual followings: ")
        for user in result:
            print (f"@{user}")
