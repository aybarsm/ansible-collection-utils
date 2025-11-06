import time
import threading
from typing import (
    Callable, Iterable, Any, TypeVar, Generic, 
    List, Set, Dict, Sequence, Optional, Mapping
)
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Data, Helper, Str, Fluent, Validate

JobAlias = str
JobId = str
JobResult = Any
JobCallback = Callable[[JobId, 'Channel'], JobResult]
OnStartCallback = Optional[Callable[[JobId, JobResult, 'Channel'], None]]
OnStatusCallback = Callable[[JobId, 'Channel'], bool]
OnCompleteCallback = Optional[Callable[[JobId, 'Channel'], None]]

class Channel():
    def __init__(
        self,
        on_status: OnStatusCallback,
        on_start: OnStartCallback = None,
        on_complete: OnCompleteCallback = None,
        jobs: Iterable[JobCallback] = [],
        poll: float = 5.0,
        manager = None
    ):
        self.jobs: list[JobCallback] = list(jobs)
        self.poll = max(0.1, poll)

        self.on_start = on_start
        self.on_status = on_status
        self.on_complete = on_complete

        self.manager = manager

        self.data = Fluent()

        self._lock = threading.Lock()
        self.active_jobs: List[JobId] = []
        self.completed_jobs: Set[JobId] = set()
        self.failed_jobs: Set[JobId] = set()
        self.job_aliases: Dict[JobId, Optional[JobAlias]] = {}

    def wait(self):
        if not self.jobs:
            return
        
        self._start()

        with self._lock:
            if not self.active_jobs:
                return
            
        self._poll()

    def _start(self):
        for job_callable in self.jobs:
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
        def get_active_job_count():
            with self._lock:
                return len(self.active_jobs)

        while get_active_job_count() > 0:
            with self._lock:
                current_active_jobs = list(self.active_jobs)

            for job_id in current_active_jobs:
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
    
    @staticmethod
    def _get_job_id(JobCallback)-> JobId:
        return 'job_' + str(id(JobCallback))
    
    def get_job_alias(self, job_id: JobId)-> Optional[JobAlias]:
        return self.job_aliases.get(job_id)

    @staticmethod
    def make(**kwargs):
        manager = kwargs.get('manager')
        if Validate.filled(manager):
            if Validate.blank(kwargs.get('on_start')):
                kwargs['on_start'] = manager_on_job_start
            
            if Validate.blank(kwargs.get('on_status')):
                kwargs['on_status'] = manager_on_job_status
            
            if Validate.blank(kwargs.get('on_complete')):
                kwargs['on_complete'] = ansible_on_job_complete
        
        return Channel(**kwargs)

def manager_on_job_start(job_id: JobId, job: JobResult, channel: Channel):
    channel.data.set(f'jobs.{job_id}', Helper.copy(job))

def manager_on_job_status(job_id: JobId, channel: Channel)-> bool:
    job_alias = channel.get_job_alias(job_id)
    job = channel.data.get(f'jobs.{job_id}', {})
    result = channel.manager._async_status(job) #type: ignore
    is_finished = Validate.truthy(Data.get(result, 'finished'))
    
    if is_finished:
        job_alias = channel.job_aliases.get(job_id)
        result_key = job_alias if Validate.filled(job_alias) else job_id
        channel.data.set(f'result.{result_key}', Helper.copy(result))

    return is_finished

def ansible_on_job_complete(job_id: JobId, channel: Channel)-> None:
    job = channel.data.get(f'jobs.{job_id}', {})
    channel.manager._async_cleanup(job) #type: ignore