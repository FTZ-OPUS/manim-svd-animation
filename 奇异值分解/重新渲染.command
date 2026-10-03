#!/bin/zsh
set -e
cd "$(dirname "$0")"
/Users/fengtianzhu/venvs/manim/bin/python -m manim -qh '奇异值分解科普.py' SVDExplainer --media_dir './升级高清'
cp './升级高清/videos/奇异值分解科普/1080p60/SVDExplainer.mp4' './奇异值分解科普动画_1080P60.mp4'
open './奇异值分解科普动画_1080P60.mp4'
