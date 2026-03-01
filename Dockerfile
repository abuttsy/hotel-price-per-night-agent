# Use Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    librandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirement files and script
COPY requirements.txt .
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and chromium browser
RUN playwright install chromium

# Set environment variables (Placeholders - should be passed at runtime)
ENV NOTION_TOKEN=""
ENV DATABASE_ID=""
ENV EMAIL_SENDER=""
ENV EMAIL_PASSWORD=""
ENV EMAIL_RECEIVER="ultimatefamilyhotels@gmail.com"
ENV MCP_TRANSPORT="stdio"

# Command to run the MCP server
CMD ["python", "mcp_server.py"]
