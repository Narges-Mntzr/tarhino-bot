FROM python:3.11

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y libgl1-mesa-glx libegl1-mesa libx11-dev

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./ /app

# Command to run the application
CMD ["python", "main.py"]
