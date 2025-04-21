import requests
import os
import time


def get_folder_path(absolute_path, prefix_to_remove):
    if not os.path.isdir(prefix_to_remove):
        raise ValueError(f"{prefix_to_remove} is not a directory")
    if prefix_to_remove[-1] != '/':
        prefix_to_remove += '/'

    if absolute_path.startswith(prefix_to_remove):
        relative_path = absolute_path[len(prefix_to_remove):]
    else:
        raise ValueError(f"The prefix {prefix_to_remove} is incorrect for file {absolute_path}")

    folder_path = os.path.dirname(relative_path)

    return folder_path


class SubmittedJob:
    def __init__(self, result_path: str, status: bool, message=''):
        self.result_path = result_path
        self.status = status
        self.message = message


class KBPort:
    def __init__(self, username: str, token: str, url: str):
        self.url = url
        if not self.url.endswith("/"):
            self.url += "/"
        self.username = username
        self.token = token

    def single_parse_job(self, file_path, result_dir=''):
        if not os.path.isfile(file_path):
            raise Exception(f'File {file_path} not found')
        if result_dir != '' and result_dir[0] == '/':
            raise ValueError('File folder should not start with "/"')
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'username': self.username, 'token': self.token, 'folder': result_dir}
            response = requests.post(self.url + 'pdf_parse', files=files, data=data)
            if response.status_code == 200:
                return SubmittedJob(os.path.join(result_dir, os.path.basename(file_path)), True)
            elif response.status_code == 500:
                return SubmittedJob(os.path.join(result_dir, os.path.basename(file_path)), False, message=response.json()['error'])
            else:
                return SubmittedJob(os.path.join(result_dir, os.path.basename(file_path)), False, message=response.json()['message'])

    def batch_parse_job(self, file_batch, result_dir='', base_path=None):
        if result_dir != '' and result_dir[0] == '/':
            raise ValueError('File folder should not start with "/"')
        process_files = []
        if not os.path.isfile(file_batch):
            raise Exception('Parsing file batch not found')
        with open(file_batch, 'r') as f:
            file_list = f.readlines()
            for file_path in file_list:
                file_path = file_path.strip()
                if len(file_path) == 0:
                    continue
                file_folder_full = result_dir
                if base_path != None:
                    file_folder_full = os.path.join(result_dir, get_folder_path(file_path, base_path))
                try:
                    submit_result = self.single_parse_job(file_path, result_dir=file_folder_full)
                    process_files.append(submit_result)
                except Exception as e:
                    process_files.append(SubmittedJob(os.path.join(file_folder_full, os.path.basename(file_path)), False, message=e))

        return process_files

    def get_job_status(self, result_path: str):
        data = {'file_path': result_path, 'username': self.username, 'token': self.token}
        response = requests.get(self.url + 'status', data=data)
        if response.status_code == 200:
            job_status = {}
            job_status['status'] = response.json()['status']
            job_status['message'] = response.json()['message']
            return job_status
        elif response.status_code == 500:
            raise Exception(response.json())
        else:
            raise Exception(response.json())

    def get_job_result(self, result_path: str):
        headers = {'Accept-Encoding': 'gzip'}
        data = {'file_path': result_path, 'username': self.username, 'token': self.token}
        response = requests.get(self.url + 'get_result', headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise Exception(response.json()['error'])
        else:
            raise Exception(response.json()['message'])

    def polling_job_result(self, result_path: str, time_out=7200):
        start_time = time.time()
        started = False
        while True:
            status = self.get_job_status(result_path)
            if status['status'] == "started":
                if not started:
                    started = True
                    start_time = time.time()
                time.sleep(5)
            elif status['status'] == "queued":
                time.sleep(5)
            elif status['status'] == "finished":
                return self.get_job_result(result_path)
            elif status['status'] == "failed":
                raise Exception(f"Job {result_path} failed with error: {status['message']}")
            elif status['status'] == "cancelled":
                return
            else:
                raise Exception(f'Job {result_path} status unknown')
            if time.time() - start_time > time_out:
                raise Exception(f'Job {result_path} timeout')

    def get_all_status(self):
        all_status = []
        data = {'username': self.username, 'token': self.token}
        response = requests.get(self.url + 'all_status', data=data)
        if response.status_code == 200:
            status_json = response.json()
            for file, file_stat in status_json.items():
                job_stat = {}
                job_stat['result_path'] = file
                job_stat['status'] = file_stat[0]
                job_stat['message'] = file_stat[1]
                all_status.append(job_stat)
            return all_status
        elif response.status_code == 500:
            raise Exception(response.json()['error'])
        else:
            raise Exception(response.json()['message'])

    def delete_result(self, result_path: str):
        data = {'file_path': result_path, 'username': self.username, 'token': self.token}
        response = requests.delete(self.url + 'delete', data=data)
        if response.status_code == 200:
            return True
        elif response.status_code == 500:
            raise Exception(response.json()['error'])
        else:
            raise Exception(response.json()['message'])

    def cancel_job(self):
        data = {'username': self.username, 'token': self.token}
        response = requests.post(self.url + 'cancel_parse', data=data)
        if response.status_code == 200:
            return True
        elif response.status_code == 500:
            raise Exception(response.json()['error'])
        else:
            raise Exception(response.json()['message'])
