#!/usr/bin/env python3
"""Configurable YouTube and general media downloader powered by yt-dlp."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from yt_dlp import YoutubeDL
from yt_dlp.utils import parse_bytes


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than 0")
    return parsed


def non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be 0 or greater")
    return parsed


def non_negative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be 0 or greater")
    return parsed


def comma_separated_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_byte_size(value: str, field_name: str) -> int:
    parsed = parse_bytes(value)
    if parsed is None:
        raise ValueError(f"invalid {field_name}: {value}")
    return parsed


def parse_retry_sleep_expression(expr: str) -> Any:
    number_re = r"\d+(?:\.\d+)?"
    match = re.fullmatch(
        rf"(?:(linear|exp)=)?({number_re})(?::({number_re})?)?(?::({number_re}))?",
        expr.strip(),
    )
    if not match:
        raise argparse.ArgumentTypeError(
            "retry sleep must be a number, linear=START[:END[:STEP]], or exp=START[:END[:BASE]]"
        )

    op, start, limit, step = match.groups()
    start_f = float(start)
    limit_f = float(limit) if limit else float("inf")

    if op == "exp":
        base_f = float(step or 2)
        return lambda n: min(start_f * (base_f**n), limit_f)

    default_step = start_f if op or limit else 0.0
    step_f = float(step or default_step)
    return lambda n: min(start_f + step_f * n, limit_f)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download YouTube videos, playlists, audio, subtitles, and more "
            "using yt-dlp."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    input_group = parser.add_argument_group("Inputs")
    input_group.add_argument(
        "urls",
        nargs="*",
        help="One or more video, playlist, channel, or supported site URLs.",
    )
    input_group.add_argument(
        "-i",
        "--input-file",
        help="Text file containing one URL per line.",
    )

    output_group = parser.add_argument_group("Output")
    output_group.add_argument(
        "-o",
        "--output-dir",
        default="downloads",
        help="Directory where downloaded files will be saved.",
    )
    output_group.add_argument(
        "--output-template",
        default="%(title)s [%(id)s].%(ext)s",
        help="yt-dlp output template used inside the output directory.",
    )
    output_group.add_argument(
        "--write-info-json",
        action="store_true",
        help="Save video metadata to a JSON file.",
    )
    output_group.add_argument(
        "--write-description",
        action="store_true",
        help="Save the media description to a text file.",
    )
    output_group.add_argument(
        "--write-thumbnail",
        action="store_true",
        help="Download the thumbnail image.",
    )
    output_group.add_argument(
        "--write-comments",
        action="store_true",
        help="Download comments when supported by the extractor.",
    )
    output_group.add_argument(
        "--no-overwrites",
        action="store_true",
        help="Do not overwrite files that already exist.",
    )
    output_group.add_argument(
        "--download-archive",
        help="Archive file used to skip videos that were already downloaded.",
    )

    media_group = parser.add_argument_group("Media Selection")
    media_group.add_argument(
        "--audio-only",
        action="store_true",
        help="Download audio only and optionally convert it.",
    )
    media_group.add_argument(
        "--audio-format",
        default="mp3",
        help="Target audio format when --audio-only is used.",
    )
    media_group.add_argument(
        "--audio-quality",
        default="192",
        help="Preferred audio quality for conversion, e.g. 128, 192, 320.",
    )
    media_group.add_argument(
        "--format",
        default="bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        help="yt-dlp format selector for video downloads. Defaults to the best MP4-only format.",
    )
    media_group.add_argument(
        "--format-sort",
        help="Comma-separated format sort keys, e.g. 'res,fps,hdr:12'.",
    )
    media_group.add_argument(
        "--remux-video",
        choices=["mp4", "mkv", "mov", "webm"],
        help="Remux the final video container after download if possible.",
    )
    media_group.add_argument(
        "--recode-video",
        choices=["mp4", "mkv", "webm", "flv", "avi"],
        help="Re-encode the final video into the selected format.",
    )
    media_group.add_argument(
        "--keep-video",
        action="store_true",
        help="Keep intermediate video files after post-processing.",
    )

    subtitle_group = parser.add_argument_group("Subtitles")
    subtitle_group.add_argument(
        "--write-subs",
        action="store_true",
        help="Download subtitles if available.",
    )
    subtitle_group.add_argument(
        "--write-auto-subs",
        action="store_true",
        help="Download auto-generated subtitles if available.",
    )
    subtitle_group.add_argument(
        "--sub-langs",
        default="en.*,en",
        help="Comma-separated subtitle languages or patterns.",
    )
    subtitle_group.add_argument(
        "--sub-format",
        default="best",
        help="Subtitle format selector, e.g. best, vtt, srt.",
    )
    subtitle_group.add_argument(
        "--embed-subs",
        action="store_true",
        help="Embed subtitles into the media file when supported.",
    )

    playlist_group = parser.add_argument_group("Playlists")
    playlist_group.add_argument(
        "--playlist-items",
        help="Playlist item selection, e.g. 1-5,8,10-12.",
    )
    playlist_group.add_argument(
        "--playlist-start",
        type=positive_int,
        help="Start index for playlist downloads.",
    )
    playlist_group.add_argument(
        "--playlist-end",
        type=positive_int,
        help="End index for playlist downloads.",
    )
    playlist_group.add_argument(
        "--no-playlist",
        action="store_true",
        help="Download only the provided video even if the URL belongs to a playlist.",
    )

    auth_group = parser.add_argument_group("Authentication")
    auth_group.add_argument(
        "--cookies",
        help="Path to a Netscape-format cookies.txt file.",
    )
    auth_group.add_argument(
        "--cookies-from-browser",
        help=(
            "Read cookies from a browser, e.g. chrome, firefox, edge, safari. "
            "Browser profiles can be specified in yt-dlp syntax."
        ),
    )
    auth_group.add_argument("--username", help="Account username for supported sites.")
    auth_group.add_argument("--password", help="Account password for supported sites.")
    auth_group.add_argument(
        "--netrc",
        action="store_true",
        help="Read credentials from ~/.netrc.",
    )
    auth_group.add_argument(
        "--video-password",
        help="Password for password-protected videos when supported.",
    )

    network_group = parser.add_argument_group("Network and Stability")
    network_group.add_argument(
        "--proxy",
        help="Proxy URL, e.g. http://127.0.0.1:7890 or socks5://127.0.0.1:1080.",
    )
    network_group.add_argument(
        "--limit-rate",
        help="Rate limit such as 2M, 500K, or 0 for unlimited.",
    )
    network_group.add_argument(
        "--throttled-rate",
        default="100K",
        help=(
            "Minimum speed below which throttling is assumed and yt-dlp re-extracts "
            "the media URL."
        ),
    )
    network_group.add_argument(
        "--retries",
        type=non_negative_int,
        default=10,
        help="Retry count for download errors.",
    )
    network_group.add_argument(
        "--fragment-retries",
        type=non_negative_int,
        default=10,
        help="Retry count for fragment download errors.",
    )
    network_group.add_argument(
        "--file-access-retries",
        type=non_negative_int,
        default=3,
        help="Retry count for local file access errors.",
    )
    network_group.add_argument(
        "--socket-timeout",
        type=non_negative_float,
        default=30.0,
        help="Socket timeout in seconds.",
    )
    network_group.add_argument(
        "--concurrent-fragments",
        type=positive_int,
        default=1,
        help="Number of fragments to download in parallel for DASH/HLS streams.",
    )
    network_group.add_argument(
        "--sleep-interval",
        type=non_negative_float,
        help="Base sleep time before each download in seconds.",
    )
    network_group.add_argument(
        "--max-sleep-interval",
        type=non_negative_float,
        help="Maximum randomized sleep time before each download in seconds.",
    )
    network_group.add_argument(
        "--sleep-requests",
        type=non_negative_float,
        help="Base sleep time between extraction requests in seconds.",
    )
    network_group.add_argument(
        "--http-chunk-size",
        help=(
            "Chunk size for chunked HTTP downloading, e.g. 10M. Useful when a server "
            "fails on large continuous transfers."
        ),
    )
    network_group.add_argument(
        "--retry-sleep-http",
        default="exp=1:30",
        help="Retry backoff for HTTP download retries.",
    )
    network_group.add_argument(
        "--retry-sleep-fragment",
        default="exp=1:30",
        help="Retry backoff for fragment download retries.",
    )
    network_group.add_argument(
        "--geo-bypass-country",
        help="Two-letter country code to attempt geobypass with supported sites.",
    )
    network_group.add_argument(
        "--force-ipv4",
        action="store_true",
        help="Force IPv4 for all network requests.",
    )

    behavior_group = parser.add_argument_group("Behavior")
    behavior_group.add_argument(
        "--embed-metadata",
        action="store_true",
        help="Embed metadata tags into the output file.",
    )
    behavior_group.add_argument(
        "--embed-thumbnail",
        action="store_true",
        help="Embed thumbnail into the output file when supported.",
    )
    behavior_group.add_argument(
        "--sponsorblock-remove",
        help=(
            "SponsorBlock categories to remove, e.g. sponsor,selfpromo,interaction. "
            "Requires media post-processing support."
        ),
    )
    behavior_group.add_argument(
        "--match-title",
        help="Only download videos whose title matches this regex.",
    )
    behavior_group.add_argument(
        "--reject-title",
        help="Skip videos whose title matches this regex.",
    )
    behavior_group.add_argument(
        "--date-after",
        help="Download only videos uploaded on or after YYYYMMDD.",
    )
    behavior_group.add_argument(
        "--date-before",
        help="Download only videos uploaded on or before YYYYMMDD.",
    )
    behavior_group.add_argument(
        "--min-views",
        type=non_negative_int,
        help="Skip videos with fewer than this many views.",
    )
    behavior_group.add_argument(
        "--max-views",
        type=non_negative_int,
        help="Skip videos with more than this many views.",
    )
    behavior_group.add_argument(
        "--min-filesize",
        help="Skip files smaller than this size, e.g. 50M.",
    )
    behavior_group.add_argument(
        "--max-filesize",
        help="Skip files larger than this size, e.g. 2G.",
    )
    behavior_group.add_argument(
        "--playlist-reverse",
        action="store_true",
        help="Download playlist entries in reverse order.",
    )
    behavior_group.add_argument(
        "--ignore-errors",
        action="store_true",
        help="Continue processing other entries even if one fails.",
    )
    behavior_group.add_argument(
        "--print-json",
        action="store_true",
        help="Print extracted metadata as JSON to stdout.",
    )
    behavior_group.add_argument(
        "--simulate",
        action="store_true",
        help="Do not download anything; simulate the run.",
    )
    behavior_group.add_argument(
        "--list-formats",
        action="store_true",
        help="List available formats for the provided URL(s) without downloading.",
    )
    behavior_group.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose yt-dlp logging.",
    )

    args = parser.parse_args()

    if not args.urls and not args.input_file:
        parser.error("provide at least one URL or use --input-file")

    if args.max_sleep_interval is not None and args.sleep_interval is None:
        parser.error("--max-sleep-interval requires --sleep-interval")

    if args.audio_only and (args.remux_video or args.recode_video):
        parser.error("--audio-only cannot be combined with --remux-video or --recode-video")

    if args.playlist_start and args.playlist_end:
        if args.playlist_start > args.playlist_end:
            parser.error("--playlist-start cannot be greater than --playlist-end")

    try:
        args.retry_sleep_http_func = parse_retry_sleep_expression(args.retry_sleep_http)
        args.retry_sleep_fragment_func = parse_retry_sleep_expression(args.retry_sleep_fragment)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))

    return args


def gather_urls(args: argparse.Namespace) -> list[str]:
    urls = list(args.urls)

    if args.input_file:
        path = Path(args.input_file).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"input file not found: {path}")

        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                urls.append(stripped)

    deduplicated: list[str] = []
    seen: set[str] = set()
    for url in urls:
        if url not in seen:
            seen.add(url)
            deduplicated.append(url)

    if not deduplicated:
        raise ValueError("no usable URLs were found")

    return deduplicated


def build_options(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    options: dict[str, Any] = {
        "paths": {"home": str(output_dir)},
        "outtmpl": {"default": args.output_template},
        "restrictfilenames": False,
        "noplaylist": args.no_playlist,
        "ignoreerrors": args.ignore_errors,
        "retries": args.retries,
        "fragment_retries": args.fragment_retries,
        "file_access_retries": args.file_access_retries,
        "socket_timeout": args.socket_timeout,
        "concurrent_fragment_downloads": args.concurrent_fragments,
        "continuedl": True,
        "overwrites": not args.no_overwrites,
        "download_archive": args.download_archive,
        "writedescription": args.write_description,
        "writeinfojson": args.write_info_json,
        "writethumbnail": args.write_thumbnail,
        "getcomments": args.write_comments,
        "playlistreverse": args.playlist_reverse,
        "matchtitle": args.match_title,
        "rejecttitle": args.reject_title,
        "dateafter": args.date_after,
        "datebefore": args.date_before,
        "min_views": args.min_views,
        "max_views": args.max_views,
        "min_filesize": (
            parse_byte_size(args.min_filesize, "min filesize") if args.min_filesize else None
        ),
        "max_filesize": (
            parse_byte_size(args.max_filesize, "max filesize") if args.max_filesize else None
        ),
        "proxy": args.proxy,
        "ratelimit": parse_byte_size(args.limit_rate, "rate limit") if args.limit_rate else None,
        "throttledratelimit": (
            parse_byte_size(args.throttled_rate, "throttled rate")
            if args.throttled_rate
            else None
        ),
        "geo_bypass_country": args.geo_bypass_country,
        "force_ipv4": args.force_ipv4,
        "print_json": args.print_json,
        "simulate": args.simulate or args.list_formats,
        "listformats": args.list_formats,
        "verbose": args.verbose,
        "retry_sleep_functions": {
            "http": args.retry_sleep_http_func,
            "fragment": args.retry_sleep_fragment_func,
        },
    }

    if args.format_sort:
        options["format_sort"] = comma_separated_list(args.format_sort)

    if args.playlist_items:
        options["playlist_items"] = args.playlist_items
    if args.playlist_start:
        options["playliststart"] = args.playlist_start
    if args.playlist_end:
        options["playlistend"] = args.playlist_end

    if args.sleep_interval is not None:
        options["sleep_interval"] = args.sleep_interval
    if args.max_sleep_interval is not None:
        options["max_sleep_interval"] = args.max_sleep_interval
    if args.sleep_requests is not None:
        options["sleep_interval_requests"] = args.sleep_requests
    if args.http_chunk_size:
        options["http_chunk_size"] = parse_byte_size(args.http_chunk_size, "HTTP chunk size")

    if args.cookies:
        options["cookiefile"] = str(Path(args.cookies).expanduser())
    if args.cookies_from_browser:
        browser_spec = comma_separated_list(args.cookies_from_browser)
        options["cookiesfrombrowser"] = tuple(browser_spec)
    if args.username:
        options["username"] = args.username
    if args.password:
        options["password"] = args.password
    if args.netrc:
        options["usenetrc"] = True
    if args.video_password:
        options["videopassword"] = args.video_password

    if args.write_subs or args.write_auto_subs or args.embed_subs:
        options["writesubtitles"] = args.write_subs or args.embed_subs
        options["writeautomaticsub"] = args.write_auto_subs
        options["subtitleslangs"] = comma_separated_list(args.sub_langs)
        options["subtitlesformat"] = args.sub_format
        options["embedsubtitles"] = args.embed_subs

    postprocessors: list[dict[str, Any]] = []

    if args.audio_only:
        options["format"] = "bestaudio/best"
        postprocessors.append(
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": args.audio_format,
                "preferredquality": args.audio_quality,
            }
        )
    else:
        options["format"] = args.format

    if args.embed_metadata:
        postprocessors.append({"key": "FFmpegMetadata"})

    if args.embed_thumbnail:
        postprocessors.append({"key": "EmbedThumbnail"})

    if args.remux_video:
        postprocessors.append(
            {"key": "FFmpegVideoRemuxer", "preferedformat": args.remux_video}
        )

    if args.recode_video:
        postprocessors.append(
            {"key": "FFmpegVideoConvertor", "preferedformat": args.recode_video}
        )

    if args.sponsorblock_remove:
        postprocessors.append(
            {
                "key": "SponsorBlock",
                "remove_sponsor_segments": comma_separated_list(args.sponsorblock_remove),
            }
        )

    if postprocessors:
        options["postprocessors"] = postprocessors

    if args.keep_video:
        options["keepvideo"] = True

    return {key: value for key, value in options.items() if value is not None}


def main() -> int:
    try:
        args = parse_args()
        urls = gather_urls(args)
        options = build_options(args)
    except Exception as exc:  # pragma: no cover - CLI entry point safety
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    try:
        with YoutubeDL(options) as downloader:
            downloader.download(urls)
    except Exception as exc:  # pragma: no cover - passthrough for yt-dlp failures
        print(f"Download failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
