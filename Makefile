# Variables
PYTHON      = python3
MAIN        = pac-man.py config.json

# Default Rule
all: install lint run

# Install activity dependencies
install:
	$(PYTHON) -m pip install pygame flake8 mypy

# Execute the main script
run:
	$(PYTHON) $(MAIN)

# Run in debug mode using pdb
debug:
	$(PYTHON) -m pdb $(MAIN)

# Remove temporary files and caches
clean:
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf .mypy_cache
	rm -f highscores.json

# lint flags
lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

# Enhanced checking
lint-strict:
	flake8 .
	mypy . --strict

.PHONY: all install run debug clean lint lint-strict