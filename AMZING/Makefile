MAIN   = a_maze_ing.py
CONFIG = config.txt
UV     = python3 -m uv

GREEN  = \033[0;32m
CYAN   = \033[0;36m
RESET  = \033[0m

all: install
	@echo "$(GREEN)Ready. Run 'make run' to start.$(RESET)"

install:
	@echo "$(CYAN)Installing dependencies with uv...$(RESET)"
	@$(UV) sync
	@echo "$(GREEN)Done.$(RESET)"

run:
	$(UV) run $(MAIN) $(CONFIG)

debug:
	$(UV) run -m pdb $(MAIN) $(CONFIG)

lint:
	@echo "$(CYAN)flake8...$(RESET)"
	@$(UV) run flake8 . --exclude=.venv,packages
	@echo "$(CYAN)mypy...$(RESET)"
	@$(UV) run mypy . --exclude '(\.venv|packages)' \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
	@echo "$(GREEN)Lint passed.$(RESET)"

lint-strict:
	@$(UV) run flake8 .
	@$(UV) run mypy . --strict

build:
	@echo "$(CYAN)Building maze-generator wheel and sdist...$(RESET)"
	@$(UV) build --package maze-generator --out-dir dist/
	@mv dist/* .
	@rmdir dist/
	@echo "$(GREEN)Done — .whl and .tar.gz are in the current directory.$(RESET)"

clean:
	@echo "$(CYAN)Cleaning caches...$(RESET)"
	@rm -rf .mypy_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
	@find . -type f -name "*.pyc" -delete

fclean: clean
	@echo "$(CYAN)Removing uv environment...$(RESET)"
	@rm -rf .venv
	@rm -rf maze.txt
	@rm -rf maze_generator-*.whl maze_generator-*.tar.gz dist/

re: fclean all

.PHONY: all install run debug lint lint-strict build clean fclean re
