FROM python:3.10

# We create home folder for non-root user.
RUN useradd -u 1001 -U  -d /server -m  app
WORKDIR /server
ENV PATH="$PATH:/server/.local/bin"
USER app

COPY ./requirements.txt ./requirements.txt

# install all the packages with cache disabled. (this layer will be cached unless requirements.txt is changed.)
RUN pip install --no-cache-dir -r requirements.txt

# copy schema and generate schema
COPY ./schema.prisma ./schema.prisma
RUN prisma generate


# Copy the code
COPY ./ ./



EXPOSE 8080
CMD /server/entrypoint.sh 