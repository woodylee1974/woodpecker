import os
from utils.kbport import KBPort
from utils.file_man import UPLOAD_DIR, collect_pdf_files
import threading
import json
import time

KBPORT_URL = os.environ.get("KBPORT_URL")
scan_api = KBPort("woodpecker", "111", KBPORT_URL)


class FileStatus:
    def __init__(self):
        self.file_status = {}
        self.work_lock = threading.Lock()

    def collect(self):
        with self.work_lock:
            self.file_status = {}
            pdf_files = collect_pdf_files()
            for pdf_file, scaned_pdf_file in pdf_files:
                self.file_status[pdf_file] = {
                    'name': os.path.basename(pdf_file),
                    'fullname': pdf_file,
                    'scaned_file': scaned_pdf_file,
                    'scan_key': None,
                    'status': {
                        'state': 'pending',
                        'message': '发现待扫描的文件!'
                    },
                    'progress': 0
                }
                if os.path.exists(scaned_pdf_file):
                    self.file_status[pdf_file]['status'] = {
                        'state': 'completed',
                        'message': '发现已扫描的文件!'
                    }
                    g_file_status.file_status[pdf_file]['progress'] = 100


g_file_status = FileStatus()
work_thread = None


def collect_files():
    g_file_status.collect()


def start_scan():
    global work_thread
    if work_thread is None:
        start_scan_loop()


def get_scan_status():
    """
        'files': [
        {
            'name': "file1",
            "status": {'state':"pending", 'message': "waiting"},
            "progress": 10
        },
    """
    files = []
    status = []
    for scan_obj in g_file_status.file_status.values():
        files.append({
            'name': os.path.basename(scan_obj['name']),
            'status': scan_obj['status'],
            'progress': scan_obj['progress']
        })
        status.append(1 if scan_obj['status']['state'] == 'completed' else 0)
    return {
        "files": files,
        "partial_done": sum(status) > 1,
        "all_done": all(status)
    }


def scan_loop():
    while True:
        with g_file_status.work_lock:
            pdf_files = list(g_file_status.file_status.keys())

        if pdf_files:
            for pdf_file in pdf_files:
                with g_file_status.work_lock:
                    if pdf_file not in g_file_status.file_status:
                        break
                    scan_obj = g_file_status.file_status[pdf_file]
                    if scan_obj['status']['state'] == 'completed':
                        continue
                    if os.path.exists(scan_obj['scaned_file']):
                        g_file_status.file_status[pdf_file]['status'] = {
                            'state': 'completed',
                            'message': '发现已扫描的文件!'
                        }
                        g_file_status.file_status[pdf_file]['progress'] = 100
                    elif g_file_status.file_status[pdf_file]['scan_key'] is None:
                        job = scan_api.single_parse_job(pdf_file, "result")
                        if job is not None:
                            if job.status:
                                g_file_status.file_status[pdf_file]['scan_key'] = job.result_path
                                print(f"commit job: {job.result_path}")
                                g_file_status.file_status[pdf_file]['status'] = {
                                    'state': 'pending',
                                    'message': '已将待扫描文件入队...'
                                }
                                g_file_status.file_status[pdf_file]['progress'] = 0
                    else:
                        print(f"1:scanobj_scan_key={scan_obj['scan_key']}")
                        status = scan_api.get_job_status(scan_obj['scan_key'])
                        print(f"2:scanobj_scan_key={scan_obj['scan_key']}, status={status['status']}")
                        if status['status'] == "started":
                            progress = json.loads(status['message'])
                            stage = progress.get("stage", None)
                            page = progress.get("page_id", 0)
                            total = progress.get("total_page", 1)
                            if page < 0:
                                page = 0
                            if stage is None:
                                desc = "扫描状态未知"
                            else:
                                desc = f"扫描阶段: {stage} [{page} / {total}]"
                            if total > 0:
                                progress = int(page / total * 100)
                            else:
                                progress = 0
                            g_file_status.file_status[pdf_file]['status'] = {
                                'state': 'progressing',
                                'message': desc
                            }
                            g_file_status.file_status[pdf_file]['progress'] = progress
                        elif status['status'] == 'finished':
                            print(f"3:scanobj_scan_key={scan_obj['scan_key']}")
                            json_data = scan_api.get_job_result(scan_obj['scan_key'])
                            print(f"4:scanobj_scan_key={scan_obj['scan_key']}")
                            with open(scan_obj['scaned_file'], "w") as f:
                                json.dump(json_data, f)
                                print(f"5:scanobj_scan_key={scan_obj['scan_key']}")
                            g_file_status.file_status[pdf_file]['status'] = {
                                'state': 'completed',
                                'message': "扫描完成！"
                            }
                            g_file_status.file_status[pdf_file]['progress'] = 100

                        elif status['status'] == 'failed':
                            g_file_status.file_status[pdf_file]['status'] = {
                                'state': 'error',
                                'message': status['message']
                            }
                time.sleep(0.5)
                print("tick")
        else:
            time.sleep(1)


def start_scan_loop():
    global work_thread
    work_thread = threading.Thread(target=scan_loop)
    work_thread.start()





