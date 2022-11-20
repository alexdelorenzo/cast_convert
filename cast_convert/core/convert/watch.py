import logging
from asyncio import gather, sleep, to_thread, BoundedSemaphore, TaskGroup
from collections.abc import AsyncIterable
from pathlib import Path

from aiopath import AsyncPath
from watchfiles import awatch, Change
import psutil

from ..exceptions import UnknownFormat
from ..model.video import Video
from ..base import DEFAULT_JOBS, DEFAULT_MODEL, DEFAULT_REPLACE, DEFAULT_THREADS, FILESIZE_CHECK_WAIT, NO_SIZE, Paths, \
  Strategy, get_error_handler, handle_errors
from .run import convert_from_name_path


def is_open_in_proc(file: Path | str) -> bool:
  file = Path(file)

  for proc in psutil.process_iter():
    files = set[Path]()

    try:
      files = {Path(f.path) for f in proc.open_files()}

    except Exception as e:
      logging.exception(e)
      logging.error(f"Couldn't read open files for {proc.pid} {proc.name()}")

    if file in files:
      return True

  return False


async def wait_until_closed(
  file: Path | str,
  wait: float = FILESIZE_CHECK_WAIT,
) -> Path:
  file = Path(file)

  while is_open_in_proc(file):
    await sleep(wait)

  return file


async def wait_for_stable_size(
  file: str | Path,
  wait: float = FILESIZE_CHECK_WAIT,
  previous: int = NO_SIZE,
) -> int:
  path: AsyncPath = AsyncPath(file)

  while True:
    try:
      result = await path.stat()
      size: int = result.st_size

      if size == previous:
        return size

      previous = size
      await sleep(wait)

    except Exception as e:
      logging.exception(e)
      previous = NO_SIZE


async def is_video(path: Path) -> bool:
  try:
    video = await to_thread(Video.from_path, path)

  except Exception as e:
    logging.exception(e)
    logging.error(f'Not a video: {path}')
    return False

  if video.formats.video_profile:
    return True

  logging.error(f'Not a video: {path}')
  return False


def get_new_path(file: str, change: Change, seen: Paths) -> Path | None:
  path = Path(file)

  if path in seen:
    return None

  seen.add(path)

  match change:
    case Change.added | Change.modified:
      return path


async def gen_new_files(
  *paths: Path,
  seen: Paths | None = None
) -> AsyncIterable[Path]:
  if seen is None:
    seen = Paths()

  async for changes in awatch(*paths):
    for change, file in changes:
      if path := get_new_path(file, change, seen):
        yield path


async def convert(
  device: str,
  path: Path,
  sem: BoundedSemaphore,
  replace: bool = DEFAULT_REPLACE,
  threads: int = DEFAULT_THREADS,
) -> Video | None:
  path = path.absolute()

  async with sem:
    await gather(wait_for_stable_size(path), wait_until_closed(path))

    if not await is_video(path):
      return None

    return await to_thread(convert_from_name_path, device, path, replace, threads)


async def convert_videos(
  *paths: Path,
  device: str = DEFAULT_MODEL,
  seen: Paths | None = None,
  jobs: int = DEFAULT_JOBS,
  replace: bool = DEFAULT_REPLACE,
  threads: int = DEFAULT_THREADS,
  error: Strategy = Strategy.quit,
):
  if seen is None:
    seen = Paths()

  sem = BoundedSemaphore(jobs)
  handled_converter = get_error_handler(convert, UnknownFormat, strategy=error)

  async with TaskGroup() as tg:
    async for path in gen_new_files(*paths, seen=seen):
      coro = handled_converter(device, path, sem, replace, threads)
      tg.create_task(coro)
