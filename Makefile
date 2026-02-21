# ─────────────────────────────────────────────────────────────────────────────
# QA Automation Portfolio — root Makefile
#
# Usage:
#   make              → print available targets
#   make all          → run all three frameworks sequentially
#   make playwright   → playwright-dotnet (C# + TypeScript, headless Chromium)
#   make selenium     → selenium-java (headless Chrome)
#   make cucumber     → cucumber (headless Chrome)
#   make clean        → remove build artefacts from all frameworks
#
# Prerequisites:
#   playwright — .NET 8 SDK (dotnet --version) · Node.js 20+ (node --version)
#   selenium   — Java 17 (java --version) · Maven 3.9+ (mvn --version)
#   cucumber   — Java 17 (java --version) · Maven 3.9+ (mvn --version)
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help all playwright selenium cucumber clean

# Print help when `make` is called with no target
help:
	@echo ""
	@echo "  QA Automation Portfolio — available targets"
	@echo "  ───────────────────────────────────────────"
	@echo "  make all          Run all three frameworks sequentially"
	@echo "  make playwright   Run playwright-dotnet suite (C# + TypeScript)"
	@echo "  make selenium     Run selenium-java suite (headless Chrome)"
	@echo "  make cucumber     Run cucumber suite (headless Chrome)"
	@echo "  make clean        Remove build artefacts from all frameworks"
	@echo ""
	@echo "  Prerequisites:"
	@echo "    playwright — .NET 8 SDK · Node.js 20+"
	@echo "    selenium   — Java 17 · Maven 3.9+"
	@echo "    cucumber   — Java 17 · Maven 3.9+"
	@echo ""

# ── Full portfolio ─────────────────────────────────────────────────────────────

all: playwright selenium cucumber
	@echo ""
	@echo ">>> All three suites complete."
	@echo ""

# ── Individual suites ─────────────────────────────────────────────────────────

playwright:
	@echo ""
	@echo ">>> [playwright-dotnet] Running C# + TypeScript suite..."
	$(MAKE) -C playwright-dotnet all
	@echo ""
	@echo ">>> [playwright-dotnet] Done."
	@echo ""

selenium:
	@echo ""
	@echo ">>> [selenium-java] Running headless Chrome suite..."
	cd selenium-java && mvn clean test -Dheadless=true
	@echo ""
	@echo ">>> [selenium-java] Done."
	@echo ""

cucumber:
	@echo ""
	@echo ">>> [cucumber] Running headless Chrome suite..."
	cd cucumber && mvn clean test -Dheadless=true
	@echo ""
	@echo ">>> [cucumber] Done."
	@echo ""

# ── Clean ─────────────────────────────────────────────────────────────────────

clean:
	@echo ""
	@echo ">>> Cleaning playwright-dotnet artefacts..."
	$(MAKE) -C playwright-dotnet clean
	@echo ""
	@echo ">>> Cleaning selenium-java artefacts..."
	cd selenium-java && mvn clean
	@echo ""
	@echo ">>> Cleaning cucumber artefacts..."
	cd cucumber && mvn clean
	@echo ""
	@echo ">>> Clean complete."
	@echo ""
