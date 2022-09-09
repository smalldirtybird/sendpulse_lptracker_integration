import requests
from urllib.parse import urljoin


base_url = 'https://direct.lptracker.ru'


def authorization(login, password, service_name):
    path = '/login'
    payload = {
        'login': login,
        'password': password,
        'service': service_name,
        'version': '1.0',
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
    person_created = response.json()
    if person_created['status'] == 'success':
        return response.json()['result']['id']


def search_contact(token, project_id, phone=None):
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
    found = response.json()['result']
    return found[0]['id'] if found else None


def get_contact(token, contact_id):
    path = f'/contact/{contact_id}'
    headers = {
        'token': token,
    }
    response = requests.get(urljoin(base_url, path), headers=headers)
    return response.json()


def get_funnel_steps(token, project_id):
    path = f'/project/{project_id}/funnel'
    headers = {
        'token': token,
    }
    response = requests.get(urljoin(base_url, path), headers=headers)
    return response.json()


def create_lead(token, name, contact_id=None, callback=False,
                funnel_id=None, lead_owner_id=0):
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


def get_users(token):
    path = '/staff'
    headers = {
        'token': token
    }
    response = requests.get(urljoin(base_url, path), headers=headers)
    return response.json()