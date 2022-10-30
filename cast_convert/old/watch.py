from concurrent.futures import ThreadPoolExecutor
from typing import Callable
from functools import partial
from os.path import getsize
from queue import Queue  # thread-safe queue
from time import sleep
import logging

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from .convert import convert_video
from .media_info import is_video
from .preferences import FILESIZE_CHECK_WAIT, THREADS, FFMPEG_PROCESSES


def debug(*items: str | int | bool):
  logging.debug(' '.join(items))


def exception(*items: str):
  logging.exception(' '.join(items))


def wait_for_stable_size(filename: str, wait: float = FILESIZE_CHECK_WAIT, previous: int = None):
  while True:
    try:
      filesize = getsize(filename)

      if filesize == previous:
        return filesize

      previous = filesize
      sleep(wait)

    except Exception as e:
      exception(e)
      previous = None


def consume_video_queue(queue: Queue, threads: int = THREADS, show_debug: bool = False):
  while True:
    filename = queue.get()

    if show_debug:
      debug("Getting %s size..." % filename)

    filesize = wait_for_stable_size(filename)

    if show_debug:
      debug(filename, filesize)
      debug("Determine if", filename, "is a video...")

    file_is_vid = is_video(filename)

    if show_debug:
      debug(filename, file_is_vid)
      debug("Converting video...")

    if file_is_vid:
      print(convert_video(filename, threads=threads))

    else:
      print(filename, 'not a video.')


class AddedFileHandler(PatternMatchingEventHandler):
  def __init__(self, queue: Queue, *args, show_debug: bool = False, **kwargs):
    super().__init__(*args, ignore_directories=True, **kwargs)
    self.queue = queue
    self.debug = show_debug
    self.seen = set()

  def on_moved(self, event):
    filename = event.dest_path

    if self.debug:
      debug(event)
      debug(filename, 'seen', filename in self.seen)

    if filename not in self.seen:
      self.queue.put(filename)
      self.seen.add(filename)

  def on_created(self, event):
    filename = event.src_path

    if self.debug:
      debug(event)
      debug(filename, 'seen', filename in self.seen)

    if filename not in self.seen:
      self.queue.put(filename)
      self.seen.add(filename)


def watch_directory(
  directory: str,
  ignore_patterns: tuple = tuple(),
  threads: int = THREADS,
  show_debug: bool = False
):
  queue = Queue()
  thread_pool = ThreadPoolExecutor(FFMPEG_PROCESSES)
  futures = [
    thread_pool.submit(consume_video_queue, queue, threads, show_debug)
    for _ in range(FFMPEG_PROCESSES)
  ]

  handler = AddedFileHandler(queue, ignore_patterns=ignore_patterns, show_debug=show_debug)
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
