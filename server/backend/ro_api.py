import json
import subprocess
from tempfile import NamedTemporaryFile
from urllib.parse import urljoin

import requests

BASE_URL = 'https://api.remonline.app/'
API_KEY = 'c0c5fe906bb14f828316f6e255d17859'


class CustomDict(dict):
    def __getattribute__(self, name):
        return self[name]


def to_custom_dict(obj) -> CustomDict:
    if isinstance(obj, list):
        result = []
        for data in obj:
            if isinstance(data, (list, dict)):
                result.append(to_custom_dict(data))
            else:
                result.append(data)

        return result

    custom_dict = CustomDict(obj)
    for key in custom_dict:
        if isinstance(custom_dict[key], dict):
            custom_dict[key] = CustomDict(custom_dict[key])
        elif isinstance(custom_dict[key], list):
            custom_dict[key] = to_custom_dict(custom_dict[key])

    return custom_dict


def get_new_token():
    url = urljoin(BASE_URL, 'token/new')
    params = {'api_key': API_KEY}
    return requests.get(url, params).json()['token']


def get_json(prefix, params=dict(), data=None, update_data=None):
    url = urljoin(BASE_URL, prefix)
    params.update({'token': get_new_token()})
    if data:
        response = requests.post(url, json=data, params=params)
    elif update_data:
        response = requests.put(url, update_data, params=params)
    else:
        response = requests.get(url, params)

    response.encoding = 'utf-8'
    if response.ok:
        return to_custom_dict(response.json())


def get_clients(**params):
    prefix = 'clients/'
    data = get_json(prefix, params).data
    return data


def get_client_by_phone_number(phone_number):
    clients = get_clients(**{'phones[]': phone_number})
    if clients:
        return clients[0]


def create_new_client(phone_number, name):
    cmd = "curl -X POST https://api.remonline.app/clients/"
    cmd += f' -d "token={get_new_token()}"'
    cmd += f' -d "name={name}"'
    cmd += f' -d "phone[]={phone_number}"'
    cmd += ' -d "ad_campaign_id=46048"'
    cmd += ''' -d "custom_fields={\\"887059\\": \\"\\"}\" '''
    file = NamedTemporaryFile()
    proc = subprocess.Popen(cmd, stdout=file, stderr=subprocess.PIPE)
    proc.wait()
    file.seek(0)
    return json.loads(file.read().decode('utf-8'))['data']['id']


def update_client(id, **data):
    prefix = 'clients'
    data.update({
        'id': id,
    })
    return get_json(prefix, update_data=data).success


def get_client_open_orders(rem_id):
    prefix = 'order/'
    params = {
        'sort_dir': 'desc',
        'clients_ids[]': rem_id,
    }
    data = get_json(prefix, params).data
    orders = list(filter(lambda order: order.status.group <= 5, data))
    return orders


def get_client_orders(rem_id, **params):
    prefix = 'order/'
    params.update({
        'sort_dir': 'desc',
        'clients_ids[]': rem_id,
    })
    return get_json(prefix, params).data
