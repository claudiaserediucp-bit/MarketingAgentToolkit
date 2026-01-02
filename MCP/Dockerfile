FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install FastMCP for stdio transport
RUN pip install --no-cache-dir fastmcp

# Copy MCP server code
COPY . .

# Set Python to unbuffered mode for real-time logs
ENV PYTHONUNBUFFERED=1

# Default command: run MCP server via stdio
CMD ["python", "server.py"]

