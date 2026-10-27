#!/usr/bin/env bash
# Build/run availability and isolated constructor probes without personal media.
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

# Constructor exploration runs in separate processes because undefined use
# cases and virtualized Metal kernels may abort rather than throw exceptions.
ulimit -c 0
for trial in 0 1 2 3 0-nil 1-nil; do
  use_case="${trial%%-*}"
  constructor_path="${RUNNER_TEMP:-/tmp}/smartstyle-constructor-${trial}.json"
  probe_args=("${constructor_path}" --constructor "${use_case}")
  if [[ "${trial}" == *-nil ]]; then
    probe_args+=(--nil-queue)
  fi
  set +e
  "${probe_bin}" "${probe_args[@]}" \
    >"${RUNNER_TEMP:-/tmp}/smartstyle-constructor-${trial}.stdout" \
    2>"${RUNNER_TEMP:-/tmp}/smartstyle-constructor-${trial}.stderr"
  status=$?
  set -e
  if [[ ${status} -ne 0 ]]; then
    printf '{"attempted":true,"trial":"%s","use_case":%s,"exit_status":%s,"constructed":false,"note":"process failed; see stderr artifact"}\n' \
      "${trial}" "${use_case}" "${status}" >"${constructor_path}"
  fi
  printf 'Smart Style constructor trial=%s exit=%s\n' "${trial}" "${status}"
  sed -n '1,20p' "${RUNNER_TEMP:-/tmp}/smartstyle-constructor-${trial}.stderr"
done
