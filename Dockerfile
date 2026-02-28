# Use Ubuntu 24.04 LTS as base image
FROM ubuntu:24.04 AS builder

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH"

# Install system dependencies and uv for fast Python package management
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv python3-pip \
    curl wget gnupg nodejs npm \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies
RUN uv venv .venv --python python3 \
    && uv sync --frozen

# Install Playwright browsers for crawl4ai
RUN .venv/bin/playwright install chromium --with-deps || true

# Use Ubuntu 24.04 LTS as base image for runtime
FROM ubuntu:24.04 AS runtime

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:/root/.local/bin:$PATH"

# Install system dependencies (runtime only)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 nodejs npm curl \
    libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1 \
    libasound2t64 libxrandr2 libxdamage1 libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy virtual environment and Playwright browsers from builder
COPY --from=builder /app/.venv ./.venv
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Copy project files
COPY main.py banana_list.txt ./
COPY modules/ ./modules/

# Create wardrobe directory structure
RUN mkdir -p user_wardrobe/{above_head,on_face,on_neck,upper_body,lower_body,feet,special_overlap}

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
