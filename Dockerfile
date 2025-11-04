FROM python:3.11-slim

# Expose port
EXPOSE 5000

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Set environment variables for Flask factory
ENV FLASK_APP=app:create_app
ENV FLASK_ENV=development

# Run Flask app
CMD ["flask", "run", "--host", "0.0.0.0"]
