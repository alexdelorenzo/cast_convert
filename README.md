# 📽️ Cast Convert
Convert videos to formats that are supported by Chromecast devices.

Casting devices like the Chromecast support unique video & audio codec and container profiles, and `cast_convert` has detailed compatibility profiles for each individual device. 

`cast_convert` will inspect and only minimally transcode videos to save time and resources. Every video is scanned to determine exactly which attributes are not compatible with specific devices, and `cast_convert` will transcode only what is needed to successfully play the video.

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
