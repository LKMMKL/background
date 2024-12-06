
import asyncio
import sys
import threading

import concurrent.futures


class ThreadMain:
    __instance = None
    __lock = threading.Lock()

    @staticmethod
    def get_instance():
        ThreadMain.__lock.acquire()

        if ThreadMain.__instance is None:
            ThreadMain.__instance = ThreadMain()

        ThreadMain.__lock.release()
        return ThreadMain.__instance

    def __init__(self):
        if ThreadMain.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.loop = None
            self.server = None
            self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)
            super().__init__()

    def _start_interval(self):
        # https://stackoverflow.com/questions/44633458/why-am-i-getting-notimplementederror-with-async-and-await-on-windows/44639711
        if sys.platform == 'win32':
            self.loop = asyncio.ProactorEventLoop()
        else:
            self.loop = asyncio.new_event_loop()

        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    def start(self):
        threading.Thread(target=self._start_interval).start()
