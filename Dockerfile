FROM --platform=linux/arm64/v8 arm64v8/python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/ducky4life/Triggerwarden"

WORKDIR /

COPY trigger.py keep_alive.py requirements.txt .env /

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["python", "trigger.py"]
