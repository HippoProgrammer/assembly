# begin with the base Alpine python image
FROM python:3.13.13-alpine3.23 
# create a directory to store the application 
WORKDIR /usr/local/ns-assembly 

# download a signal handler
RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_x86_64
RUN chmod +x /usr/local/bin/dumb-init

# copy requirements file
COPY requirements.txt ./ 
# install required dependencies
RUN pip install --no-cache-dir -r requirements.txt 

# copy the source code
COPY src ./src 

# make sure logs are unbuffered
ENV PYTHON_UNBUFFERED=1 

# send a KeyboardInterrupt instead of SIGTERM
STOPSIGNAL SIGINT

# run source code
ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ["python", "./src/"] 