import time, threading
import typing as T
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.task import Task, TaskCollection, TaskId, JobCollection
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.fluent import Fluent

class Concurrent(object):
    def __init__(self, tasks: TaskCollection):
        self.data: Fluent = Fluent()
        self.tasks: TaskCollection = tasks

        self._lock = threading.Lock()
        self.jobs: JobCollection = self.tasks.get_job_collection()

    def wait(self):
        if self.tasks.empty():
            return
        
        self._start()

        with self._lock:
            if not self.jobs.has_active():
                return
            
        self._poll()

    def _start(self):
        for task in self.tasks.all():
            job_id = self._get_job_id(job_callable)
            job_alias = getattr(job_callable, '__alias__')
            try:
                job_result = job_callable(job_id, self)
                if self.on_start:
                    self.on_start(job_id, job_result, self)

                with self._lock:
                    self.active_jobs.append(job_id)
                    self.job_aliases[job_id] = job_alias

            except Exception as e:
                with self._lock:
                    self.failed_jobs.add(job_id)

    def _poll(self):
        def has_active_jobs():
            with self._lock:
                return self.jobs.has_active()

        while has_active_jobs():
            with self._lock:
                active_jobs = list(self.jobs.active)

            for task_id in active_jobs:
                if not 
                try:
                    is_finished = self.on_status(job_id, self)

                    if is_finished:
                        self._completed(job_id)
                except Exception as e:
                    message = f"[ERROR] Failed to get status for job {job_id}"
                    
                    job_alias = self.get_job_alias(job_id)
                    if Validate.filled(job_alias):
                        message += f"[{job_alias}]"
                    
                    raise RuntimeError(f"{message}: {e}")

            if get_active_job_count() > 0:
                time.sleep(self.poll)

    def _completed(self, job_id: JobId):
        if self.on_complete == None:
            return
        
        try:
            self.on_complete(job_id, self)
        except Exception as e:
            message = f"[ERROR] 'on_complete' callback failed for {job_id}"
            
            job_alias = self.get_job_alias(job_id)
            if Validate.filled(job_alias):
                message += f"[{job_alias}]"
            
            raise RuntimeError(f"{message}: {e}")

        with self._lock:
            if job_id in self.active_jobs:
                self.active_jobs.remove(job_id)
                self.completed_jobs.add(job_id)
