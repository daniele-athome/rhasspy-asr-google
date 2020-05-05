SHELL := bash

PYTHON_NAME = rhasspyasr_google
PYTHON_FILES = $(PYTHON_NAME)/*.py *.py
DOWNLOAD_DIR = download

platform = $(shell sh platform.sh)

.PHONY: reformat check venv dist downloads

all: venv

reformat:
	scripts/format-code.sh $(PYTHON_FILES)

check:
	scripts/check-code.sh $(PYTHON_FILES)

venv: downloads
	scripts/create-venv.sh

dist:
	scripts/build-wheel.sh $(platform)

test:
	scripts/run-tests.sh

# -----------------------------------------------------------------------------
# Downloads
# -----------------------------------------------------------------------------

# Rhasspy development dependencies
RHASSPY_DEPS := $(shell grep '^rhasspy-' requirements.txt | sort | comm -3 - rhasspy_wheels.txt | sed -e 's|^|$(DOWNLOAD_DIR)/|' -e 's/==/-/' -e 's/$$/.tar.gz/')

$(DOWNLOAD_DIR)/%.tar.gz:
	mkdir -p "$(DOWNLOAD_DIR)"
	scripts/download-dep.sh "$@"

downloads: $(RHASSPY_DEPS)
