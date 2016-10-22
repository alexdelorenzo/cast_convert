from concurrent.futures import ThreadPoolExecutor
from functools import partial
from os.path import getsize
from queue import Queue  # thread-safe queue
from time import sleep

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from .convert import convert_video
from .media_info import is_video
from .preferences import FILESIZE_CHECK_WAIT, THREADS, FFMPEG_PROCESSES


debug_print = partial(print, "DEBUG ->")


def wait_for_stable_size(filename: str, wait: float = FILESIZE_CHECK_WAIT, previous: int = None):
    while True:
        filesize = getsize(filename)

        if filesize == previous:
            return filesize

        previous = filesize
        sleep(wait)


def consume_video_queue(queue: Queue, threads: int = THREADS, debug: bool = False):
    while True:
        filename = queue.get()

        if debug:
            debug_print("Getting %s size..." % filename)

        filesize = wait_for_stable_size(filename)
        file_is_vid = is_video(filename)

        if debug:
            debug_print(filename, filesize)
            debug_print(filename, file_is_vid)

        if file_is_vid:
            print(convert_video(filename, threads=threads))

        else:
            print(filename, 'not a video.')


class AddedFileHandler(PatternMatchingEventHandler):
    def __init__(self, queue: Queue, *args, debug: bool = False, **kwargs):
        super().__init__(*args, ignore_directories=True, **kwargs)
        self.queue = queue
        self.debug = debug
        self.seen = set()

    def on_moved(self, event):
        filename = event.dest_path

        if self.debug:
            debug_print(event)
            debug_print(filename, 'seen', filename in self.seen)

        if filename not in self.seen:
            self.queue.put(filename)
            self.seen.add(filename)

    def on_created(self, event):
        filename = event.src_path

        if self.debug:
            debug_print(event)
            debug_print(filename, 'seen', filename in self.seen)

        if filename not in self.seen:
            self.queue.put(filename)
            self.seen.add(filename)


def watch_directory(directory: str,
                    ignore_patterns: tuple = tuple(),
                    threads: int = THREADS,
                    debug: bool = False):
    queue = Queue()
    thread_pool = ThreadPoolExecutor(FFMPEG_PROCESSES)
    converter_futures = [thread_pool.submit(consume_video_queue, queue, threads, debug)
                         for _ in range(FFMPEG_PROCESSES)]

    handler = AddedFileHandler(queue, ignore_patterns=ignore_patterns, debug=debug)
    observer = Observer()
    observer.schedule(handler, directory, recursive=True)
    observer.start()

    print("Watching %s for new videos..." % directory)

    try:
        while True:
            sleep(1)

    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        queue.join()
        thread_pool.shutdown(wait=0.1)
