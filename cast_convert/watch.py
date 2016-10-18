from concurrent.futures import ThreadPoolExecutor as TPE
from queue import Queue
from time import sleep, time

from os.path import getsize
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .media_info import is_video
from .convert import convert_video


SIZE_CHECK_WAIT = 1


def file_size_stable(filename: str, wait: float = SIZE_CHECK_WAIT, previous: int = -1):
    while True:
        sleep(wait)

        filesize = getsize(filename)

        if filesize == previous:
            return

        previous = filesize


def consume_video_queue(queue: Queue):
    seen = set()

    while True:
        filename = queue.get()

        if filename in seen:
            continue

        file_size_stable(filename)

        if is_video(filename):
            print(convert_video(filename))

        else:
            print(filename, 'not video')

        seen.add(filename)


class AddedFileHandler(FileSystemEventHandler):
    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue

    def on_modified(self, event):
        if event.is_directory:
            return

        self.queue.put(event.src_path)

    def on_moved(self, event):
        self.on_modified(event)

    def on_created(self, event):
        self.on_modified(event)


def watch_directory(directory: str):
    observer = Observer()
    queue = Queue()
    handler = AddedFileHandler(queue)

    thread_pool = TPE(1)
    converter_future = thread_pool.submit(consume_video_queue, queue)

    observer.schedule(handler, directory, recursive=True)
    observer.start()

    try:
        while True:
            sleep(1)

    except KeyboardInterrupt:
        observer.stop()

    try:
        observer.join()
        queue.join()
        converter_future.cancel()
        thread_pool.shutdown(wait=0.1)

    except KeyboardInterrupt:
        exit()

