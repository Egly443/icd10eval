#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_image="$project_root/assets/epicode-explainer-storyboard.png"
subtitles="$project_root/assets/epicode-explainer.ass"
output="$project_root/src/synthetic_episode_studio/static/media/epicode-explainer.mp4"
poster="$project_root/src/synthetic_episode_studio/static/media/epicode-explainer-poster.jpg"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

ffmpeg -hide_banner -loglevel error -y -i "$source_image" -filter_complex \
  "[0:v]crop=546:442:6:24[p1];[0:v]crop=546:442:560:24[p2];[0:v]crop=551:442:1114:24[p3];[0:v]crop=546:441:6:476[p4];[0:v]crop=546:441:560:476[p5];[0:v]crop=551:441:1114:476[p6]" \
  -map '[p1]' "$work/1.png" -map '[p2]' "$work/2.png" -map '[p3]' "$work/3.png" \
  -map '[p4]' "$work/4.png" -map '[p5]' "$work/5.png" -map '[p6]' "$work/6.png"

ffmpeg -hide_banner -loglevel error -y \
  -i "$work/1.png" -i "$work/2.png" -i "$work/3.png" -i "$work/4.png" -i "$work/5.png" -i "$work/6.png" \
  -f lavfi -i "sine=frequency=740:duration=0.20:sample_rate=48000" \
  -filter_complex \
  "[0:v]scale=1408:792:force_original_aspect_ratio=increase,zoompan=z='min(zoom+0.00018,1.045)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=300:s=1280x720:fps=30[v0];\
   [1:v]scale=1408:792:force_original_aspect_ratio=increase,zoompan=z='min(zoom+0.00016,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=300:s=1280x720:fps=30[v1];\
   [2:v]scale=1408:792:force_original_aspect_ratio=increase,zoompan=z='min(zoom+0.00020,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=300:s=1280x720:fps=30[v2];\
   [3:v]scale=1408:792:force_original_aspect_ratio=increase,zoompan=z='min(zoom+0.00016,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=300:s=1280x720:fps=30[v3];\
   [4:v]scale=1408:792:force_original_aspect_ratio=increase,zoompan=z='min(zoom+0.00018,1.045)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=300:s=1280x720:fps=30[v4];\
   [5:v]scale=1408:792:force_original_aspect_ratio=increase,zoompan=z='min(zoom+0.00020,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=300:s=1280x720:fps=30[v5];\
   [v0][v1][v2][v3][v4][v5]concat=n=6:v=1:a=0,subtitles='$subtitles'[video];\
   [6:a]asplit=7[a0][a1][a2][a3][a4][a5][a6];\
   [a0]volume=0.16[c0];[a1]adelay=10000|10000,volume=0.13[c1];[a2]adelay=20000|20000,volume=0.13[c2];\
   [a3]adelay=30000|30000,volume=0.13[c3];[a4]adelay=40000|40000,volume=0.13[c4];\
   [a5]adelay=50000|50000,volume=0.13[c5];[a6]adelay=58100|58100,volume=0.18[c6];\
   [c0][c1][c2][c3][c4][c5][c6]amix=inputs=7:duration=longest,apad=pad_dur=60[audio]" \
  -map '[video]' -map '[audio]' -t 60 -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart "$output"

ffmpeg -hide_banner -loglevel error -y -ss 0.25 -i "$output" -frames:v 1 -q:v 2 "$poster"
echo "Built $output"
