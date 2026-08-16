# C25 SOVEREIGN ECOSYSTEM MAKEFILE
.PHONY: all build deploy
all: build
build:
	@echo "[*] Building sovereign mesh..."
deploy:
	@echo "[*] Deploying to master_unified_build..."
	@pm2 start ecosystem.config.js || true
