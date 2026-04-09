FROM python:3.13.13-alpine3.23
WORKDIR /usr/local/ns-assembly

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

CMD ["python", "./src/"]