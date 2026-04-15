#!/usr/bin/env sh
# watch_and_run.sh
# プロジェクトルートで使うファイル監視 + uv 実行スクリプト
# 使い方: ./watch_and_run.sh <input.md> [interval_sec]
set -eu

INPUT="${1:-}"
INTERVAL="${2:-1}"

if [ -z "${INPUT}" ]; then
  echo "使い方: $0 <input.md> [interval_sec]"
  exit 2
fi

# デバウンス（保存の連続トリガ抑止）
DEBOUNCE_SEC=0.2

timestamp() {
  date '+%Y-%m-%d %H:%M:%S'
}

# mtime を取得（macOS/GNU互換）
get_mtime() {
  if command -v stat >/dev/null 2>&1; then
    # macOS: stat -f "%m" ; GNU: stat -c "%Y"
    stat -f "%m" "${INPUT}" 2>/dev/null || stat -c "%Y" "${INPUT}" 2>/dev/null || printf ""
  else
    printf ""
  fi
}

run_once() {
  echo "[$(timestamp)] 実行: uv run main.py \"${INPUT}\""
  # uv を使うプロジェクト環境で実行する想定
  uv run main.py "${INPUT}"
  echo "[$(timestamp)] 実行完了"
}

cleanup_and_exit() {
  echo "[$(timestamp)] 監視停止"
  exit 0
}

trap 'cleanup_and_exit' INT TERM

# 初回実行（ファイルが存在すれば）
LAST_MTIME=""
if [ -f "${INPUT}" ]; then
  LAST_MTIME="$(get_mtime)"
  if [ -n "${LAST_MTIME}" ]; then
    run_once
  fi
fi

echo "[$(timestamp)] 監視開始: ${INPUT} （間隔: ${INTERVAL}s） Ctrl+Cで停止"

while :; do
  sleep "${INTERVAL}"

  if [ ! -f "${INPUT}" ]; then
    if [ -n "${LAST_MTIME}" ]; then
      echo "[$(timestamp)] ファイルが削除されました: ${INPUT}"
      LAST_MTIME=""
    fi
    continue
  fi

  MT="$(get_mtime)"
  if [ -z "${MT}" ]; then
    continue
  fi

  if [ "${MT}" != "${LAST_MTIME}" ]; then
    # 少し待って保存完了を待つ（デバウンス）
    sleep "${DEBOUNCE_SEC}"
    # 再取得して変化がなければスキップ
    MT2="$(get_mtime)"
    if [ -z "${MT2}" ]; then
      continue
    fi
    if [ "${MT2}" = "${LAST_MTIME}" ]; then
      continue
    fi
    LAST_MTIME="${MT2}"
    echo "[$(timestamp)] 変更検出: 再変換を実行します"
    run_once || echo "[$(timestamp)] 実行でエラーが発生しました"
  fi
done
