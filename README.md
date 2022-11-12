# 📽️ Convert videos for Chromecasts
Identify and convert videos to formats that are Chromecast supported.

`cast_convert` can tell you whether videos will play correctly on your casting devices. If they won't, `cast_convert` can convert videos into formats that devices support.

[Click here to see a list of supported devices](#supported-devices).

### What this project helps with
`cast_convert` can identify and correct a video's incompatibility with a device caused by the video's:
  - Video encoding
  - Audio encoding
  - Encoder profile
  - Encoder level
  - Container file format
  - Frame rate
  - Resolution
  - Subtitle format

This utility can tell you if a video will or won't play correctly on your casting device. It can then efficiently modify the video so that it will play on the device.

### About
Individual casting devices like the Chromecast have unique video encoding, audio encoding and container support combinations for video files. `cast_convert` has detailed compatibility profiles for each individual Chromecast model on the market. 

`cast_convert` will inspect a video's metadata to determine what video attributes must get changed to successfully play it. To use resources efficiently, it will determine only the minimum amount of transcoding needed to successfully play each video back.

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

 📽️ Identify and convert videos to formats that are
 Chromecast supported.

╭─ Options ────────────────────────────────────────────────╮
│ --log-level                 TEXT  Choose level of debug  │
│                                   logging.               │
│                                   [default: warn]        │
│ --install-completion              Install completion for │
│                                   the current shell.     │
│ --show-completion                 Show completion for    │
│                                   the current shell, to  │
│                                   copy it or customize   │
│                                   the installation.      │
│ --help                            Show this message and  │
│                                   exit.                  │
╰──────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────╮
│ convert      Convert video for Chromecast compatibility. │
│ devices      List all supported device names.            │
│ get-command  Get FFMPEG transcoding command.             │
│ inspect      Inspect a video to see what attributes      │
│              should be decoded.                          │
│ watch        Watch directories for added videos and      │
│              convert them.                               │
╰──────────────────────────────────────────────────────────╯

```

### Parameters
#### `--log-level`
You can set the log level using the `--log-level` flag:

```bash
$ cast-convert --log-level debug devices
```

Default log level is `warn`.

#### `--name`
You can specify the model of your device with the `--name` flag.

The `--name` flag comes *after* [`cast-convert` commands](#commands).

```bash
$ cast-convert inspect --name 'Chromecast Ultra' ~/video.mkv
```

Default device name is `Chromecast 1st Gen`.


#### `PATHS`
You can specify one or more file or directory paths as `PATHS` arguments.

You must specify at least one path. Paths are supplied after commands, and they are the *last* arguments to `cast-convert`.

```bash
$ cast-convert get-command vid1.mkv vid2.mkv vid3.mkv
```

### Commands
#### `convert`
```bash
Usage: cast-convert convert [OPTIONS] PATHS...

📼 Convert video for Chromecast compatibility. 

╭─ Arguments ──────────────────────────────────────────────╮
│ *    paths      PATHS...  Path, or paths, to video(s)    │
│                           [default: None]                │
│                           [required]                     │
╰──────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────╮
│ --name        TEXT  Chromecast model name                │
│                     [default: Chromecast 1st Gen]        │
│ --help              Show this message and exit.          │
╰──────────────────────────────────────────────────────────╯
```

#### `devices`
```bash
Usage: cast-convert convert [OPTIONS] PATHS...

📺 List the names of supported devices.

╭─ Options ────────────────────────────────────────────────╮
│ --help              Show this message and exit.          │
╰──────────────────────────────────────────────────────────╯
```

#### `get-command`
```bash

Usage: cast-convert get-command [OPTIONS] PATHS...

📜 Get FFMPEG transcoding commands.

╭─ Arguments ──────────────────────────────────────────────╮
│ *    paths      PATHS...  Path, or paths, to video(s)    │
│                           [default: None]                │
│                           [required]                     │
╰──────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────╮
│ --name        TEXT  Chromecast model name                │
│                     [default: Chromecast 1st Gen]        │
│ --help              Show this message and exit.          │
╰──────────────────────────────────────────────────────────╯
```

#### `inspect`
```bash
Usage: cast-convert inspect [OPTIONS] PATHS...

🔎 Inspect a video to see what attributes should be transcoded.

╭─ Arguments ──────────────────────────────────────────────╮
│ *    paths      PATHS...  Path, or paths, to video(s)    │
│                           [default: None]                │
│                           [required]                     │
╰──────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────╮
│ --name        TEXT  Chromecast model name                │
│                     [default: Chromecast 1st Gen]        │
│ --help              Show this message and exit.          │
╰──────────────────────────────────────────────────────────╯
```


#### `watch`
```bash
Usage: cast-convert watch [OPTIONS] PATHS...

👀 Watch directories for added videos and convert them. 

╭─ Arguments ──────────────────────────────────────────────╮
│ *    paths      PATHS...  Path, or paths, to video(s)    │
│                           [default: None]                │
│                           [required]                     │
╰──────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────╮
│ --name           TEXT     Chromecast model name          │
│                           [default: Chromecast 1st Gen]  │
│ --threads        INTEGER  [default: 2]                   │
│ --help                    Show this message and exit.    │
╰──────────────────────────────────────────────────────────╯
```

