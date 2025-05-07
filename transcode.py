#!/usr/bin/env python3
import argparse
import os
import subprocess
from pathlib import Path
import shutil


def parse_args():
    parser = argparse.ArgumentParser(
        description="""
        Batch transcode video files using HandBrakeCLI.

        Features:
        - Supports recursive directory traversal (-r)
        - Filters by file extension (--ext)
        - Writes output as <original_name>-converted.mp4 in the same folder
        - Uses temporary file until successful completion to avoid partial outputs
        - Skips files that already have -converted.mp4 (unless --reprocess is used)
        - Supports --delete to remove source files after success or if -converted.mp4 already exists
        - Defaults to dry-run unless --commit (-c) is passed
        - Prints a summary after execution (or simulated summary in dry-run)

        Example usages:
          hbconvert --start . --ext mkv -r             # Dry-run, recursively find all .mkv files
          hbconvert --start ~/Videos --ext avi -r -c   # Actually transcode recursively
          hbconvert --start . --ext mkv -c --delete    # Transcode and delete source after success
          hbconvert --start . --ext mkv --reprocess    # Re-transcode even if output exists (dry-run)
          hbconvert --start . --ext mkv -c --delete    # Can be re-run to clean up sources afterward
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--start", type=str, default=".", help="Start path (default: current directory)")
    parser.add_argument("--ext", type=str, default="mkv", help="File extension to target (default: mkv)")
    parser.add_argument("-r", "-R", action="store_true", dest="recursive", help="Recursively search subdirectories")
    parser.add_argument("--reprocess", action="store_true", help="Reprocess files even if output exists")
    parser.add_argument("--delete", action="store_true", help="Delete source files after transcoding or if already converted")
    parser.add_argument("-c", "--commit", action="store_true", help="Actually perform changes (dry-run otherwise)")
    return parser.parse_args()


def find_target_files(start_path: Path, ext: str, recursive: bool):
    if recursive:
        return list(start_path.rglob(f"*.{ext}"))
    else:
        return list(start_path.glob(f"*.{ext}"))


def transcode_file(src: Path, dst: Path, dry_run: bool, index: int, total: int):
    tmp_dst = dst.with_suffix(".tmp.mp4")
    print(f"[{index}/{total}] Processing: {src.name}")

    if dry_run:
        print(f"[DRY RUN] Would transcode: {src} -> {dst}")
        return True

    try:
        process = subprocess.Popen([
            "HandBrakeCLI",
            "-i", str(src),
            "-o", str(tmp_dst),
            "-e", "x264",
            "-q", "20",
            "-B", "160",
            "--optimize"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        for line in process.stdout:
            if line.startswith("Encoding:"):
                print(line.strip(), end='\r', flush=True)

        process.wait()
        if process.returncode != 0:
            print(f"[{index}/{total}] [ERROR] Failed to transcode {src.name}")
            if tmp_dst.exists():
                tmp_dst.unlink()
            return False

        tmp_dst.rename(dst)
        print(f"\n[{index}/{total}] Done: {dst.name}")
        return True

    except Exception as e:
        print(f"[{index}/{total}] [EXCEPTION] {e}")
        if tmp_dst.exists():
            tmp_dst.unlink()
        return False


def main():
    args = parse_args()
    start = Path(args.start).resolve()
    targets = find_target_files(start, args.ext, args.recursive)

    total = len(targets)
    processed = []
    skipped = []
    deleted = []
    failed = []
    total_saved = 0
    
    print(f"\nFound {total} .{args.ext} file(s) to check.")

    for i, file in enumerate(targets, 1):
        dst = file.with_name(file.stem + "-converted.mp4")

        if dst.exists() and not args.reprocess:
            print(f"[{i}/{total}] Skipping (already exists): {file.name}")
            skipped.append(file)
            if args.commit and args.delete:
                file.unlink()
                deleted.append(file)
            continue

        src_size = file.stat().st_size
        success = transcode_file(file, dst, not args.commit, i, total)

        if success:
            processed.append((file, dst))
            if args.commit:
                new_size = dst.stat().st_size
                total_saved += (src_size - new_size)
                if args.delete:
                    file.unlink()
                    deleted.append(file)
        else:
            failed.append(file)

    print("\nSUMMARY")
    print("=======")
    print(f"Processed ({len(processed)}):")
    for src, dst in processed:
        print(f"  {src} -> {dst}")
    print(f"\nSkipped ({len(skipped)}):")
    for file in skipped:
        print(f"  {file}")
    print(f"\nDeleted ({len(deleted)}):")
    for file in deleted:
        print(f"  {file}")
    print(f"\nFailed ({len(failed)}):")
    for file in failed:
        print(f"  {file}")

    if args.commit:
        print(f"\nTotal space saved: {total_saved / (1024**2):.2f} MB")
    else:
        print("\n(DRY RUN — no files were modified. Use -c to commit changes.)")


if __name__ == "__main__":
    main()
