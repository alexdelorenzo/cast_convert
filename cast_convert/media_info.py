from json import loads
from subprocess import getoutput


try:
    from typing import Dict, List, Union

except ImportError as e:
    try:
        from mypy.types import Dict, List, Union

    except ImportError as e:
        raise ImportError("Please install mypy from pip3") from e


from .chromecast_compat import COMPAT_AUDIO, COMPAT_CONTAINER, COMPAT_VIDEO
from .preferences import AUDIO_CODEC, VIDEO_CODEC, CONTAINER_TYPE


FFPROBE_CMD_FMT = 'ffprobe ' \
                  '-show_format ' \
                  '-show_streams ' \
                  '-loglevel quiet ' \
                  '-print_format json "%s"'

TRANSCODE_OPTS = {"audio": False,
                  "video": False,
                  "container": False}


CodecInfo = Union[bool, str]
Options = Dict[str, str]


def get_media_info(filename: str) -> dict:
    json = loads(getoutput(FFPROBE_CMD_FMT % filename))

    if not json:
        raise IOError("File %s cannot be read by ffprobe." % filename)

    return json


def get_codec(media_info: dict, codec_type: str) -> str:
    streams = media_info['streams']

    for stream in streams:
        if stream['codec_type'] == codec_type:
            return stream['codec_name']


def get_video_codec(media_info: dict) -> str:
    return get_codec(media_info, 'video')


def get_audio_codec(media_info: dict) -> str:
    return get_codec(media_info, 'audio')


def get_container_format(media_info: dict) -> str:
    format_info = media_info['format']
    name = format_info['format_name']

    # ffprobe might return a list of types
    # let's check each one for compatibility
    for fmt in name.split(','):
        if fmt in COMPAT_CONTAINER:
            return fmt

    return name


def is_audio_compatible(codec: str) -> bool:
    return codec in COMPAT_AUDIO


def is_video_compatible(codec: str) -> bool:
    return codec in COMPAT_VIDEO


def is_container_compatible(container: str) -> bool:
    return container in COMPAT_CONTAINER


def determine_transcodings(media_info: dict) -> Options:
    transcoding_info = TRANSCODE_OPTS.copy()

    if not is_audio_compatible(get_audio_codec(media_info)):
        transcoding_info['audio'] = AUDIO_CODEC

    if not is_video_compatible(get_video_codec(media_info)):
        transcoding_info['video'] = VIDEO_CODEC

    if not is_container_compatible(get_container_format(media_info)):
        transcoding_info['container'] = CONTAINER_TYPE

    return transcoding_info


def get_transcode_info(filename: str) -> Options:
    return determine_transcodings(get_media_info(filename))
