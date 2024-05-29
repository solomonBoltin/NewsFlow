# Base image with Python
FROM python:3.12-bookworm

# Working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
RUN apt-get update && apt-get install -y

RUN pip install playwright==1.44.0 && \
    playwright install --with-deps && \
    playwright install webkit

# RUN python3
COPY requirements.txt requirements.txt

# RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

# Copy your project code
COPY . /app

# set the google application credentials
# ENV GOOGLE_APPLICATION_CREDENTIALS="/app/credentials.json"

# Command to run your application (replace with your actual command)
CMD ["python", "run.py"]
