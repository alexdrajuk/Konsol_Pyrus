import os

import requests


def pyrus_auth(login, security_key):
    url = "https://api.pyrus.com/v4/auth"
    params = {
        'login': login,
        'security_key': security_key,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    response_data = response.json()
    access_token = response_data.get('token')
    return access_token


def get_task(taks_id, token):
    url = f"https://api.pyrus.com/v4/tasks/{taks_id}"
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response_data = response.json()
    task = response_data.get('task')
    return task


def get_lists(token):
    url = "https://api.pyrus.com/v4/lists"
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response_data = response.json()
    lists = response_data.get('lists')
    return lists


def get_tasks_from_list(token, list_id, item_count=200, include_archived='n'):
    url = f"https://api.pyrus.com/v4/lists/{list_id}/tasks"
    headers = {
        'Authorization': f'Bearer {token}',
    }
    params = {
        'item_count': item_count,
        'include_archived': 'n',
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    response_data = response.json()
    tasks = response_data.get('tasks')
    return tasks


def get_inbox(token, item_count=50):
    url = "https://api.pyrus.com/v4/inbox"
    headers = {
        'Authorization': f'Bearer {token}',
    }
    params = {
        'item_count': item_count,
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    response_data = response.json()
    inbox_tasks = response_data.get('tasks')
    return inbox_tasks


def get_contacts(token):
    '''Fetch persons data from only first organisation'''
    url = "https://api.pyrus.com/v4/contacts"
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response_data = response.json()
    organizations = response_data.get('organizations')
    persons = organizations[0].get('persons')
    return persons


def update_task(token, task_id, **kwargs):
    url = f"https://api.pyrus.com/v4/tasks/{task_id}/comments"
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.post(url, headers=headers, json=kwargs)
    response.raise_for_status()
    return response.json()
