# Base image
FROM python:3.6-onbuild

MAINTAINER navaneeths1998@gmail.com

# Port to expose
EXPOSE 5000

# Run app
CMD ["python", "./app.py"]
