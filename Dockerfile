# Use the official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .




# ENV DBName=whatsapp
# ENV DBUser=kenobi
# ENV DBPassword=kenobi
# ENV DBHost= 10.109.128.18


# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the app will run on
EXPOSE 8080

# Command to run the application
CMD ["python", "-m", "src.main"]
