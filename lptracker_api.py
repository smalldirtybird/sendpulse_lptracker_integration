import requests
from urllib.parse import urljoin


base_url = 'https://direct.lptracker.ru'


def authorization(login, password, service_name):
    path = '/login'
    payload = {
        "login": login,
        "password": password,
        "service": service_name,
        "version": "1.0",
    }
    response = requests.post(urljoin(base_url, path), json=payload)
    return response.json()


def create_person(token, project_id, name, profession=None, site=None,
                  fields=None, **kwargs):
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
    return response.json()['result']['id']


def search_contact(token, project_id, email=None, phone=None):
    path = '/contact/search'
    headers = {
        'token': token,
    }
    params = {
        'project_id': project_id,
        'phone': phone,
        'email': email,
    }
    response = requests.get(
        urljoin(base_url, path),
        params=params,
        headers=headers,
    )
    found = response.json()['result']
    return found[0]['id'] if found else None


def get_contact(token, contact_id):
    path = f'/contact/{contact_id}'
    headers = {
        'token': token,
    }
    response = requests.get(urljoin(base_url, path), headers=headers)
    return response.json()


def create_lead(token, name, contact_id=None, contact=None,
                callback=False):
    path = '/lead'
    headers = {
        'token': token,
    }
    payload = {
        "contact_id": contact_id,
        "contact": contact,
        "name": name,
        "callback": callback,
    }
    response = requests.post(
        urljoin(base_url, path),
        headers=headers,
        json=payload,
    )
    return response.json()


def get_leads(token, project_id):
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
    return response.json()


def get_projects(token):
    path = '/projects'
    headers = {
        'token': token
    }
    response = requests.get(urljoin(base_url, path), headers=headers)
    return response.json()
