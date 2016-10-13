from multiprocessing import cpu_count


ENCODING_OPTIONS = {
    'mp3': '-c:a libmp3lame -vbr 3',
    'h264': '-c:v libx264 -preset ultrafast -crf 21',
    'mp4': '-f mp4'
}

COPY_OPTIONS = {
    'audio': '-c:a copy',
    'video': '-c:v copy',
    'container': ''
}

THREADS = cpu_count()

AUDIO_CODEC = 'mp3'
VIDEO_CODEC = 'h264'
CONTAINER_TYPE = 'mp4'