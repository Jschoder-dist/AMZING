PYTHON   = python3
VENV     = venv
BIN      = $(VENV)/bin
MAIN     = a_maze_ing.py
CONFIG   = config.txt
RM       = rm -rf

GREEN  = \033[0;32m
CYAN   = \033[0;36m
RESET  = \033[0m

all: install
	@echo "$(GREEN)Ready. Run 'make run' to start.$(RESET)"

install:
	@echo "$(CYAN)Creating virtual environment and installing tools...$(RESET)"
	@$(PYTHON) -m venv $(VENV)
	@$(BIN)/pip install --upgrade pip --quiet
	@$(BIN)/pip install flake8 mypy --quiet
	@echo "$(GREEN)Done.$(RESET)"

run:
	@if [ ! -d "$(VENV)" ]; then make install; fi
	$(BIN)/python3 $(MAIN) $(CONFIG)

debug:
	@if [ ! -d "$(VENV)" ]; then make install; fi
	$(BIN)/python3 -m pdb $(MAIN) $(CONFIG)

lint:
	@if [ ! -d "$(VENV)" ]; then make install; fi
	@echo "$(CYAN)flake8...$(RESET)"
	@$(BIN)/flake8 . --exclude=$(VENV)
	@echo "$(CYAN)mypy...$(RESET)"
	@$(BIN)/mypy . --exclude $(VENV) \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
	@echo "$(GREEN)Lint passed.$(RESET)"

lint-strict:
	@if [ ! -d "$(VENV)" ]; then make install; fi
	@$(BIN)/flake8 .
	@$(BIN)/mypy . --strict

clean:
	@echo "$(CYAN)Cleaning caches...$(RESET)"
	@$(RM) .mypy_cache
	@find . -type d -name "__pycache__" -exec $(RM) {} + 2>/dev/null; true
	@find . -type f -name "*.pyc" -delete

fclean: clean
	@echo "$(CYAN)Removing virtual environment...$(RESET)"
	@$(RM) $(VENV)
	@$(RM) maze.txt

re: fclean all

.PHONY: all install run debug lint lint-strict clean fclean re
