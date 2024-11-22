# Use the Python 3.12 slim image as the base
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy application files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app runs on
EXPOSE 5000
EXPOSE 8080

# Command to run the application
CMD ["python", "app.py"]