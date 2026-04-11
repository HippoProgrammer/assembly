FROM python:3.13.13-alpine3.23 # begin with the base Alpine python image
WORKDIR /usr/local/ns-assembly # create a directory to store the application 

COPY requirements.txt ./ # copy requirements file
RUN pip install --no-cache-dir -r requirements.txt # install required dependencies

COPY src ./src # copy the source code

ENV PYTHON_UNBUFFERED=1 # make sure logs are unbuffered

CMD ["python", "./src/"] # run source code