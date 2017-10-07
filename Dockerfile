FROM mbodenhamer/python-dev:latest
COPY dev/ /usr/local/bin/
    
# Install docker client
RUN curl -sSL -O https://download.docker.com/linux/static/stable/x86_64/docker-17.06.2-ce.tgz \
    && tar zxf docker-17.06.2-ce.tgz \
    && mv docker/* /usr/bin \
    && rm -rf docker*
