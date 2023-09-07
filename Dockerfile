FROM python:3.8

WORKDIR /code

COPY requirements.txt ./
RUN apt-get update
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3",  "utils.py"  ]
