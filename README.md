# HandBrakeCLI Batch Transcoder

A minimal-dependency Python script to batch-transcode video files using `HandBrakeCLI`. Designed to be CLI-friendly, dry-run safe, and usable as a standalone system command.

## Features

* Transcodes video files to MP4 using:

  * x264 encoder
  * RF 20 quality
  * 160kbps audio
  * Web-optimized output
* Supports recursive directory traversal
* Lets you target specific file extensions (e.g., `.mkv`, `.avi`)
* Outputs `*-converted.mp4` files in the same directory as the original
* Skips files already converted (unless `--reprocess` is used)
* Safe by default (dry run unless `--commit` is used)
* Deletes source files after successful conversion if `--delete` is set
* Resumable without tracking files — based on whether the output file exists
* Summarizes all actions at the end

## Installation

```bash
chmod +x handbrake_wrapper.py
sudo mv handbrake_wrapper.py /usr/local/bin/transcode
```

## Usage

### Basic (dry run)

```bash
transcode --start . --ext mkv
```

### Recursive conversion

```bash
transcode --start ~/Videos --ext avi -r
```

### Actually run it (commit changes)

```bash
transcode --start . --ext mkv -r -c
```

### Reprocess all matching files

```bash
transcode --start . --ext mkv -r -c --reprocess
```

### Delete original files after encoding

```bash
transcode --start . --ext mkv -r -c --delete
```

### Cleanup source files after earlier run

```bash
transcode --start . --ext mkv -r -c --delete
```

## Help

```bash
transcode --help
```

## License

MIT

---

**Note:** Requires `HandBrakeCLI` to be installed and available in your `$PATH`.

Install it on Arch Linux:

```bash
sudo pacman -S handbrake-cli
```
