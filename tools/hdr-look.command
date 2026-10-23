#!/bin/zsh
# Thin launcher: XDRemux owns discovery, reconstruction, validation and publication.
set -u

hdr_root=${0:A:h}
hdr_cli=${XDREMUX_CLI:-}
if [[ -z "$hdr_cli" ]]; then
    for hdr_candidate in \
        "$hdr_root/bin/xdremux" \
        "/Applications/XDRemuxApp.app/Contents/Helpers/xdremux" \
        "$HOME/Applications/XDRemuxApp.app/Contents/Helpers/xdremux"; do
        if [[ -x "$hdr_candidate" ]]; then hdr_cli=$hdr_candidate; break; fi
    done
fi
if [[ -z "$hdr_cli" ]] && (( $+commands[xdremux] )); then hdr_cli=$commands[xdremux]; fi
if [[ -z "$hdr_cli" || ! -x "$hdr_cli" ]]; then
    print -u2 -- '找不到支持 hdr-look 的 XDRemux。请安装配套工具，或设置 XDREMUX_CLI。'
    exit 2
fi
if [[ -z ${XDREMUX_APPLE_ADAPTER:-} && -x "$hdr_root/bin/xdremux-apple-adapter" ]]; then
    export XDREMUX_APPLE_ADAPTER="$hdr_root/bin/xdremux-apple-adapter"
fi

if (( $# )); then
    exec "$hdr_cli" --lang "${XDREMUX_LANG:-zh-CN}" hdr-look --recursive "$@"
fi

print -- '摄影风格 HDR · 原图保留，输出仅有 HDR HEIC'
print -- '输入照片／文件夹路径，或从 Finder 拖入一个或多个项目：'
IFS= read -r hdr_line || exit 2
[[ -n "$hdr_line" ]] || exit 2
typeset -a hdr_inputs
if [[ -e "$hdr_line" ]]; then
    hdr_inputs=("$hdr_line")
else
    # Lex and unquote Finder's escaped paths; never evaluate shell expressions.
    hdr_inputs=("${(@Q)${(z)hdr_line}}")
fi
"$hdr_cli" --lang "${XDREMUX_LANG:-zh-CN}" hdr-look --recursive -- "${hdr_inputs[@]}"
hdr_exit=$?
if [[ -t 0 ]]; then
    print -- '按回车关闭。'
    IFS= read -r hdr_close
fi
exit $hdr_exit
