# SENKU // QuantumFlow - Universal Docker Container
FROM python:3.12-slim

WORKDIR /app

# Copy all project files
COPY . /app

# Expose standard port
ENV PORT=8080
ENV HOST=0.0.0.0
EXPOSE 8080

# Launch Senku Quantum Labs Web Visualizer
CMD ["python", "senku.py", "web"]
