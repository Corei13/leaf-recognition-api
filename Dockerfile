FROM tensorflow/tensorflow:latest-jupyter

# Upgrade pip
RUN pip install --upgrade pip

# set "app" as the working directory from which CMD, RUN, ADD references

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update -y && apt install -y --no-install-recommends python3-opencv libgl1


WORKDIR /app

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /tf/app

COPY app.py .
COPY tea-firebase.json .
COPY . .
# Define our command to be run when launching the container
# CMD gunicorn app:app --bind 0.0.0.0:6000 --reload --workers=4
CMD ["gunicorn"  , "-b", "0.0.0.0:6000", "app:app" ]