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

from ...cli.helpers import DEFAULT_MODEL, _convert
from ..model.device import Device
from ..model.video import Video


FILESIZE_CHECK_WAIT: Final[float] = 2.0
DEFAULT_THREADS: Final[int] = 2
NO_SIZE: Final[int] = -1


async def wait_for_stable_size(
  file: str | Path,
  wait: float = FILESIZE_CHECK_WAIT,
  previous: int = None,
) -> int:
  path = AsyncPath(file)
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
      exception(e)
      previous = NO_SIZE


async def is_video(path: Path) -> bool:
  try:
    await to_thread(Video.from_path, path)

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
    async for path in gen_videos(*paths, seen=seen):
      coro = convert(device, path, sem)
      tg.create_task(coro)
