# Use official Python image for AMD64 CPU architecture
FROM --platform=linux/amd64 python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy all necessary Python scripts to the container
COPY main.py .
COPY outline_detector.py .
COPY utils.py .

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the default command to run the program
CMD ["python", "main.py"]
