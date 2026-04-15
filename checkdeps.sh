#!/bin/bash
# configure.sh — check (and optionally install) project dependencies
# Usage: configure.sh [--install]
#   --install : auto-install missing Python packages via pip

set -e

INSTALL=false
[ "${1:-}" = "--install" ] && INSTALL=true

# ── formatting helpers ─────────────────────────────────────────────────────
ok()   { printf "  \033[32m✓\033[0m  %-28s %s\n" "$1" "$2"; }
warn() { printf "  \033[33m⚠\033[0m  %-28s %s\n" "$1" "$2"; }
fail() { printf "  \033[31m✗\033[0m  %-28s %s\n" "$1" "$2"; }
info() { printf "  \033[36m◉\033[0m  %s\n" "$1"; }

HAS_ERR=0

# ── macOS or Linux? ────────────────────────────────────────────────────────
case "$(uname -s)" in
  Darwin) OS="macOS" ;;
  Linux)  OS=$(lsb_release -is 2>/dev/null || echo "Linux") ;;
  *)      fail "OS" "unsupported operating system: $(uname -s)"; exit 1 ;;
esac

# ── OS-aware install hint ──────────────────────────────────────────────────
pkg_hint() {
  local brew="$1" apt="$2"
  case "${OS}" in
    macOS)         echo "brew install ${brew}" ;;
    Ubuntu|Debian) echo "sudo apt install ${apt}" ;;
    Fedora)        echo "sudo dnf install ${apt}" ;;
    Arch)          echo "sudo pacman -S ${apt}" ;;
    *)             echo "install ${apt} with your package manager" ;;
  esac
}

# portable sed -i (macOS needs '')
sedi() {
   if [ "$(uname -s)" = "Darwin" ]; then
      sed -i '' -e "$@"
   else
      sed -i -e "$@"
   fi
}

check_bin() {
  local label="$1" cmd="$2" required="${3:-true}" hint="${4:-}"
  if command -v "${cmd}" &>/dev/null; then
    local ver
    ver=$("${cmd}" --version 2>&1 | head -1) || ver="(unknown version)"
    ok "${label}" "${ver}"
  elif [ "${required}" = "true" ]; then
    fail "${label}" "not found${hint:+ — ${hint}}"
    HAS_ERR=1
  else
    warn "${label}" "not found (optional)${hint:+ — ${hint}}"
  fi
}

# ── macOS .app symlinker ──────────────────────────────────────────────────
check_mac_app() {
  local label="$1" cmd="$2" app_path="$3" hint="$4"
  if command -v "${cmd}" &>/dev/null; then
    ok "${label}" "$("${cmd}" --version 2>&1 | head -1)"
  elif [ "${OS}" = "macOS" ] && [ -x "${app_path}" ]; then
    warn "${label}" "found at ${app_path} but not in PATH"
    info "Creating symlink: /usr/local/bin/${cmd} → ${app_path}"
    ln -sf "${app_path}" "/usr/local/bin/${cmd}" 2>/dev/null && \
      ok "${label}" "symlink created" || \
      warn "${label}" "symlink failed — try: sudo ln -s ${app_path} /usr/local/bin/${cmd}"
  else
    warn "${label}" "not found (optional)${hint:+ — ${hint}}"
  fi
}

# ── Python packages required by the plotting scripts ───────────────────────
PY_PACKAGES=(matplotlib numpy) # networkx sklearn diagrams math sqlite3

# ── header ─────────────────────────────────────────────────────────────────
echo ""
info "Checking project dependencies... [${OS}]"
echo ""

# ── system tools ───────────────────────────────────────────────────────────
info "System tools"

if [ -n "${BASH_VERSION:-}" ]; then
  ok "bash" "bash ${BASH_VERSION}"
else
  fail "bash" "not running under bash"
  HAS_ERR=1
fi

check_bin "GNU Make" make true "$(pkg_hint make build-essential)"
check_bin "rsvg-convert" rsvg-convert false "$(pkg_hint librsvg librsvg2-bin)"
check_mac_app "GIMP" gimp "/Applications/GIMP.app/Contents/MacOS/gimp" \
  "needed only for XCF→PNG; $(pkg_hint gimp gimp)"
check_mac_app "Inkscape" inkscape "/Applications/Inkscape.app/Contents/MacOS/inkscape" \
  "needed for SVG→PDF; $(pkg_hint inkscape inkscape)"

echo ""

# ── LaTeX toolchain ────────────────────────────────────────────────────────
info "LaTeX toolchain"

LATEX_HINT="install a TeX distribution — https://www.latex-project.org/get/#tex-distributions"
check_bin "lualatex" lualatex true "${LATEX_HINT}"
check_bin "bibtex"   bibtex  true "${LATEX_HINT}"

if command -v makeglossaries &>/dev/null; then
  ok "makeglossaries" "$(makeglossaries --version 2>&1 | head -1)"
elif command -v perl &>/dev/null; then
  fail "makeglossaries" "not found — install the glossaries LaTeX package"
  HAS_ERR=1
else
  fail "makeglossaries" "not found (perl missing too)"
  HAS_ERR=1
fi

echo ""

# ── Python ─────────────────────────────────────────────────────────────────
info "Python environment"

PYTHONS=$(echo "${PATH}" | tr ':' '\n' | while read -r d; do
  find "${d}" -maxdepth 1 -name 'python*' -type f 2>/dev/null
done | sort -u)

if [ -z "${PYTHONS}" ]; then
  fail "python" "no python found in PATH"
  HAS_ERR=1
else
  BEST=""
  while IFS= read -r py; do
    name=$(basename "${py}")
    ver=$("${py}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null) || continue
    n_ok=0
    for pkg in "${PY_PACKAGES[@]}"; do
      "${py}" -c "import ${pkg}" 2>/dev/null && n_ok=$((n_ok+1))
    done
    if [ "${n_ok}" -eq "${#PY_PACKAGES[@]}" ]; then
      ok "${name}" "${ver} — all packages found"
      BEST="${py}"
    elif [ "${n_ok}" -gt 0 ]; then
      warn "${name}" "${ver} — ${n_ok}/${#PY_PACKAGES[@]} packages"
    else
      warn "${name}" "${ver} — no required packages"
    fi
  done <<< "${PYTHONS}"

  if [ -n "${BEST}" ]; then
    echo ""
    info "Selected: ${BEST}"
    for pkg in "${PY_PACKAGES[@]}"; do
      pkgver=$("${BEST}" -c "import ${pkg}; print(${pkg}.__version__)" 2>/dev/null || echo "?")
      ok "  ${pkg}" "${pkgver}"
    done
    sedi "s|^PYTHON.*:=.*|PYTHON     := ${BEST}|" Makefile 2>/dev/null && \
      ok "Makefile" "PYTHON updated to ${BEST}"
  else
    echo ""
    fail "python" "no python has all required packages (${PY_PACKAGES[*]})"
    HAS_ERR=1

    PIP=""
    for p in pip3 pip; do
      command -v "${p}" &>/dev/null && PIP="${p}" && break
    done
    if [ "${INSTALL}" = "true" ] && [ -n "${PIP}" ]; then
      PY_FALLBACK=$(echo "${PYTHONS}" | tail -1)
      info "Installing with ${PIP}: ${PY_PACKAGES[*]}"
      ${PIP} install "${PY_PACKAGES[@]}"
      echo ""
      ALL_OK=true
      for pkg in "${PY_PACKAGES[@]}"; do
        if "${PY_FALLBACK}" -c "import ${pkg}" 2>/dev/null; then
          pkgver=$("${PY_FALLBACK}" -c "import ${pkg}; print(${pkg}.__version__)" 2>/dev/null || echo "?")
          ok "  ${pkg}" "${pkgver}"
        else
          fail "  ${pkg}" "installation failed"
          ALL_OK=false
        fi
      done
      if [ "${ALL_OK}" = "true" ]; then
        sedi "s|^PYTHON.*:=.*|PYTHON     := ${PY_FALLBACK}|" Makefile 2>/dev/null && \
          ok "Makefile" "PYTHON updated to ${PY_FALLBACK}"
        HAS_ERR=0
      fi
    else
      info "Run ./configure.sh --install to install them"
    fi
  fi
fi

# ── summary ────────────────────────────────────────────────────────────────
echo ""
if [ "${HAS_ERR}" -eq 0 ]; then
  printf "  \033[32m>>> All good — ready to compile.\033[0m\n\n"
  exit 0
else
  printf "  \033[31m>>> Some dependencies are missing (see above).\033[0m\n\n"
  exit 1
fi

