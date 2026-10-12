#!/usr/bin/env python3
"""Offline media metadata + COMPLETE video/audio decode using installed FFmpeg."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('file', type=Path)
    p.add_argument('--ffmpeg', default='ffmpeg')
    p.add_argument('--ffprobe', default='ffprobe')
    p.add_argument('--output', type=Path, default=Path('media_verification'))
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    h = hashlib.sha256()
    with a.file.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    probe = subprocess.run([a.ffprobe, '-v', 'error', '-count_frames', '-show_format',
                            '-show_streams', '-of', 'json', str(a.file.resolve())],
                           capture_output=True, text=True, check=True)
    metadata = json.loads(probe.stdout)
    (a.output / 'metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    # software decoding; no -c copy, no frame/time limit, all video/audio streams
    with (a.output / 'full_decode.log').open('wb') as log:
        decode = subprocess.run([a.ffmpeg, '-nostdin', '-v', 'info', '-xerror',
                                 '-i', str(a.file.resolve()), '-map', '0:v?', '-map', '0:a?',
                                 '-f', 'null', '-'], stdout=log, stderr=subprocess.STDOUT)
    result = {'sha256': h.hexdigest(), 'bytes': a.file.stat().st_size,
              'full_decode_exit_code': decode.returncode,
              'full_video_audio_decode_passed': decode.returncode == 0,
              'note': 'Readback/menu labels alone do not prove these file properties. This check does not establish every frame is intra; inspect frame types separately.'}
    (a.output / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    return decode.returncode


if __name__ == '__main__':
    raise SystemExit(main())
