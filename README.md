# 📽️ Convert videos for Chromecasts
Identify and convert videos to formats that are Chromecast supported with `cast_convert`.

`cast_convert` can tell you whether or not a video will play correctly on your casting device. If it won't, `cast_convert` can convert videos into formats that the device supports.

[Click here to see a list of supported devices](#supported-devices).

### What it helps with
`cast_convert` can identify and correct a video's incompatibility with a device caused by the video's:
 - Video codec
 - Audio codec
 - Encoder profile
 - Encoder level
 - Container file format
 - Frames per second
 - Resolution

This utility can tell you if a video will or won't play correctly on your casting device. It can then efficiently modify the video so that it will play on the device.

### About
Individual casting devices like the Chromecast have unique video encoding, audio encoding and container support combinations for video files. Instead of looking up the specifics for the specific model you own,`cast_convert` already uses detailed compatibility profiles for each individual Chromecast model. 

`cast_convert` will inspect video metadata to determine what video attributes must get changed for successful playback. To use resources efficiently, it will determine the minimum amount of transcoding needed to successfully play each video back.

### Supported devices
 - Chromecast 1st Gen
 - Chromecast 2nd Gen
 - Chromecast 3rd Gen
 - Chromecast Ultra
 - Chromecast with Google TV
 - Google Nest Hub
 - Nest Hub Max

## Requirements
### Minimum
 - Python 3.11
 - `mediainfo`
 - `ffmpeg`

### Encoders
 - `libmp3lame`
 - `x264`

## Installation
```bashe
$ python3 -m pip install cast_convert
```

[//]: # ()
[//]: # (## Usage)

[//]: # (### General)

[//]: # (```)

[//]: # (alex@mbp12,1:~$ cast_convert --help)

[//]: # (Usage: cast_convert [OPTIONS] COMMAND [ARGS]...)

[//]: # ()
[//]: # (  Convert and inspect video for Chromecast compatibility)

[//]: # ()
[//]: # (Options:)

[//]: # (  --help  Show this message and exit.)

[//]: # ()
[//]: # (Commands:)

[//]: # (  convert  Convert video to Chromecast compatible...)

[//]: # (  get_cmd  Generate ffmpeg conversion command)

[//]: # (  inspect  Inspect video for transcoding options)

[//]: # ()
[//]: # (```)

[//]: # ()
[//]: # (### Inspection)

[//]: # (```)

[//]: # (alex@mbp12,1:~$ cast_convert inspect Vids/Zoolander\ 2001\ \&#40;1080p\ x265\ 10bit\ Joy\&#41;.mkv)

[//]: # (Transcode video to {'container': '', 'audio': '', 'video': 'h264'})

[//]: # ()
[//]: # (```)

[//]: # ()
[//]: # (### Conversion)

[//]: # (```)

[//]: # (alex@mbp12,1:~$ cast_convert convert --help)

[//]: # (Usage: cast_convert convert [OPTIONS] FILENAME)

[//]: # ()
[//]: # (  Convert video to Chromecast compatible encodings and container)

[//]: # ()
[//]: # (Options:)

[//]: # (  -t, --threads INTEGER  Count of threads for ffmpeg to use. Default: 4)

[//]: # (  --help                 Show this message and exit.)

[//]: # (```)

[//]: # ()
[//]: # (### Print ffmpeg call)

[//]: # (The conversion command calls ffmpeg to transcode video. The `get_cmd` command will print the ffmpeg call.)

[//]: # (```)

[//]: # (alex@mbp12,1:~$ cast_convert get_cmd Vids/Zoolander\ 2001\ \&#40;1080p\ x265\ 10bit\ Joy\&#41;.mkv)

[//]: # (ffmpeg -fflags +genpts -i "Vids/Zoolander 2001 &#40;1080p x265 10bit Joy&#41;.mkv" -c:v libx264 -preset ultrafast -crf 21 -c:a copy  -threads 4 "Vids/Zoolander 2001 &#40;1080p x265 10bit Joy&#41;_transcode.mp4")

[//]: # ()
[//]: # (```)

[//]: # ()
[//]: # (## License)

[//]: # (See `LICENSE`)
