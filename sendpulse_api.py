import requests
from urllib.parse import urljoin


base_url = 'https://api.sendpulse.com'


def authorization(client_id, client_secret):
    path = '/oauth/access_token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    response = requests.post(urljoin(base_url, path), json=payload)
    response.raise_for_status()
    return response.json()


def get_deals(token, pipeline_ids, step_id, status):
    path = '/crm/v1/deals/get-list'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    payload = {
        "order_by": 'id',
        "sort": "asc",
        "pipelineIds": pipeline_ids,
        "filter": [
            {
                "name": "stepId",
                "expression": "eq",
                "value": step_id,
            },
            {
                "name": "status",
                "expression": "eq",
                "value": status,
            },
        ]
    }
    response = requests.post(
        urljoin(base_url, path),
        headers=headers,
        json=payload,
    )
    response.raise_for_status()
    return response.json()


def get_deal(token, deal_id):
    path = f'/crm/v1/deals/{deal_id}'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(
        urljoin(base_url, path),
        headers=headers,
    )
    response.raise_for_status()
    # return response.json()['data']
    return response.text


def get_pipelines(token):
    path = '/crm/v1/pipelines'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(urljoin(base_url, path), headers=headers)
    response.raise_for_status()
    return response.json()


def get_contacts(token):
    path = '/crm/v1/contacts/get-list'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.post(
        urljoin(base_url, path),
        headers=headers,
    )
    response.raise_for_status()
    return response.json()


def create_deal(token, pipeline_id, step_id, responsible_id, name, price,
                currency, source_id, contact_id):
    path = '/crm/v1/deals'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    payload = {
        'pipelineId': pipeline_id,
        'stepId': step_id,
        'responsibleId': responsible_id,
        'name': name,
        'price': price,
        'currency': currency,
        'sourceId': source_id,
        'contact': {
            'id': contact_id
        }
    }
    response = requests.post(
        urljoin(base_url, path),
        headers=headers,
        json=payload,
    )
    response.raise_for_status()
    return response.json()


def get_users(token):
    path = '/crm/v1/users'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(
        urljoin(base_url, path),
        headers=headers,
    )
    response.raise_for_status()
    return response.json()


def get_contact_details(token, contact_id):
    path = f'/crm/v1/contacts/{contact_id}'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(
        urljoin(base_url, path),
        headers=headers,
    )
    response.raise_for_status()
    return response.json()['data']
