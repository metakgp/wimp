# Base image
FROM python:3.9-slim-buster
LABEL AUTHOR navaneeths1998@gmail.com
WORKDIR /src

RUN pip install --upgrade pip
RUN pip install gunicorn

COPY requirements.txt ./requirements.txt

RUN pip install -U pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
