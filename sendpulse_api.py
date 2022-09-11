from urllib.parse import urljoin

import requests

base_url = 'https://api.sendpulse.com'


def authorization(client_id: str, client_secret: str) -> dict:
    path = '/oauth/access_token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    response = requests.post(urljoin(base_url, path), json=payload)
    response.raise_for_status()
    return response.json()


def get_deals(token: str, pipeline_ids: list, step_ids: list,
              status_ids: list) -> list:
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
                "expression": "in",
                "value": step_ids,
            },
            {
                "name": "status",
                "expression": "in",
                "value": status_ids,
            },
        ]
    }
    response = requests.post(
        urljoin(base_url, path),
        headers=headers,
        json=payload,
    )
    response.raise_for_status()
    return response.json()['data']


def get_deal(token: str, deal_id: int) -> dict:
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
    return response.json()['data']


def delete_deal(token: str, deal_id: int) -> str:
    path = f'/crm/v1/deals/{deal_id}'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.delete(
        urljoin(base_url, path),
        headers=headers,
    )
    response.raise_for_status()
    return response.text


def get_pipelines(token: str) -> dict:
    path = '/crm/v1/pipelines'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(urljoin(base_url, path), headers=headers)
    response.raise_for_status()
    return response.json()


def get_contacts(token: str) -> dict:
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


def create_deal(token: str, pipeline_id: int, step_id: int,
                responsible_id: int, name: str, price: float, currency: str,
                source_id: str, contact_id: int) -> dict:
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


def get_users(token: str) -> dict:
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


def get_contact_details(token: str, contact_id: int) -> dict:
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


def change_deal_status(token: str, deal_id: int, deal_details: dict,
                       sp_final_status: int) -> dict:
    path = f'/crm/v1/deals/{deal_id}'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    payload = {
        'pipelineId': deal_details['pipelineId'],
        'status': sp_final_status,
        'stepId': deal_details['stepId'],
        'responsibleId': deal_details['responsibleId'],
        'name': deal_details['name'],
        'price': deal_details['price'],
        'currency': deal_details['currency'],
        'sourceId': deal_details['sourceId'],
        'order': deal_details['order'],
    }
    response = requests.put(
        urljoin(base_url, path), json=payload,
        headers=headers,
    )
    response.raise_for_status()
    return response.json()
