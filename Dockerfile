# begin with the base Alpine python image
FROM python:3.13.13-alpine3.23 
# create a directory to store the application 
WORKDIR /usr/local/ns-assembly 

# copy requirements file
COPY requirements.txt ./ 
# install required dependencies
RUN pip install --no-cache-dir -r requirements.txt 

# copy the source code
COPY src ./src 

# make sure logs are unbuffered
ENV PYTHON_UNBUFFERED=1 

# run source code
CMD ["python", "./src/"] 