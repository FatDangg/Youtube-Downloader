# YouTube Downloader with `yt-dlp`

This project provides a Python command-line downloader built on top of [`yt-dlp`](https://github.com/yt-dlp/yt-dlp). It is designed to be easy to run, easy to extend, and configurable enough for common YouTube download workflows such as:

- Downloading a single video
- Downloading full playlists
- Downloading audio only
- Downloading subtitles
- Saving metadata, thumbnails, and descriptions
- Using cookies for age-restricted or private-access content
- Limiting speed, adding retries, and using a proxy
- Filtering downloads by title, date, views, or file size

## Important Notes

- Only download content you have the right to download.
- `yt-dlp` supports many sites, but this script is documented primarily for YouTube.
- Some features require `ffmpeg`, especially:
  - audio extraction and conversion
  - subtitle embedding
  - thumbnail embedding
  - remuxing or recoding video
- If YouTube changes something upstream, you may need to update `yt-dlp`.

## Project Files

- `youtube_downloader.py`: Main Python CLI script
- `requirements.txt`: Pip dependency file
- `environment.yml`: Conda environment definition with `ffmpeg`
- `README.md`: Setup and usage guide

## Requirements

You need:

- Conda or Miniconda
- Python 3.11 or compatible
- Internet access
- `ffmpeg` for post-processing features

## Setup

Start from cloning the repository and moving into the project folder:

```bash
git clone <your-repository-url>
cd Youtube\ Downloader
```

### Option 1: Create the Conda environment from `environment.yml`

From the project directory:

```bash
conda env create -f environment.yml
conda activate yt-downloader
```

This is the recommended setup because it installs both:

- Python
- `ffmpeg`
- `yt-dlp`

### Option 2: Create the Conda environment manually

```bash
conda create -n yt-downloader python=3.11 -y
conda activate yt-downloader
conda install -c conda-forge ffmpeg -y
pip install -r requirements.txt
```

## Verify Installation

Run:

```bash
python youtube_downloader.py --help
```

You should see the CLI help message with all supported options.

You can also verify `ffmpeg`:

```bash
ffmpeg -version
```

## Basic Usage

General syntax:

```bash
python youtube_downloader.py [OPTIONS] URL [URL ...]
```

You can pass:

- One URL
- Multiple URLs
- A playlist URL
- An input file with URLs using `--input-file`

By default, downloads go into:

```text
downloads/
```

Default output filename template:

```text
%(title)s [%(id)s].%(ext)s
```

For normal video downloads, the script now uses the highest-quality MP4-only format by default instead of WebM. If a video does not offer an MP4 format, you can override this with `--format`.

The downloader also resumes partial files and uses exponential retry backoff for HTTP and fragment errors by default, which helps with transient `503 Service Unavailable` failures.

## Quick Start Examples

### 1. Download one video

```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 2. Download multiple videos at once

```bash
python youtube_downloader.py \
  "https://www.youtube.com/watch?v=VIDEO_ID_1" \
  "https://www.youtube.com/watch?v=VIDEO_ID_2"
```

### 3. Download a full playlist

```bash
python youtube_downloader.py "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### 4. Download only audio as MP3

```bash
python youtube_downloader.py \
  --audio-only \
  --audio-format mp3 \
  --audio-quality 192 \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 5. Download the best video and remux to MP4

```bash
python youtube_downloader.py \
  --remux-video mp4 \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 6. Save into a custom folder

```bash
python youtube_downloader.py \
  --output-dir my_downloads \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 7. Use a custom output filename template

```bash
python youtube_downloader.py \
  --output-template "%(uploader)s/%(upload_date)s - %(title)s [%(id)s].%(ext)s" \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 8. Download subtitles

```bash
python youtube_downloader.py \
  --write-subs \
  --sub-langs "en,en-US" \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 9. Download auto-generated subtitles and embed them

```bash
python youtube_downloader.py \
  --write-auto-subs \
  --embed-subs \
  --sub-format srt \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 10. Use cookies from a browser

```bash
python youtube_downloader.py \
  --cookies-from-browser chrome \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 11. Use a cookies file

```bash
python youtube_downloader.py \
  --cookies ./cookies.txt \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 12. Download only items 1 to 5 from a playlist

```bash
python youtube_downloader.py \
  --playlist-start 1 \
  --playlist-end 5 \
  "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### 13. Download specific playlist items

```bash
python youtube_downloader.py \
  --playlist-items "1-3,7,10-12" \
  "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### 14. Limit download speed and add retries

```bash
python youtube_downloader.py \
  --limit-rate 2M \
  --retries 20 \
  --fragment-retries 20 \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 15. Retry more gently when YouTube returns 503

```bash
python youtube_downloader.py \
  --retries 20 \
  --fragment-retries 20 \
  --retry-sleep-http "exp=1:30" \
  --retry-sleep-fragment "exp=1:30" \
  --http-chunk-size 10M \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 16. Simulate without downloading

```bash
python youtube_downloader.py \
  --simulate \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 17. List available formats

```bash
python youtube_downloader.py \
  --list-formats \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 18. Download URLs from a text file

Create `urls.txt`:

```text
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
https://www.youtube.com/playlist?list=PLAYLIST_ID
```

Then run:

```bash
python youtube_downloader.py --input-file urls.txt
```

## Full Option Reference

Below is the practical meaning of each option supported by the script.

### Inputs

- `urls`
  - One or more URLs directly on the command line.
- `-i, --input-file`
  - Path to a text file containing one URL per line.
  - Empty lines and lines starting with `#` are ignored.

### Output Options

- `-o, --output-dir`
  - Folder where all downloads are saved.
  - Default: `downloads`
- `--output-template`
  - Filename template used by `yt-dlp`.
  - Default: `%(title)s [%(id)s].%(ext)s`
- `--write-info-json`
  - Save metadata as a `.info.json` file.
- `--write-description`
  - Save the video description to a text file.
- `--write-thumbnail`
  - Download the thumbnail image.
- `--write-comments`
  - Save comments when the site extractor supports it.
- `--no-overwrites`
  - Skip overwriting existing files.
- `--download-archive FILE`
  - Skip videos already listed in the archive file.

### Media Selection

- `--audio-only`
  - Download audio only.
- `--audio-format FORMAT`
  - Output audio format when using `--audio-only`.
  - Common values: `mp3`, `m4a`, `wav`, `flac`, `opus`
- `--audio-quality QUALITY`
  - Audio conversion quality.
  - Common values: `128`, `192`, `256`, `320`
- `--format FORMAT_SELECTOR`
  - Manual format selector for video downloads.
  - Default: `bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]`
- `--format-sort SORT_KEYS`
  - Comma-separated sort keys used by `yt-dlp`.
- `--remux-video FORMAT`
  - Change the final container without re-encoding if possible.
  - Choices: `mp4`, `mkv`, `mov`, `webm`
- `--recode-video FORMAT`
  - Re-encode the final video into a new format.
  - Choices: `mp4`, `mkv`, `webm`, `flv`, `avi`
- `--keep-video`
  - Keep intermediate files after post-processing.

### Subtitle Options

- `--write-subs`
  - Download regular subtitles.
- `--write-auto-subs`
  - Download auto-generated subtitles.
- `--sub-langs LANGS`
  - Comma-separated language list or patterns.
  - Example: `en,en-US,zh-TW`
- `--sub-format FORMAT`
  - Subtitle format such as `best`, `srt`, or `vtt`
- `--embed-subs`
  - Embed subtitles into the media file.

### Playlist Options

- `--playlist-items ITEMS`
  - Select specific items like `1-3,8,10-12`
- `--playlist-start N`
  - Start at item index `N`
- `--playlist-end N`
  - Stop at item index `N`
- `--no-playlist`
  - Ignore the playlist and download only the single referenced video

### Authentication Options

- `--cookies FILE`
  - Use a cookies file in Netscape format.
- `--cookies-from-browser BROWSER`
  - Load cookies from a local browser profile.
  - Common values: `chrome`, `firefox`, `edge`, `safari`
- `--username USERNAME`
  - Login username for supported sites.
- `--password PASSWORD`
  - Login password for supported sites.
- `--netrc`
  - Load credentials from `~/.netrc`.
- `--video-password PASSWORD`
  - Password for protected videos on supported sites.

### Network and Stability Options

- `--proxy URL`
  - Use an HTTP, HTTPS, or SOCKS proxy.
- `--limit-rate RATE`
  - Limit bandwidth.
  - Examples: `500K`, `2M`, `10M`
- `--throttled-rate RATE`
  - If speed drops below this threshold, yt-dlp assumes throttling and refreshes the media URL.
  - Default: `100K`
- `--retries N`
  - Retry count for download failures.
- `--fragment-retries N`
  - Retry count for fragment download failures.
- `--file-access-retries N`
  - Retry count for local file access failures.
- `--socket-timeout SECONDS`
  - Socket timeout.
- `--concurrent-fragments N`
  - Download fragments in parallel when supported.
- `--sleep-interval SECONDS`
  - Base delay before each download.
- `--max-sleep-interval SECONDS`
  - Maximum randomized delay before each download.
- `--sleep-requests SECONDS`
  - Delay between extraction requests.
- `--http-chunk-size SIZE`
  - Download in HTTP chunks instead of one long continuous transfer.
  - Example: `10M`
- `--retry-sleep-http EXPR`
  - Backoff expression for HTTP retries.
  - Default: `exp=1:30`
- `--retry-sleep-fragment EXPR`
  - Backoff expression for fragment retries.
  - Default: `exp=1:30`
- `--geo-bypass-country CC`
  - Try a country-specific geobypass.
  - Example: `US`, `JP`, `TW`
- `--force-ipv4`
  - Force IPv4 networking.

### Behavior Options

- `--embed-metadata`
  - Embed metadata into the final file.
- `--embed-thumbnail`
  - Embed the thumbnail into the final file when supported.
- `--sponsorblock-remove CATEGORIES`
  - Remove SponsorBlock categories.
  - Example: `sponsor,selfpromo,interaction`
- `--match-title REGEX`
  - Only download titles matching a regex.
- `--reject-title REGEX`
  - Skip titles matching a regex.
- `--date-after YYYYMMDD`
  - Download only items uploaded on or after the date.
- `--date-before YYYYMMDD`
  - Download only items uploaded on or before the date.
- `--min-views N`
  - Skip videos below this view count.
- `--max-views N`
  - Skip videos above this view count.
- `--min-filesize SIZE`
  - Skip files below this size.
  - Example: `50M`
- `--max-filesize SIZE`
  - Skip files above this size.
  - Example: `2G`
- `--playlist-reverse`
  - Download playlist items in reverse order.
- `--ignore-errors`
  - Continue when one entry fails.
- `--print-json`
  - Print extracted metadata as JSON.
- `--simulate`
  - Dry run without downloading.
- `--list-formats`
  - Show available formats and exit.
- `--verbose`
  - Enable verbose logging.

## Advanced Examples

### Download audio from many URLs and avoid duplicates

```bash
python youtube_downloader.py \
  --input-file urls.txt \
  --audio-only \
  --audio-format mp3 \
  --download-archive downloaded.txt \
  --output-dir music
```

### Save metadata, thumbnail, and description

```bash
python youtube_downloader.py \
  --write-info-json \
  --write-thumbnail \
  --write-description \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download only videos uploaded after January 1, 2024

```bash
python youtube_downloader.py \
  --date-after 20240101 \
  "https://www.youtube.com/@CHANNEL_HANDLE/videos"
```

### Filter by title and minimum views

```bash
python youtube_downloader.py \
  --match-title "Python|Machine Learning" \
  --min-views 10000 \
  "https://www.youtube.com/@CHANNEL_HANDLE/videos"
```

### Use a proxy and browser cookies for restricted content

```bash
python youtube_downloader.py \
  --proxy socks5://127.0.0.1:1080 \
  --cookies-from-browser firefox \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Recode video to MKV and embed metadata

```bash
python youtube_downloader.py \
  --recode-video mkv \
  --embed-metadata \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Remove SponsorBlock categories

```bash
python youtube_downloader.py \
  --sponsorblock-remove sponsor,selfpromo,interaction \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

## How the Script Works

The script:

1. Parses CLI arguments with `argparse`
2. Accepts URLs directly or from a text file
3. Builds a `yt-dlp` options dictionary
4. Creates the output directory if it does not exist
5. Passes the options into `yt_dlp.YoutubeDL`
6. Starts the download process

This means you can easily extend it later by adding more CLI flags and mapping them into the options dictionary.

## Updating `yt-dlp`

Because site behavior changes over time, updating `yt-dlp` is normal.

If you used the Conda environment:

```bash
pip install -U yt-dlp
```

If needed, also update `ffmpeg`:

```bash
conda install -c conda-forge ffmpeg -y
```

## Troubleshooting

### 1. `ffmpeg` not found

Symptoms:

- audio conversion fails
- merging fails
- subtitles do not embed

Fix:

```bash
conda install -c conda-forge ffmpeg -y
```

### 2. Download fails for restricted or age-gated content

Try:

- `--cookies-from-browser chrome`
- `--cookies-from-browser firefox`
- `--cookies ./cookies.txt`

### 3. A format is unavailable

First inspect formats:

```bash
python youtube_downloader.py --list-formats "https://www.youtube.com/watch?v=VIDEO_ID"
```

Then specify a custom format:

```bash
python youtube_downloader.py \
  --format "bestvideo[height<=1080]+bestaudio/best[height<=1080]" \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 4. Slow or unstable downloads

Try:

- increasing `--retries`
- increasing `--fragment-retries`
- setting `--retry-sleep-http "exp=1:30"`
- setting `--retry-sleep-fragment "exp=1:30"`
- setting `--socket-timeout 60`
- setting `--http-chunk-size 10M`
- using `--limit-rate`
- using a stable proxy

### 5. Repeated `HTTP Error 503: Service Unavailable`

This usually means the remote server or CDN temporarily refused part of the download. The script now resumes partial downloads automatically, but if 503 keeps happening, try:

- `--http-chunk-size 10M`
- `--retries 20`
- `--fragment-retries 20`
- `--retry-sleep-http "exp=1:30"`
- `--retry-sleep-fragment "exp=1:30"`
- `--cookies-from-browser chrome`

Example:

```bash
python youtube_downloader.py \
  --http-chunk-size 10M \
  --retries 20 \
  --fragment-retries 20 \
  --retry-sleep-http "exp=1:30" \
  --retry-sleep-fragment "exp=1:30" \
  --cookies-from-browser chrome \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 6. Playlist is too large

Use:

- `--playlist-items`
- `--playlist-start`
- `--playlist-end`
- `--download-archive`

## Common `yt-dlp` Template Fields

Useful placeholders for `--output-template`:

- `%(title)s`
- `%(id)s`
- `%(uploader)s`
- `%(channel)s`
- `%(upload_date)s`
- `%(playlist_title)s`
- `%(playlist_index)s`
- `%(ext)s`

Example:

```bash
python youtube_downloader.py \
  --output-template "%(channel)s/%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

## Security Notes

- Avoid putting account passwords directly into shell history if you can use cookies or `.netrc` instead.
- Browser cookies may grant account access, so protect exported cookie files carefully.
- Do not share cookies files publicly.

## Suggested Next Improvements

If you want to extend this project later, good additions would be:

- a GUI version with Tkinter or PySide
- a config file loader
- presets such as `audio`, `archive`, `playlist`, or `subtitles`
- logging to a file
- unit tests for argument parsing

## License and Responsibility

This example is provided as a general-purpose downloader wrapper for `yt-dlp`. You are responsible for using it in a way that complies with the law, site terms, and content rights.
