from urllib.parse import urljoin

import requests

base_url = 'https://direct.lptracker.ru'


def authorization(login: str, password: str, service_name: str) -> dict:
    path = '/login'
    payload = {
        'login': login,
        'password': password,
        'service': service_name,
        'version': '1.0',
    }
    response = requests.post(urljoin(base_url, path), json=payload)
    return response.json()


def get_projects(token):
    path = f'/projects'
    headers = {
        'token': token,
    }
    response = requests.get(urljoin(base_url, path), headers=headers)
    return response.json()


def create_person(token: str, project_id: int, name: str,
                  profession: str = None, site: str = None,
                  fields: dict = None,
                  **kwargs) -> int:
    path = '/contact'
    headers = {
        'token': token,
    }
    payload = {
        'project_id': project_id,
        'name': name,
        'profession': profession,
        'site': site,
        'details': [],
        'fields': fields,
    }
    for detail_type, detail_data in kwargs.items():
        payload['details'].append(
            {
                'type': detail_type,
                'data': detail_data,
            }
        )
    response = requests.post(
        urljoin(base_url, path),
        headers=headers,
        json=payload,
    )
    person_created = response.json()
    if person_created['status'] == 'success':
        return response.json()['result']['id']


def search_contact(token: str, project_id: int, phone: int = None) -> int:
    path = '/contact/search'
    headers = {
        'token': token,
    }
    params = {
        'project_id': project_id,
        'phone': phone,
    }
    response = requests.get(
        urljoin(base_url, path),
        params=params,
        headers=headers,
    )
    found = response.json()
    if found['status'] == 'success' and found['result']:
        return found['result'][0]['id']


def get_contact(token: str, contact_id: int) -> dict:
    path = f'/contact/{contact_id}'
    headers = {
        'token': token,
    }
    response = requests.get(urljoin(base_url, path), headers=headers)
    return response.json()


def delete_contact(token: str, contact_id: int) -> dict:
    path = f'/contact/{contact_id}'
    headers = {
        'token': token,
    }
    response = requests.delete(urljoin(base_url, path), headers=headers)
    return response.json()


def get_funnel_steps(token: str, project_id: int) -> dict:
    path = f'/project/{project_id}/funnel'
    headers = {
        'token': token,
    }
    response = requests.get(urljoin(base_url, path), headers=headers)
    return response.json()


def create_lead(token: str, name: str, contact_id: int = None,
                callback: bool = False, funnel_id: int = None,
                lead_owner_id: int = 0) -> dict:
    path = '/lead'
    headers = {
        'token': token,
    }
    payload = {
        'contact_id': contact_id,
        'name': name,
        'callback': callback,
        'funnel': funnel_id,
        'owner': lead_owner_id
    }
    response = requests.post(
        urljoin(base_url, path),
        headers=headers,
        json=payload,
    )
    return response.json()


def get_leads(token: str, project_id: int) -> dict:
    path = f'/lead/{project_id}/list'
    headers = {
        'token': token,
    }
    params = {
        'sort[created_at]': '3',
    }
    response = requests.get(
        urljoin(base_url, path),
        params=params,
        headers=headers,
    )
    return response.json()['result']


def get_projects(token: str) -> dict:
    path = '/projects'
    headers = {
        'token': token
    }
    response = requests.get(urljoin(base_url, path), headers=headers)
    return response.json()


def get_users(token: str) -> dict:
    path = '/staff'
    headers = {
        'token': token
    }
    response = requests.get(urljoin(base_url, path), headers=headers)
    return response.json()['result']


def change_lead_owner(token: str, lead_id: int, lead_owner_id: int):
    path = f'/lead/{lead_id}/owner'
    headers = {
        'token': token,
    }
    payload = {
        'owner': lead_owner_id
    }
    response = requests.put(
        urljoin(base_url, path),
        headers=headers,
        json=payload,
    )
    response.raise_for_status()
    return response.json()
