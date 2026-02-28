# ---------- BUILD STAGE ----------
FROM python:3.13-slim AS builder

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH" \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install uv and node
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget gnupg nodejs npm \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app

# Cache dependency layers before copying source
COPY pyproject.toml uv.lock ./

# Create venv and install only production deps
RUN uv venv .venv --python python3.13 \
    && uv sync --frozen --no-dev

# Install Chromium browser binary for Playwright
RUN .venv/bin/playwright install chromium --with-deps


# ---------- RUNTIME STAGE ----------
FROM python:3.13-slim AS runtime

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

# Chromium runtime system libraries + node
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs npm curl \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libasound2t64 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxshmfence1 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Bring over venv and browser binary from builder — nothing else
COPY --from=builder /app/.venv ./.venv
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# App source
COPY main.py banana_list.txt ./
COPY modules/ ./modules/

# Persistent wardrobe storage dirs
RUN mkdir -p user_wardrobe/{above_head,on_face,on_neck,upper_body,lower_body,feet,special_overlap}

# Drop root privileges for security
RUN groupadd --gid 1001 appuser \
    && useradd --uid 1001 --gid appuser --shell /bin/bash --create-home appuser \
    && chown -R appuser:appuser /app /root/.cache/ms-playwright
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
