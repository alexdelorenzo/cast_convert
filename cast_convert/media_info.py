from json import loads
from subprocess import getoutput
from collections import defaultdict

from cast_convert.chromecast_compat import COMPAT_AUDIO, COMPAT_CONTAINER, COMPAT_VIDEO


FFPROBE_CMD_FMT = 'ffprobe -show_format -show_streams -loglevel quiet -print_format json "%s"'


def get_media_info(filename: str) -> dict:
    return loads(getoutput(FFPROBE_CMD_FMT % filename))


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

    return format_info['format_name']


def is_audio_compatible(codec: str) -> bool:
    return codec in COMPAT_AUDIO


def is_video_compatible(codec: str) -> bool:
    return codec in COMPAT_VIDEO


def is_container_compatible(container: str) -> bool:
    return container in COMPAT_CONTAINER


def determine_transcodings(media_info: dict) -> dict:
    transcoding_info = defaultdict(bool)

    if not is_audio_compatible(get_audio_codec(media_info)):
        transcoding_info['audio'] = 'mp3'

    if not is_video_compatible(get_video_codec(media_info)):
        transcoding_info['video'] = 'h264'

    if not is_container_compatible(get_container_format(media_info)):
        transcoding_info['container'] = 'mp4'

    return transcoding_info


def get_transcode_info(filename: str) -> dict:
    return determine_transcodings(get_media_info(filename))
