# Base image
FROM python:3.9-slim-buster
MAINTAINER navaneeths1998@gmail.com
WORKDIR /src

COPY requirements.txt ./requirements.txt

RUN pip install -U pip
RUN pip install -r requirements.txt

COPY . .

# Port to expose

EXPOSE 5000
# Run app
CMD ["python", "app.py"]
