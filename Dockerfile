FROM python:3.11.6

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/

RUN python -m pip install --upgrade pip \
    && pip install -r /app/requirements.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
