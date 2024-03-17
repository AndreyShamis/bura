import threading
import time


MAX_THREADS_ALLOWED = 3  # Set the maximum number of threads allowed
LOOP_MAX_TIME_WAIT = 2    # Maximum time (in seconds) to wait for a thread to become available



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

    def __del__(self):
        self.stop_all_threads()

    def start_thread(self, func, *args, **kwargs):
        start_time = time.time()
        while True:
            self.lock.acquire()
            if self.thread_count < MAX_THREADS_ALLOWED:
                thread = threading.Thread(target=self._thread_wrapper, args=(func, args, kwargs))
                thread.daemon = True
                self.threads.append(thread)
                self.thread_count += 1
                self.lock.release()
                thread.start()
                break
            self.lock.release()
            if time.time() - start_time > LOOP_MAX_TIME_WAIT:
                print("Maximum wait time exceeded. Unable to start a new thread.")
                break
            time.sleep(0.1)  # Add a small delay to avoid excessive CPU usage

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
        self.thread_count -= len(finished_threads)
        self.threads_executed += len(finished_threads)
        self.lock.release()

    def get_thread_count(self):
        return self.thread_count

    def get_threads_executed(self):
        return self.threads_executed


# Initialize ThreadManager instance
thread_manager = ThreadManager()
