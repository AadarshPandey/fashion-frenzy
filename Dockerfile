# Use Python slim image — Python is pre-installed, much faster than ubuntu base
FROM python:3.13-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install only the minimal system deps needed for Playwright Chromium + Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    # Playwright Chromium runtime dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libxshmfence1 \
    # Pillow dependencies
    libjpeg62-turbo \
    libwebp7 \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files first (for Docker layer caching)
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies
RUN uv venv .venv --python python3
RUN uv sync --frozen || uv sync

# Install Playwright Chromium browser (for crawl4ai scraper)
RUN .venv/bin/playwright install chromium || true

# Copy application source code
COPY main.py ./
COPY modules/ ./modules/
COPY banana_list.txt ./

# Create wardrobe directory structure
RUN mkdir -p user_wardrobe/above_head \
    user_wardrobe/on_face \
    user_wardrobe/on_neck \
    user_wardrobe/upper_body \
    user_wardrobe/lower_body \
    user_wardrobe/feet \
    user_wardrobe/special_overlap

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["uv", "run", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
