FROM python:3.12-slim

WORKDIR /usr/local/exercise_1
# ENV PYTHONPATH=/usr/local/exercise_1

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .


RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home nsk
RUN chown -R nsk:nsk /usr/local/exercise_1
USER nsk