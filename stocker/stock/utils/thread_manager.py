import threading
import time


class ThreadManager:
    threads = []
    def __init__(self):
        self.threads = []
        self.thread_count = 0
        self.threads_executed = 0
        self.lock = threading.Lock()

    def start_thread(self, func, *args, **kwargs):
        thread = threading.Thread(target=self._thread_wrapper, args=(func, args, kwargs))
        self.lock.acquire()
        self.threads.append(thread)
        self.thread_count += 1
        self.lock.release()
        thread.start()

    def _thread_wrapper(self, func, args, kwargs):
        func(*args, **kwargs)
        self.lock.acquire()
        self.threads.remove(threading.current_thread())
        self.thread_count -= 1
        self.threads_executed += 1
        self.lock.release()

    def stop_all_threads(self):
        for thread in self.threads:
            thread.join()

    def get_thread_count(self):
        return self.thread_count

    def get_threads_executed(self):
        return self.threads_executed


# Initialize ThreadManager instance
thread_manager = ThreadManager()
