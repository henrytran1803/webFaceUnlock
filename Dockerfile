FROM python:3.11.6

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update \
    && apt-get install -y libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# copy project
COPY . /app/

# install Python dependencies
RUN python -m pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# port to expose
EXPOSE 8000

# command to run on container start
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
