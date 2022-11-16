import logging
from asyncio import sleep, to_thread, BoundedSemaphore, TaskGroup
from pathlib import Path
from typing import AsyncIterable, Final
from multiprocessing import cpu_count

from aiopath import AsyncPath
from watchfiles import awatch, Change

from ..model.video import Video
from ..base import DEFAULT_MODEL
from .helpers import _convert


FILESIZE_CHECK_WAIT: Final[float] = 2.0
DEFAULT_JOBS: Final[int] = 2
DEFAULT_THREADS: Final[int] = cpu_count()
NO_SIZE: Final[int] = -1


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
        case Change.added | Change.modified if await is_video(path):
          yield path


async def convert(
  device: str,
  path: Path,
  sem: BoundedSemaphore,
  threads: int,
):
  path = path.absolute()

  async with sem:
    await wait_for_stable_size(path)
    await to_thread(_convert, device, path, threads)


async def convert_videos(
  *paths: Path,
  device: str = DEFAULT_MODEL,
  seen: set[Path] | None = None,
  jobs: int = DEFAULT_JOBS,
  threads: int = DEFAULT_THREADS,
):
  if seen is None:
    seen = set[Path]()

  sem = BoundedSemaphore(jobs)

  async with TaskGroup() as tg:
    async for path in gen_videos(*paths, seen=seen):
      coro = convert(device, path, sem, threads)
      tg.create_task(coro)
