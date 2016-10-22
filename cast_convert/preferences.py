from multiprocessing import cpu_count


ENCODER_OPTIONS = {
    'mp3': '-c:a libmp3lame '
           '-q:a 3 ',
    'h264': '-c:v libx264 '
            '-preset ultrafast '
            '-crf 21 ',
    'mp4': '-f mp4 '
}

COPY_OPTIONS = {
    'audio': '-c:a copy',
    'video': '-c:v copy',
    'container': ''
}

CONVERT_TO_CODEC = {
    'audio': 'mp3',
    'video': 'h264',
    'container': 'mp4',
    None: None  # stream isn't found
}

NEW_FILE_FMT = '%s_castconvert.mp4'
FILESIZE_CHECK_WAIT = 2.0

CPUS = cpu_count()
THREADS = (CPUS - 1) if CPUS >= 3 else CPUS

FFMPEG_PROCESSES = 1 if CPUS >= 2 else 1
