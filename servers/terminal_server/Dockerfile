# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements (if any) and install dependencies
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Set the default command to run your app (replace app.py with your entry point)
CMD ["python", "terminal_server.py"]