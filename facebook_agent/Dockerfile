FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends tzdata openssh-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY facebook_agent/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY facebook_agent /app/facebook_agent

# Default log location
VOLUME ["/data/logs"]

CMD ["python", "-m", "facebook_agent.agent.main"]

