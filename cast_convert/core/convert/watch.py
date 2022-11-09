import logging
import os
import asyncio
from asyncio import sleep, Queue, to_thread, BoundedSemaphore, TaskGroup
from dataclasses import dataclass, field
from logging import exception
from pathlib import Path
from typing import AsyncGenerator, AsyncIterable, Final

from aiopath import AsyncPath
from watchfiles import awatch, Change
from hachiko.hachiko import AIOEventHandler
from watchdog.events import PatternMatchingEventHandler
from watchdog.utils.patterns import match_any_paths

from cast_convert.cli.helpers import DEFAULT_MODEL, _convert
from cast_convert.core.model.device import Device
from cast_convert.core.model.video import Video


FILESIZE_CHECK_WAIT: Final[float] = 2.0
DEFAULT_THREADS: Final[int] = 2


async def wait_for_stable_size(
  file: str | Path,
  wait: float = FILESIZE_CHECK_WAIT,
  previous: int = None,
) -> int:
  path = AsyncPath(file)
  previous: int | None

  while True:
    try:
      result = await path.stat()
      size: int = result.st_size

      if size == previous:
        return size

      previous = size
      await sleep(wait)

    except Exception as e:
      exception(e)
      previous = None


async def is_video(path: Path) -> bool:
  try:
    await asyncio.to_thread(Video.from_path, path)

  except Exception as e:
    logging.exception(e)
    logging.error(f'Not a video: {path}')
    return False

  return True


async def gen_videos(
  *paths: Path,
  seen: set[Path] | None = None
) -> AsyncIterable[Path]:
  if seen is None:
    seen = set[Path]()

  async for changes in awatch(*paths):
    for change, file in changes:
      path = Path(file)

      if path in seen:
        continue

      seen.add(path)

      match change:
        case Change.added | Change.modified:
          if await is_video(path):
            yield path


async def convert(
  device: str,
  path: Path,
  sem: BoundedSemaphore,
):
  path = path.absolute()

  async with sem:
    await wait_for_stable_size(path)
    await to_thread(_convert, device, path)


async def convert_videos(
  *paths: Path,
  device: str = DEFAULT_MODEL,
  seen: set[Path] | None = None,
  threads: int = DEFAULT_THREADS,
):
  if seen is None:
    seen = set[Path]()

  sem = BoundedSemaphore(threads)

  async with TaskGroup() as tg:
    async for path in gen_videos(*paths, seen=seen):  # type: ignore
      coro = convert(device, path, sem)
      tg.create_task(coro)


### watchdog ###

@dataclass
class AddedFileHandler(
  AIOEventHandler
):
  patterns: list[str] | None = None
  excluded: list[str] | None = None
  case_sensitive: bool = True
  seen: set[Path] = field(default_factory=set[Path])
  debug: bool = False
  queue: Queue = field(default_factory=Queue)

  def matches(self, *paths: Path) -> bool:
    return match_any_paths(
      paths,
      included_patterns=self.patterns,
      excluded_patterns=self.excluded,
      case_sensitive=self.case_sensitive,
    )

  def dispatch(self, event):
    logging.debug(f'Handling {event}')
    paths: list[str] = []

    if hasattr(event, 'dest_path'):
      paths.append(os.fsdecode(event.dest_path))

    if event.src_path:
      paths.append(os.fsdecode(event.src_path))

    if self.matches(*paths):
      return super().dispatch(event)

  async def on_moved(self, event):
    filename = event.dest_path

    if self.debug:
      logging.debug(event)
      logging.debug((filename, 'seen', filename in self.seen))

    if filename not in self.seen:
      await self.queue.put(filename)
      self.seen.add(filename)

  async def on_created(self, event):
    return await self.on_moved(event)


async def consume_video_queue(
  queue: Queue,
  threads: int = DEFAULT_THREADS,
  show_debug: bool = False
):
  while True:
    name = await queue.get()

    if show_debug:
      logging.debug("Getting %s size..." % name)

    size = await wait_for_stable_size(name)

    if show_debug:
      logging.debug(name, size)
      logging.debug("Determine if", name, "is a video...")

    is_vid = await is_video(name)

    if show_debug:
      logging.debug(name, is_vid)
      logging.debug("Converting video...")

    if is_vid:
      pass

    else:
      print(name, 'not a video.')
