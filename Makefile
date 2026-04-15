# ############################################################################## #
# Makefile de la thèse que me hará doctora (o eso espero) ✨                     #
#                                                                                #
# Ce Makefile compile le document principal, génère les graphiques avec Python,  #
# exécute BibTeX et makeglossaries, et fournit des commandes supplémentaires     #
# pour un flux de travail automatisé et robuste.                                 #
#                                                                                #
# Requirements:                                                                  #
#   - LaTeX (lualatex)                                                           #
#   - BibTeX                                                                     #
#   - makeglossaries                                                             #
#   - Python3 for generating plots                                               #
#   - GNU Make (obviously)                                                       #
#                                                                       🏗️       #
# ############################################################################## #

SHELL      := /bin/bash
MAIN       := tesis.tex
MAINBASE   := $(basename $(MAIN))
STYLE      := style_template.tex
STYLE_SRC  := .$(STYLE)
LATEX      := lualatex
BIBTEX     := bibtex
MAKEGLOSS  := makeglossaries
PYTHON     := /usr/bin/python3
SPIN       := ./compile.sh
CONFIGURE  := ./checkdeps.sh
LOGFILE    := make.log
FLAGS      := -interaction=nonstopmode -halt-on-error
PYPLOT     := $(wildcard methodology/mlearning/img/*py methodology/foundations/plt/*py results/qtaim/img/memory.py)
SVGFIG     := $(wildcard appendix/img/*svg methodology/dft/img/*svg methodology/comp_details/img/*svg methodology/solvation/img/*svg methodology/solvation/img/*svg results/nucleophilicity/diagramas/*svg)
TEX        := $(wildcard *.tex */*.tex bibl/*.bib)
KEEP_LOGS  ?= false
chapter    ?= intro
bib        ?= false

AUX_EXTS   := aux bbl blg glg glo gls ist not ntt out sbl sym tld toc alg acn acr err listing log

ifneq ($(filter keep-logs,$(MAKECMDGOALS)),)
KEEP_LOGS := true
endif


# ── helpers ────────────────────────────────────────────────────────────────────

# Prints info to the console and log file
define log_echo
	@echo $(1) | tee -a $(LOGFILE)
endef

# animation for the compilation process
define spin_tex
	@$(SPIN) "$(1)" "$(LOGFILE)" "$(2)" "$(3)"
endef

define spin_cmd
	@$(SPIN) "$(1)" "$(LOGFILE)" "$(2)"
endef

define spin_cmd_soft
	@$(SPIN) "$(1)" "$(LOGFILE)" "($(2)) || true"
endef

# Clean output
define post_compile
	@if [ "$(KEEP_LOGS)" != "true" ]; then \
		$(MAKE) --no-print-directory clean; \
	else \
		echo ">>> Keeping auxiliary and log files"; \
	fi
endef

################################################################################
# info
.DEFAULT_GOAL := tex

help:
	@echo "==================================================================="
	@echo "                         Available Commands"
	@echo "==================================================================="
	@echo " Available targets:"
	@echo "  all            - Full compilation (runs plots and LaTeX)"
	@echo "  plots          - Generate plots"
	@echo "  svg            - Convert SVG figures to PDF"
	@echo "  png            - From XCF GIMP files to PNG"
	@echo "  img            - svg + plots [NO xcf]"
	@echo "  tex            - Compile full thesis (with bib and glossaries)"
	@echo "  fast           - Fast compile (no bib or glossaries)"
	@echo "  style          - Compile style template"
	@echo "  bib            - Compile bibliography only"
	@echo "  gloss          - Compile glossaries only"
	@echo "  clean          - Remove auxiliary files"
	@echo "  test           - Compile an individual chapter"
	@echo "  config         - Check project dependencies"
	@echo "  config-install - Check and install missing Python packages"
	@echo "  "
	@echo " Flags:"
	@echo "  make tex KEEP_LOGS=true"
	@echo "  make tex keep-logs"
	@echo ""
	@echo "                                                  ~ Happy writing! "
	@echo "==================================================================="

################################################################################
# Main targets
all: img tex
img: svg plots

plots:
	@$(call log_echo,">>> Generating plots... 🐍")
	@for f in $(PYPLOT); do \
		d=$$(dirname $$f); \
		b=$$(basename $$f); \
		( cd $$d && $(PYTHON) $$b ) >> $(LOGFILE) 2>&1 || exit 1; \
	done

# XCF to PNG conversion (BE SURE WHAT YOU DO)
# I never use this, tbh
png:
	@$(call log_echo,">>> Converting XCF files to PNG... 🖼️")
	@for f in $(wildcard appendix/img/*xcf); do \
		if [ -f "$$f" ]; then \
			gimp -i -b '(let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "$$f" "$$f"))) (drawable (car (gimp-image-get-active-layer image)))) (file-png-save RUN-NONINTERACTIVE image drawable "$${f%.xcf}.png" "$${f%.xcf}.png" 0 9 0 0 0 0 0) (gimp-image-delete image))' -b '(gimp-quit 0)' >> $(LOGFILE) 2>&1 || exit 1; \
		fi; \
	done

# SVG to PDF conversion
svg:
	@$(call log_echo,">>> Converting SVG files to PDF... 📄")
	@for f in $(SVGFIG); do \
		if [ -f "$$f" ]; then \
			rsvg-convert -f pdf -o $${f%.svg}.pdf $$f >> $(LOGFILE) 2>&1 || exit 1; \
		fi; \
	done

################################################################################
# LaTeX compilation

tex: $(TEX) clean-log
	@$(call log_echo,">>> Full compilation of $(MAIN)...")
	$(call spin_tex,First LaTeX pass,$(LATEX) $(FLAGS) $(MAIN),$(MAINBASE).log)
	$(call spin_cmd_soft,BibTeX,$(BIBTEX) $(MAINBASE))
	$(call spin_cmd_soft,Make glossaries,$(MAKEGLOSS) $(MAINBASE))
	$(call spin_tex,Second LaTeX pass,$(LATEX) $(FLAGS) $(MAIN),$(MAINBASE).log)
	@$(call spin_tex,Final LaTeX pass,$(LATEX) $(FLAGS) $(MAIN),$(MAINBASE).log)
	$(call post_compile)

# $(call spin_tex,Fast LaTeX pass,$(LATEX) $(FLAGS) $(MAIN),$(LOGFILE))
fast: $(TEX) clean-log
	@$(call log_echo,">>> Fast compilation of $(MAIN)...")
	$(call spin_tex,Fast LaTeX pass,$(LATEX) $(FLAGS) $(MAIN),$(MAINBASE).log)
	$(call post_compile)

test: test_private clean
test_private: clean-log
	@$(call log_echo,">>> Compiling $(chapter)")
	@if [ "$(chapter)" = "intro" ]; then \
		cp .chapter_test.tex intro.tex; \
	else \
		sed 's|\\subimport{intro/}{introduction}|\\subimport{$(chapter)/}{$(chapter).tex}|' .chapter_test.tex > $(chapter).tex; \
	fi
	$(call spin_tex,LaTeX $(chapter),$(LATEX) $(FLAGS) $(chapter).tex,$(chapter).log)
	@if [ "$(bib)" = "true" ]; then \
		$(SPIN) "BibTeX $(chapter)" "$(LOGFILE)" "($(BIBTEX) $(chapter)) || true" && \
		$(SPIN) "LaTeX $(chapter) 2nd" "$(LOGFILE)" "$(LATEX) $(FLAGS) $(chapter).tex" "$(chapter).log" && \
		$(SPIN) "LaTeX $(chapter) 3rd" "$(LOGFILE)" "$(LATEX) $(FLAGS) $(chapter).tex" "$(chapter).log"; \
	fi
	@rm -f $(chapter).tex
	@$(call log_echo,">>> ✅ Chapter finished successfully.")

################################################################################
# Standalone tools

bib:
	$(BIBTEX) $(MAINBASE)
gloss:
	$(MAKEGLOSS) $(MAINBASE)

style:
	@cp $(STYLE_SRC) $(STYLE)
	$(call spin_tex,Style template,$(LATEX) $(FLAGS) $(STYLE),style_template.log)
	@rm -f style_template.* !(style_template.pdf)
	$(call post_compile)

################################################################################
# Configuration

config:
	@$(CONFIGURE)

config-install:
	@$(CONFIGURE) --install

################################################################################
# Cleanup

clean-log:
	@rm -f $(LOGFILE)
clean:
	@echo ">>> Cleaning up... 🧹"
	@rm -f $(foreach ext,$(AUX_EXTS),*.$(ext) */*.$(ext))

keep-logs:
	@:

.PHONY: all img plots png svg tex fast test test_private bib gloss style clean clean-log help keep-logs

