#!/bin/zsh
set -e
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
task_python="/Users/retriedstormtrooper/.pyenv/versions/3.13.14/bin/python3"
if [[ ! -x "$task_python" ]]; then task_python="$(command -v python3)"; fi
"$task_python" "${0:A:h}/rebuild.py" "$@"
if [[ $# -eq 0 ]]; then read -r "?处理结束，按回车关闭。"; fi
