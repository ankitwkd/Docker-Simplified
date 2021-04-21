FROM python:3.8-slim-buster
WORKDIR /py_todo_app
COPY . .
RUN pip3 install flask
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=3000"]