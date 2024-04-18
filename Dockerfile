FROM python:3.9

RUN mkdir -p /app


COPY requirements.txt /app
COPY src /app

COPY static/datasets /datasets
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=0

CMD [ "python3", "power_consumption.py" ]

