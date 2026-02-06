# Use Ubuntu 24.04 LTS as base image
FROM ubuntu:24.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies (Python 3.12 is default in Ubuntu 24.04)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    curl \
    wget \
    gnupg \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
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

# Create virtual environment and install dependencies
RUN uv venv .venv --python python3
RUN uv sync --frozen || uv sync

# Install Playwright browsers for crawl4ai
RUN .venv/bin/playwright install chromium || true
RUN .venv/bin/playwright install-deps chromium || true

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["uv", "run", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
