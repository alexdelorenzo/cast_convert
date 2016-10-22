from collections import namedtuple
from json import loads
from os.path import getsize
from subprocess import getoutput

try:
    from typing import Dict, List, Union, Tuple

except ImportError as e:
    try:
        from mypy.types import Dict, List, Union, Tuple

    except ImportError as e2:
        raise ImportError("Please install mypy via pip") from e2


from .exceptions import StreamNotFoundException
from .chromecast_compat import CAST_COMPAT
from .preferences import CONVERT_TO_CODEC


FFPROBE_CMD_FMT = 'ffprobe ' \
                  '-show_format ' \
                  '-show_streams ' \
                  '-loglevel quiet ' \
                  '-print_format json "%s"'

TRANSCODE_OPTS = {"audio": False,
                  "video": False,
                  "container": False}


NOT_VIDS = set('ansi mjpg png subrip'.split())


CodecInfo = Union[bool, str]
Options = Dict[str, CodecInfo]

Duration = namedtuple("Duration", "hour min sec")


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

    raise StreamNotFoundException("%s stream not found in file." % codec_type.capitalize())


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
        if fmt in CAST_COMPAT['container']:
            return fmt

    return name


VID_INFO_FUNCS = {
    'audio': get_audio_codec,
    'video': get_video_codec,
    'container': get_container_format
}


def duration_from_seconds(time: float) -> Duration:
    m, s = divmod(time, 60)
    h, m = divmod(m, 60)

    return Duration(h, m, s)


def get_duration(media_info: dict) -> float:
    return media_info['format']['duration']


def get_bitrate(media_info: dict) -> float:
    return media_info['format']['bitrate']


def is_compatible(codec_type: str, codec: str):
    if codec_type is None:
        return False

    return codec in CAST_COMPAT[codec_type]


def update_transcoding_info(stream_type: str, media_info: Options, transcoding_info: Options):
    func_get_codec = VID_INFO_FUNCS[stream_type]

    try:
        codec = func_get_codec(media_info)

        if not is_compatible(stream_type, codec):
            transcoding_info[stream_type] = CONVERT_TO_CODEC[stream_type]

    except StreamNotFoundException as e:
        transcoding_info[stream_type] = False


def determine_transcodings(media_info: dict) -> Options:
    transcoding_info = TRANSCODE_OPTS.copy()

    for stream_type in TRANSCODE_OPTS:
        update_transcoding_info(stream_type, media_info, transcoding_info)

    return transcoding_info


def get_transcode_info(filename: str) -> Options:
    return determine_transcodings(get_media_info(filename))


def is_video(path: str) -> bool:
    try:
        media_info = get_media_info(path)

    except IOError as e:
        return False

    codec = get_video_codec(media_info)

    if codec in NOT_VIDS:
        return False

    return bool(codec)
