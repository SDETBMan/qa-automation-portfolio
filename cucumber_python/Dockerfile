# ============================================================
# cucumber_python — Test Runner Image
#
# Multi-stage build:
#   Stage 1 (deps)   — install Python deps into a venv
#   Stage 2 (runner) — copy venv + source; run behave
#
# Mirrors: cucumber/Dockerfile (Maven pre-cache pattern)
# ============================================================

# ── Stage 1: dependency installation ─────────────────────────────────────────
FROM python:3.11-slim AS deps

WORKDIR /install

COPY requirements.txt .

# Install into an isolated venv so Stage 2 can copy the whole directory cleanly
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip --quiet && \
    /opt/venv/bin/pip install -r requirements.txt --quiet

# ── Stage 2: test runner ──────────────────────────────────────────────────────
FROM python:3.11-slim AS runner

# Install Chromium + ChromeDriver for headless browser tests
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Point Selenium to the system Chromium binary
ENV CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage"
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy pre-built venv from Stage 1
COPY --from=deps /opt/venv /opt/venv

# Copy framework source
COPY . .

# Create reports output directory
RUN mkdir -p reports/allure-results reports/junit

# Default: run all scenarios headless against Selenium Grid
# Override with: docker run ... behave --tags @smoke
ENTRYPOINT ["behave"]
CMD ["--no-capture"]
