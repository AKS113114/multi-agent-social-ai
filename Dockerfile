FROM python:3.11-slim

# Install system dependencies and curl
RUN apt-get update && apt-get install -y curl zstd procps && rm -rf /var/lib/apt/lists/*

# Install Ollama CLI & Engine
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Set default environment variables
ENV PORT=10000
ENV OLLAMA_BASE_URL=http://127.0.0.1:11434
ENV OLLAMA_MODEL=gemma3:4b

# Create startup script to launch Ollama and FastAPI together
RUN echo '#!/bin/sh\n\
ollama serve &\n\
sleep 5\n\
ollama pull gemma3:4b || true\n\
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 10000

CMD ["/app/start.sh"]
