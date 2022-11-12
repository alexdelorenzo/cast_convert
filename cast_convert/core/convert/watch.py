import logging
from asyncio import sleep, to_thread, BoundedSemaphore, TaskGroup
from pathlib import Path
from typing import AsyncIterable, Final

from aiopath import AsyncPath
from watchfiles import awatch, Change

from ..model.video import Video
from ..base import DEFAULT_MODEL
from .helpers import _convert


FILESIZE_CHECK_WAIT: Final[float] = 2.0
DEFAULT_PROCS: Final[int] = 2
NO_SIZE: Final[int] = -1


async def wait_for_stable_size(
  file: str | Path,
  wait: float = FILESIZE_CHECK_WAIT,
  previous: int = None,
) -> int:
  path: AsyncPath = AsyncPath(file)
  previous: int = NO_SIZE

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
):
  path = path.absolute()

  async with sem:
    await wait_for_stable_size(path)
    await to_thread(_convert, device, path)


async def convert_videos(
  *paths: Path,
  device: str = DEFAULT_MODEL,
  seen: set[Path] | None = None,
  procs: int = DEFAULT_PROCS,
):
  if seen is None:
    seen = set[Path]()

  sem = BoundedSemaphore(procs)

  async with TaskGroup() as tg:
    async for path in gen_videos(*paths, seen=seen):
      coro = convert(device, path, sem)
      tg.create_task(coro)


# async def convert_videos(
#   *paths: Path,
#   device: str = DEFAULT_MODEL,
#   seen: set[Path] | None = None,
#   threads: int = DEFAULT_THREADS,
# ):
#   if seen is None:
#     seen = set[Path]()
#
#   sem = BoundedSemaphore(threads)
#
#   async for path in gen_videos(*paths, seen=seen):
#     await convert(device, path
