# 📽️ Convert videos for Chromecasts

Identify and convert videos to formats that are Chromecast supported.

`cast_convert` can tell you whether videos will play correctly on your casting devices. If they won't, this project can convert videos into formats that devices do support.

[Click here to see a list of supported devices](#supported-devices).

### What `cast_convert` does

`cast_convert` can identify and correct a video's incompatibility with a device caused by the video's:

- Video encoding
- Audio encoding
- Encoder profile
- Encoder level
- Container file format
- Frame rate
- Resolution
- Subtitle format

This utility can tell you if a video will or won't play correctly on your casting device. It can then efficiently modify
the video so that it will play on the device.

### About

Individual casting devices like the Chromecast have unique video encoding, audio encoding and container support
combinations for video files. `cast_convert` has detailed compatibility profiles for each individual Chromecast model on
the market.

`cast_convert` will inspect a video's metadata to determine what video attributes must get changed to successfully play
it. To use resources efficiently, it will determine only the minimum amount of transcoding needed to successfully play
each video back.

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

```bash
$ python3 -m pip install cast_convert
```

## Usage

### Launch

You can run the Python module directly:

```bash
$ python3 -m cast_convert --help
```

Or you can use launcher that gets added to your `$PATH`:

```bash
$ cast-convert --help
```

### Options and commands

```bash
                        
 Usage: cast-convert [OPTIONS] COMMAND [ARGS]...

 📽️ Identify and convert videos to formats that are Chromecast supported.

 See https://github.com/alexdelorenzo/cast_contvert for more information.
 Copyright © 2022 Alex DeLorenzo (https://alexdelorenzo.dev).

╭─ ❓ About ───────────────────────────────────────────────────────────────────╮
│ --log-level  -l      [critical|debug|error|fata  🪵 Set the minimum logging  │
│                      l|info|warn]                level.                      │
│                                                  [default: warn]             │
│ --version    -v                                  🔢 Show application versio… │
│                                                  and quit.                   │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ 📊 Analyze ─────────────────────────────────────────────────────────────────╮
│ command   📜 Get FFmpeg transcoding command.                                 │
│ inspect   🔎 Inspect videos to see what attributes should get transcoded.    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ 📽️ Convert ─────────────────────────────────────────────────────────────────╮
│ convert   📼 Convert videos so they're compatible with specified device.     │
│ watch     👀 Watch directories for new or modified videos and convert them.  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ 🛠️ Hardware Support ────────────────────────────────────────────────────────╮
│ devices          📺 List all supported devices.                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Parameters

### `--log-level`

You can set the log level using the `--log-level` flag:

```bash
$ cast-convert --log-level debug devices
[06:12:49] DEBUG    DEBUG:root:Loaded devices from file     base.py:201
You can use these device names with the --name flag:
    - Chromecast 1st Gen
    - Chromecast 2nd Gen
    - Chromecast 3rd Gen
    - Chromecast Ultra
    - Chromecast with Google TV
    - Google Nest Hub
    - Nest Hub Max
```

Default log level is `warn`.

### `--name`

You can specify the model of your device with the `--name` flag. It uses fuzzy matching, so you don't have to type out
device names completely.

The `--name` flag comes *after* [`cast-convert` commands](#commands).

```bash
$ cast-convert inspect --name '1st Gen' ~/video.mkv
[🔄️] Need to convert "/home/user/video.mkv" to play on Chromecast 1st Gen...
  Must convert from:
    - Container: webm
    - Codec: vp9
    - Resolution: 406
    - Fps: 25.000
    - Level: 0
  To:
    - Codec: avc
    - Level: 4.1
```

Default device name is `Chromecast 1st Gen`.

### `PATHS`

You can specify one or more file or directory paths as `PATHS` arguments.

You must specify at least one path. Paths are supplied after commands, and they are the *last* arguments
to `cast-convert`.

```bash
$ cast-convert command vid1.mkv vid2.mkv
ffmpeg -fflags +genpts -i 'vid1.mkv' -acodec copy -movflags faststart -scodec 
copy -threads 12 -vcodec libx264 -vlevel 4.1 'vid1_transcoded.mkv' -y

ffmpeg -fflags +genpts -i 'vid2.mkv' -acodec copy -movflags faststart -scodec 
copy -threads 12 -vcodec libx264 -vlevel 4.1 'vid2_transcoded.mkv' -y
```

### Commands

### `convert`

```bash
 Usage: cast-convert convert [OPTIONS] 📂PATHS

 📼 Convert videos so they're compatible with specified device.

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    paths      📂PATHS  Path(s) to video(s). [required]                     │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ 📺 Device ──────────────────────────────────────────────────────────────────╮
│ --name  -n      TEXT  📛 Device model name. [default: Chromecast 1st Gen]    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ 🖥 Encoder Options ──────────────────────────────────────────────────────────╮
│ --replace  -r               💾 Replace original file with transcoded video.  │
│ --threads  -t      INTEGER  🧵 Number of threads to tell FFMPEG to use per   │
│                             job.                                             │
│                             [default: 12]                                    │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### `devices`

```bash
 Usage: cast-convert devices [OPTIONS]

 📺 List all supported devices.

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ 📺 Device ──────────────────────────────────────────────────────────────────╮
│ --details  -d        ℹ Show detailed device information.                     │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### `command`

```bash
 Usage: cast-convert command [OPTIONS] 📂PATHS

 📜 Get FFmpeg transcoding command.

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    paths      📂PATHS  Path(s) to video(s). [required]                     │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ 📺 Device ──────────────────────────────────────────────────────────────────╮
│ --name  -n      TEXT  📛 Device model name. [default: Chromecast 1st Gen]    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ 🖥 Encoder Options ──────────────────────────────────────────────────────────╮
│ --replace  -r               💾 Replace original file with transcoded video.  │
│ --threads  -t      INTEGER  🧵 Number of threads to tell FFMPEG to use per   │
│                             job.                                             │
│                             [default: 12]                                    │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### `inspect`

```bash
 Usage: cast-convert inspect [OPTIONS] 📂PATHS 

 🔎 Inspect videos to see what attributes should get transcoded.                

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    paths      📂PATHS  Path(s) to video(s). [required]                     │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ 📺 Device ──────────────────────────────────────────────────────────────────╮
│ --name  -n      TEXT  📛 Device model name. [default: Chromecast 1st Gen]    │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### `watch`

```bash
 Usage: cast-convert watch [OPTIONS] 📂PATHS

 👀 Watch directories for new or modified videos and convert them.

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    paths      📂PATHS  Path(s) to video(s). [required]                     │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ 📺 Device ──────────────────────────────────────────────────────────────────╮
│ --name  -n      TEXT  📛 Device model name. [default: Chromecast 1st Gen]    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ 🖥 Encoder Options ──────────────────────────────────────────────────────────╮
│ --jobs     -j      INTEGER  🔢 Number of simultaneous transcoding jobs.      │
│                             [default: 2]                                     │
│ --replace  -r               💾 Replace original file with transcoded video.  │
│ --threads  -t      INTEGER  🧵 Number of threads to tell FFMPEG to use per   │
│                             job.                                             │
│                             [default: 12]                                    │
╰──────────────────────────────────────────────────────────────────────────────╯
```
