from queue import Queue
from time import sleep

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from queue import Queue
from concurrent.futures import ThreadPoolExecutor as TPE

from .media_info import get_media_info
from .convert import convert_video


def is_video(path: str) -> bool:
    media_info = get_media_info(path)

    if 'codec_type' in media_info:
        return media_info['codec_type'] == 'video'

    return False


def consume_video_queue(queue: Queue):
    while True:
        video = queue.get()
        convert_video(video)


class AddedFileHandler(FileSystemEventHandler):
    def __init__(self, queue: Queue):
        self.queue = queue

    def on_created(self, event):
        if event.is_directory:
            return

        file = event.src_path

        if is_video(file):
            self.queue.put(file)


class TestHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(event, 'sleeping')
        sleep(5)
        print('woke up')


def watch_directory(dir: str):
    observer = Observer()
    queue = Queue()
    handler = AddedFileHandler(queue)
    thread_pool = TPE(1)
    future = thread_pool.submit(consume_video_queue, queue)

    observer.schedule(handler, dir, recursive=True)
    observer.start()

