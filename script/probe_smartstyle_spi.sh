#!/usr/bin/env bash
# Build/run the isolated, read-only Smart Style SPI availability probe.
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo 'usage: bash script/probe_smartstyle_spi.sh OUTPUT_JSON' >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
output_path="$1"
probe_bin="${RUNNER_TEMP:-/tmp}/smartstyle-spi-probe"

clang -std=gnu11 -fobjc-arc -Wall -Wextra -Werror \
  -framework Foundation -framework Metal \
  "${repo_root}/tools/smartstyle_spi_probe.m" \
  -o "${probe_bin}"

"${probe_bin}" "${output_path}"
