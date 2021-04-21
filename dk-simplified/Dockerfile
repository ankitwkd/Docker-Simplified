FROM python:3.8-slim-buster

WORKDIR /app2

COPY requirements.txt requirements.txt
RUN pip install termcolor
RUN pip install tabulate

COPY . .

CMD [ "python3", "dk-helper.py"]