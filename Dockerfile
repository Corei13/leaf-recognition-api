FROM tensorflow/tensorflow:latest-jupyter

# Upgrade pip
RUN pip install --upgrade pip

## make a local directory
RUN mkdir /app

# set "app" as the working directory from which CMD, RUN, ADD references
WORKDIR /app

# now copy all the files in this directory to /code
ADD . .

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update -y && apt install -y --no-install-recommends python3-opencv libgl1
RUN pip install -r requirements.txt

# Define our command to be run when launching the container
CMD gunicorn app:app --bind 0.0.0.0:6000 --reload
