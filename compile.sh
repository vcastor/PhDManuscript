#!/bin/bash
# compile.sh — compile a LaTeX document with a spinner
# Usage: compile.sh LABEL LOGFILE CMD [TEXLOG]
#   LABEL   : human-readable label for the progress line
#   LOGFILE : file to append stdout/stderr of CMD
#   CMD     : full shell command to run (passed to eval)
#   TEXLOG  : .log produced by TeX itself (for last-file hint), optional

LABEL="${1:?label required}"
LOGFILE="${2:?logfile required}"
CMD="${3:?command required}"
TEXLOG="${4:-}"

# Remember where the log ends so on failure we can isolate this command's output
LOG_START=$(wc -c < "${LOGFILE}" 2>/dev/null || echo 0)

# ── spinner ────────────────────────────────────────────────────────────────
printf "  \033[36m◉\033[0m  %-48s" "${LABEL}..."

eval "${CMD}" >> "${LOGFILE}" 2>&1 &
PID=$!

i=0
while kill -0 "${PID}" 2>/dev/null; do
  case $((i % 4)) in
    0) c='|' ;; 1) c='/' ;; 2) c='-' ;; *) c='+' ;;
  esac
  printf "\b\033[33m%s\033[0m" "${c}"
  sleep 0.2
  i=$((i + 1))
done

wait "${PID}"; STATUS=$?

# ── result ─────────────────────────────────────────────────────────────────
if [ "${STATUS}" -eq 0 ]; then
  printf "\b \033[32m✓\033[0m\n"
  exit 0
fi

printf "\b \033[31m✗\033[0m\n"

# ── bibtex-specific failure ────────────────────────────────────────────────
if echo "${CMD}" | grep -qE '\bbibtex\b'; then
  printf "\n  \033[31m>>> BibTeX failed — 'Error' lines:\033[0m\n\n"
  tail -c "+$((LOG_START + 1))" "${LOGFILE}" | grep --color=always -iE \
    'article|book|misc|phdthesis|unpublished|incollection|bibl|bib|error|$' \
    || tail -c "+$((LOG_START + 1))" "${LOGFILE}"
  printf "\n"
  exit 1
fi

# ── LaTeX / generic failure ────────────────────────────────────────────────
printf "\n  \033[31m>>> Compilation failed — last 20 log lines:\033[0m\n\n"
tail -n 20 "${LOGFILE}" | grep --color=always -E '[^ )]+\.tex|l\.[0-9]+|$'

if [ -n "${TEXLOG}" ] && [ -f "${TEXLOG}" ]; then
  TEXLINE=$(grep -n '\.tex$' "${TEXLOG}" 2>/dev/null | tail -1 | cut -d: -f1)
  if [ -n "${TEXLINE}" ]; then
    RAW=$(head -n "${TEXLINE}" "${TEXLOG}" | tail -1)
    N="${TEXLINE}"
    while ! echo "${RAW}" | grep -qE '[\[\(]' && [ "${N}" -gt 1 ]; do
      N=$((N-1))
      PREV=$(head -n "${N}" "${TEXLOG}" | tail -1)
      RAW="${PREV}${RAW}"
    done
    LAST_TEX=$(echo "${RAW}" | awk '{if(NF>1)print $NF; else print}' | sed 's/^(//')
  fi
  if [ -n "${LAST_TEX}" ]; then
    printf "\n  \033[33m>>> Last .tex file referenced:\033[0m\n"
    printf "  \033[35m%s\033[0m\n" "${LAST_TEX}"
  fi
fi
printf "\n"
exit 1

