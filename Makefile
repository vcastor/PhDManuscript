# ################################################################################
# Makefile de la thèse que me hará doctora (o eso espero) ✨
#
# Ce Makefile compile le document principal, génère les graphiques avec Python,
# exécute BibTeX et makeglossaries, et fournit des commandes supplémentaires pour
# un flux de travail automatisé et robuste.
#
# Requirements:
#   - LaTeX (lualatex)
#   - BibTeX
#   - makeglossaries
#   - Python3 for generating plots
#   - GNU Make (obviously)
#																			 🏗️
# ################################################################################

MAIN      = tesis.tex
MAINBASE  = $(basename $(MAIN))
STYLE     = style_template.tex
LATEX     = lualatex
BIBTEX    = bibtex
MAKEGLOSS = makeglossaries
PYTHON    = /usr/bin/python3
LOGFILE   = make.log
FLAGS     = -interaction=nonstopmode -halt-on-error
PYPLOT    = $(wildcard methodology/mlearning/img/*py methodology/foundations/plt/*py results/qtaim/img/memory.py)
SVGFIG    = $(wildcard appendix/img/*svg methodology/dft/img/*svg methodology/comp_details/img/*svg methodology/solvation/img/*svg methodology/solvation/img/*svg results/nucleophilicity/diagramas/*svg)
TEX       = $(wildcard *.tex */*.tex bibl/*.bib)

# Prints info to the console and log file
define log_echo
	@echo $(1) | tee -a $(LOGFILE)
endef

# Prints the last 20 lines of the log file and the last TeX file
define print_error
	tail -n 20 $(LOGFILE); \
	echo ""; \
	echo ">>> Last TeX file:"; \
	grep '\.tex'  $(MAINBASE).log | tail -1
endef
# grep "^(" $(MAINBASE).log | grep '\.tex' | tail -1

################################################################################

# Clean log files
clean-log:
	@if [ -f $(LOGFILE) ]; then rm $(LOGFILE); fi

# Help target: lists all available commands
help:
	@echo "==================================================================="
	@echo "                         Available Commands"
	@echo "==================================================================="
	@echo " Available targets:"
	@echo "  all       - Full compilation (runs plots and LaTeX)"
	@echo "  plots     - Generate plots"
	@echo "  svg       - Convert the svg figures to pdf"
	@echo "  png       - From xcf GIMP files to png (BE SURE WHAT YOU DO)"
	@echo "  img       - svg + plots [NO xcf]"
	@echo "  tex       - Compile full thesis (with bib and glossaries)"
	@echo "  fast      - Fast compile (no bib or glossaries)"
	@echo "  style     - Compile style templated"
	@echo "  bib       - Compile bibliography only"
	@echo "  clean     - Remove auxiliary files"
	@echo "  "
	@echo "  test      - Compile an individual chapter"
	@echo "  test chapter=<name> [bib=true] - Compile a specific chapter"
	@echo "==================================================================="

################################################################################
# Main targets
all: img tex
img: svg plots

#
# python plots
plots:
	@$(call log_echo,">>> Generating plots... 🐍")
	@for f in $(PYPLOT); do \
		$(PYTHON) $$f || exit 1; \
	done

#
# XCF to PNG conversion (BE SURE WHAT YOU DO)
# I never use this, tbh
png:
	@$(call log_echo,">>> Converting XCF files to PNG... 🖼️")
	@for f in $(wildcard appendix/img/*xcf); do \
		if [ -f "$$f" ]; then \
			gimp -i -b '(let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "$$f" "$$f"))) (drawable (car (gimp-image-get-active-layer image)))) (file-png-save RUN-NONINTERACTIVE image drawable "$${f%.xcf}.png" "$${f%.xcf}.png" 0 9 0 0 0 0 0) (gimp-image-delete image))' -b '(gimp-quit 0)'; \
		fi; \
	done

#
# SVG to PDF conversion
svg:
	@$(call log_echo,">>> Converting SVG files to PDF... 📄")
	@for f in $(SVGFIG); do \
		if [ -f "$$f" ]; then \
			rsvg-convert -f pdf -o $${f%.svg}.pdf $$f; \
		fi; \
	done

#
# All LaTeX compilation
tex: $(TEX) clean-log
	@$(call log_echo,">>> Compiling $(MAIN) for first time... 📄")
	@$(LATEX) $(FLAGS) $(MAIN) >> $(LOGFILE) || { \
		echo ">>> ❌ First LaTeX run failed. Showing last 20 lines:"; \
		$(print_error); exit 1; }
	@$(call log_echo,">>> Running bibtex...")
	@$(BIBTEX) $(MAINBASE) >> $(LOGFILE) || true
	@$(call log_echo,">>> Running makeglossaries...")
	@$(MAKEGLOSS) $(MAINBASE) >> $(LOGFILE) 2>> $(LOGFILE) || true
	@$(call log_echo,">>> Second LaTeX pass with bib and glossaries...")
	@$(LATEX) $(FLAGS) $(MAIN) >> $(LOGFILE) || { \
		echo ">>> ❌ Second LaTeX run failed. Showing last 20 lines:"; \
		$(print_error); exit 1; }
	@$(call log_echo,">>> Final LaTeX pass...")
	@$(LATEX) $(FLAGS) $(MAIN) >> $(LOGFILE) || true
	@$(call log_echo,">>> ✅ Compilation finished successfully. Check $(LOGFILE) for details.")

#
# Fast compile (no bib or glossaries)
fast: $(TEX) clean-log
	@$(call log_echo,">>> Compiling just the main file no bib or glossaries...")
	@$(LATEX) $(FLAGS) $(MAIN) >> $(LOGFILE) || { \
		echo ">>> ❌ Fast LaTeX run failed. Showing last 20 lines:"; \
		$(print_error); exit 1; }
	@$(call log_echo,">>> ✅ Fast LaTeX run finished successfully.")

#
# Compile individual chapter (example: make test chapter=intro [bib=true])
chapter ?= intro
bib ?= false

test: test_private clean
test_private: clean-log
	@$(call log_echo,">>> Compiling $(chapter)")
	@if [ "$(chapter)" = "intro" ]; then \
		cp .chapter_test.tex intro.tex; \
	else \
		sed 's|\\subimport{intro/}{introduction}|\\subimport{$(chapter)/}{$(chapter).tex}|' .chapter_test.tex > $(chapter).tex; \
	fi
	@$(LATEX) $(FLAGS) $(chapter).tex > $(LOGFILE) 2>&1 || { \
		echo ">>> ❌ Fast LaTeX run failed. Showing last 20 lines:"; \
		$(print_error); exit 1; }
	@if [ "$(bib)" = "true" ]; then \
		echo ">>> Running BibTeX for $(chapter)"; \
		$(BIBTEX) $(basename $(chapter)) >> $(LOGFILE) || true ; \
		$(LATEX) $(FLAGS) $(chapter).tex >> $(LOGFILE) 2>&1; \
		$(LATEX) $(FLAGS) $(chapter).tex >> $(LOGFILE) 2>&1; \
	fi
	rm -f $(chapter).tex
	@$(call log_echo,">>> ✅ Chapter finished successfully.")

################################################################################
# Compile bibliography or glossaries only
bib:
	$(BIBTEX) $(MAINBASE)
gloss:
	$(MAKEGLOSS) $(MAINBASE)

# Compile the template style
style:
	@cp .$(STYLE) style_template.tex
	$(LATEX) $(STYLE) >> /dev/null
	@rm -f style_template.* !(style_template.pdf)

# Clean auxiliary files
clean:
	@echo ">>> Cleaning up... 🧹"
	@rm -rf */*.aux *.aux *.bbl *.blg *.glg *.glo *.gls *.ist *.log *.not \
		*.ntt *.out *.sbl *.sym *.tld *.toc *.alg *.acn *.acr *.err *.listing

################################################################################
.PHONY: all plots tex fast style bib gloss clean test help clean-log

