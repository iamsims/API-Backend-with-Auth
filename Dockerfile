# A Dockerfile is a text document that contains all the commands
# a user could call on the command line to assemble an image.

FROM python:3.10

# We create folder named build for our stuff.

RUN useradd -u 1001 -U  -d /server -m  app
WORKDIR /server

# Basic WORKDIR is just /
# Now we just want to our WORKDIR to be /build

COPY ./requirements.txt ./requirements.txt


# FROM [path to files from the folder we run docker run]
# TO [current WORKDIR]
# We copy our files (files from .dockerignore are ignored)
# to the WORKDIR

RUN pip install --no-cache-dir -r requirements.txt

COPY ./alembic.ini ./alembic.ini
COPY ./alembic ./alembic
COPY ./entrypoint.sh ./entrypoint.sh
COPY ./main.py ./main.py
COPY ./app ./app

# OK, now we pip install our requirements

EXPOSE 8080


# Now we just want to our WORKDIR to be /build/app for simplicity
# We could skip this part and then type
# python -m uvicorn main.app:app ... below
USER app
CMD /server/entrypoint.sh 