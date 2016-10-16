# cast_convert

Convert audio, video and container to Chromecast supported types. Will only convert if necessary.

## Requirements
Requires a copy of ffmpeg with ffprobe along with libmp3lame and libx264 encoders.

### Debian
`sudo apt-get install ffmpeg lame libmp3lame0 x264`

### Mac OS X
`brew install ffmpeg lame x264`

### Windows
`Good Luck(tm)`

## Installation
- Ensure you have installed all requirements.
- `pip3 install cast_convert`

## Usage

### General
```
alex@mbp12,1:~$ cast_convert --help
Usage: cast_convert [OPTIONS] COMMAND [ARGS]...

  Convert and inspect video for Chromecast compatibility

Options:
  --help  Show this message and exit.

Commands:
  convert  Convert video to Chromecast compatible...
  get_cmd  Generate ffmpeg conversion command
  inspect  Inspect video for transcoding options

```

### Inspection
```
alex@mbp12,1:~$ cast_convert inspect Vids/Zoolander\ 2001\ \(1080p\ x265\ 10bit\ Joy\).mkv
Transcode video to {'container': '', 'audio': '', 'video': 'h264'}

```

### Conversion
```
alex@mbp12,1:~$ cast_convert convert --help
Usage: cast_convert convert [OPTIONS] FILENAME

  Convert video to Chromecast compatible encodings and container

Options:
  -t, --threads INTEGER  Count of threads for ffmpeg to use. Default: 4
  --help                 Show this message and exit.
```

### Print ffmpeg call
The conversion command calls ffmpeg to transcode video. The `get_cmd` command will print the ffmpeg call.
```
alex@mbp12,1:~$ cast_convert get_cmd Vids/Zoolander\ 2001\ \(1080p\ x265\ 10bit\ Joy\).mkv
ffmpeg -fflags +genpts -i "Vids/Zoolander 2001 (1080p x265 10bit Joy).mkv" -c:v libx264 -preset ultrafast -crf 21 -c:a copy  -threads 4 "Vids/Zoolander 2001 (1080p x265 10bit Joy)_transcode.mp4"

```

## License
See `LICENSE`
