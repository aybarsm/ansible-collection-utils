import time
import threading
from typing import (
    Callable, Iterable, Any, TypeVar, Generic, 
    List, Set, Dict, Sequence
)

JobId = TypeVar('JobId')
JobResult = Any
JobCallback = Callable[[], JobResult]
OnJobIdCallback = Callable[[JobResult], JobId]
OnStatusCallback = Callable[[JobId], bool]
OnCompleteCallback = Callable[[JobId], None]

class Channel(Generic[JobId]):
    def __init__(
        self,
        jobs: Iterable[JobCallback],
        on_job_id: OnJobIdCallback,
        on_status: OnStatusCallback,
        on_complete: OnCompleteCallback,
        poll: float = 1.0
    ):
        self.jobs: Sequence[JobCallback] = list(jobs)
        self.on_job_id = on_job_id
        self.on_status = on_status
        self.on_complete = on_complete
        self.poll = max(0.1, poll)

        self._lock = threading.Lock() 

        self.active_job_ids: List[JobId] = []
        self.finished_job_ids: Set[JobId] = set()
        self.job_start_results: Dict[JobId, JobResult] = {}
        self.failed_to_start_jobs: Set[str] = set()

    def wait(self):
        if not self.jobs:
            return
        
        self._start()

        with self._lock:
            if not self.active_job_ids:
                return
            
        self._poll()

    def _start(self):
        for job_callable in self.jobs:
            job_name = getattr(job_callable, '__name__', 'unknown_job')
            try:
                job_result = job_callable()
                job_id = self.on_job_id(job_result)

                with self._lock:
                    self.active_job_ids.append(job_id)
                    self.job_start_results[job_id] = job_result

            except Exception as e:
                with self._lock:
                    self.failed_to_start_jobs.add(job_name)

    def _poll(self):
        def get_active_job_count():
            with self._lock:
                return len(self.active_job_ids)

        while get_active_job_count() > 0:
            with self._lock:
                current_active_jobs = list(self.active_job_ids)

            for job_id in current_active_jobs:
                try:
                    is_finished = self.on_status(job_id)

                    if is_finished:
                        self._completed(job_id)
                except Exception as e:
                    raise RuntimeError(f"[ERROR] Failed to get status for job {job_id}: {e}")

            if get_active_job_count() > 0:
                time.sleep(self.poll)

    def _completed(self, job_id: JobId):
        try:
            self.on_complete(job_id)
        except Exception as e:
            raise RuntimeError(f"[ERROR] 'on_complete' callback failed for {job_id}: {e}")

        with self._lock:
            if job_id in self.active_job_ids:
                self.active_job_ids.remove(job_id)
                self.finished_job_ids.add(job_id)