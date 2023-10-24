FROM python:3.8
RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean

# create work dir
RUN mkdir /home/app
# Define work dir
WORKDIR /home/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install reqs
RUN pip install --upgrade pip

COPY ./requirements.txt .
# устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
# Copy all stuff
COPY . /home/app