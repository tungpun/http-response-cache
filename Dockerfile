FROM python:3.9-alpine
WORKDIR /code
COPY /requirements.txt /code/
RUN pip3 install -r requirements.txt
COPY . /code/
# ENTRYPOINT ["flask", "run", "-p", "5000", "--host=0.0.0.0"]
