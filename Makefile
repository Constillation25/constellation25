.PHONY: install start stop status test push docs clean help

# Constellation25 Makefile

help:
	@echo "Constellation25 — 17-Agent Sovereign AI Platform"
	@echo ""
	@echo "Usage: make <command>"
	@echo ""
	@echo "Commands:"
	@echo "  install    Install Constellation25"
	@echo "  start      Start all 17 agents"
	@echo "  stop       Stop all agents"
	@echo "  status     Show agent status"
	@echo "  test       Run tests"
	@echo "  push       Push to GitHub"
	@echo "  docs       View documentation"
	@echo "  clean      Clean logs and temp files"
	@echo "  recall     Run TotalRecall scan"

install:
	bash install.sh

start:
	bash start_all_agents.sh

stop:
	bash stop_all_agents.sh

status:
	bash status_agents.sh

test:
	bash agents/history_scanner.sh

push:
	bash push_to_github.sh

docs:
	cat docs/QUICKSTART.md

clean:
	find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null || true
	rm -f stalker_global.pid logs/*.pid
	@echo "✓ Cleaned"

recall:
	bash ~/total_recall_fast.sh 2>/dev/null || echo "TotalRecall not found in home dir"

c25:
	bash c25_master_control.sh
