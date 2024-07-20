.DEFAULT_GOAL := help

help: ## Displays makefile commands
	@grep -E '^[a-zA-Z0-9_-]+:.?## .$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

install:  ## Install pre-commit and docker
	@echo "----Installing Commit Hooks----"
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "----Done----"

build:  ## Build docker image
	@echo "----Building Containers----"
	docker-compose build
	@echo "----Done----"

up:  ## Run local server
	@echo "----Starting Containers----"
	docker-compose up
	@echo "----Containers Running----"

down:  ## Stop local server container
	@echo "----Stopping Containers----"
	docker-compose down
	@echo "----Containers Stopped----"

scrap:  ## Runs main file
	@echo "----Running main.py----"
	docker-compose exec house-scraper python main.py
	@echo "----Script Execution Complete----"
