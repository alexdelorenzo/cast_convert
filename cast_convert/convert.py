#!/usr/bin/env python3

from subprocess import call, PIPE

import click

from .media_info import Options, CodecInfo, get_transcode_info
from .preferences import ENCODING_OPTIONS, COPY_OPTIONS, THREADS


FFMPEG_CMD = 'ffmpeg -fflags +genpts -i "%s" %s'
NEW_FILE_FMT = '%s_transcode.mp4'
THREADS_FMT = " -threads %s"


def get_option(media_type: str, codec: CodecInfo) -> str:
    return ENCODING_OPTIONS[codec] if codec else COPY_OPTIONS[media_type]


def build_options(options: Options) -> str:
    return ' '.join(get_option(media_type, codec)
                    for media_type, codec in options.items())


def build_cmd(filename: str, options: Options, threads: int=THREADS) -> str:
    threads = THREADS_FMT % str(threads)
    opts = build_options(options) + threads

    return FFMPEG_CMD % (filename, opts)


def convert_filename(filename: str) -> str:
    name, _, suffix = filename.rpartition('.')

    return NEW_FILE_FMT % name


def need_to_transcode(transcode_info: Options) -> bool:
    return any(new_codec for new_codec in transcode_info.values())


def get_ffmpeg_cmd(filename: str, threads: int=THREADS) -> str:
    transcode_info = get_transcode_info(filename)

    if not need_to_transcode(transcode_info):
        return ''

    cmd = build_cmd(filename, transcode_info, threads)
    filename = convert_filename(filename)

    return cmd + ' "%s"' % filename


def convert_video(filename: str, threads: int=THREADS) -> str:
    ffmpeg_cmd = get_ffmpeg_cmd(filename, threads)

    if not ffmpeg_cmd:
        print("No need to transcode %s" % filename)
        return

    call(ffmpeg_cmd, shell=True, stdout=PIPE)

    return convert_filename(filename)


@click.group(help="Convert and inspect video for Chromecast compatibility")
def cmd(debug: bool=False):
    pass


@click.command(help="Convert video to Chromecast compatible encodings and container")
@click.argument("filename")
@click.option("-t", "--threads", default=THREADS,  type=click.INT,
              help="Count of threads for ffmpeg to use. Default: %s" % THREADS)
def convert(filename: str, threads: int):
    print("%s -> %s" % (filename, convert_video(filename, threads)))


@click.command(help="Inspect video for transcoding options")
@click.argument("filename")
def inspect(filename: str):
    info = get_transcode_info(filename)

    if need_to_transcode(info):
        print("Transcode video to %s" % str(info))

    else:
        print("No need to transcode.")


cmd.add_command(convert)
cmd.add_command(inspect)


if __name__ == "__main__":
    cmd()

