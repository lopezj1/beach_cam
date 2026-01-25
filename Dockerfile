FROM ultralytics/ultralytics:latest-cpu

# Set working directory
WORKDIR /app

# Copy uv from official uv image
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

# Install Node.js (required by yt-dlp for JavaScript runtime) and OpenCV dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    libxcb1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Sync dependencies (excluding dev group which contains ultralytics, already in base image)
RUN uv sync --no-dev

# Set environment to production
ENV PYTHONUNBUFFERED=1

# Run the application
ENTRYPOINT ["uv", "run", "python", "-m", "src.main"]
