import os
import logging

import requests
from requests.exceptions import HTTPError

logger = logging.getLogger('app_logger')


class PyrusAccount:
    def __init__(self, login, secret_key):
        url = 'https://api.pyrus.com/v4/auth'
        params = {
            'login': login,
            'security_key': secret_key,
        }
        try:
            response = requests.get(url, params=params)
            response_data = response.json()
            response.raise_for_status()
            self.token = response_data.get('access_token')
        except HTTPError as e:
            logger.debug(str(e))

    def get_task(self, task_id):
        url = f"https://api.pyrus.com/v4/tasks/{task_id}"
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        task = response_data.get('task')
        return task

    def get_lists(self):
        url = "https://api.pyrus.com/v4/lists"
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        lists = response_data.get('lists')
        return lists

    def get_planed_tasks(self):
        '''Возвращает все задачи из списка "Plan"'''
        plan_list_id = None
        for lst in self.get_lists():
            if lst.get('name').lower() == 'plan':
                plan_list_id = lst.get('id')

        url = f"https://api.pyrus.com/v4/lists/{plan_list_id}/tasks"
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        tasks = [self.get_task(task.get('id')) for task in response_data.get('tasks', [])]
        return tasks

    def get_inbox(self):
        url = "https://api.pyrus.com/v4/inbox"
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        inbox_tasks = response_data.get('tasks')
        return inbox_tasks

    def get_contacts(self):
        '''возвращает список доступных пользователю контактов'''
        url = "https://api.pyrus.com/v4/contacts"
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        organizations = response_data.get('organizations')
        persons = organizations[0].get('persons')
        return persons

    def update_task(self, task_id, **kwargs):
        url = f"https://api.pyrus.com/v4/tasks/{task_id}/comments"
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        response = requests.post(url, headers=headers, json=kwargs)
        response.raise_for_status()
        return response.json()

    def fetch_related_tasks(self, task):
        related_task_ids = task.get('linked_task_ids')
        if not related_task_ids:
            return
        related_tasks = [self.get_task(task_id) for task_id in related_task_ids]
        return related_tasks

    def locate_plan_list(self):
        '''Возвращает ID списка "Plan"'''
        url = "https://api.pyrus.com/v4/lists"
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        lists = response_data.get('lists', [])
        for lst in lists:
            if lst.get('name', '') == 'Plan':
                return lst.get('id')

    def clear_plan_list(self):
        '''Очищает список "Plan"'''
        tasks = self.get_planed_tasks()
        plan_list_id = self.locate_plan_list()
        for task in tasks:
            self.update_task(task.get('id'), removed_list_ids=[plan_list_id])
