import threading
import time


class ThreadManager:
    threads = []
    def __init__(self):
        self.threads = []
        self.thread_count = 0
        self.threads_executed = 0
        self.lock = threading.Lock()
        # Start a separate thread for periodic cleanup
        self.cleanup_thread = threading.Thread(target=self._periodic_cleanup)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()

    def start_thread(self, func, *args, **kwargs):
        thread = threading.Thread(target=self._thread_wrapper, args=(func, args, kwargs))
        thread.daemon = True
        self.lock.acquire()
        self.threads.append(thread)
        self.thread_count += 1
        self.lock.release()
        thread.start()

    def _thread_wrapper(self, func, args, kwargs):
        try:
            func(*args, **kwargs)
        finally:
            self.close_finished_threads()

    def _periodic_cleanup(self):
        while True:
            self.close_finished_threads()
            time.sleep(0.001)  # Adjust the interval as needed

    def stop_all_threads(self):
        self.lock.acquire()

        for thread in self.threads:
            thread.join(0)
            self.threads.remove(thread)
            self.thread_count -= 1
            self.threads_executed += 1
        self.lock.release()
        
    def close_finished_threads(self):
        self.lock.acquire()
        finished_threads = [thread for thread in self.threads if not thread.is_alive()]
        for thread in finished_threads:
            self.threads.remove(thread)
            self.thread_count -= 1
            self.threads_executed += 1
        self.lock.release()

    def get_thread_count(self):
        return self.thread_count

    def get_threads_executed(self):
        return self.threads_executed


# Initialize ThreadManager instance
thread_manager = ThreadManager()
