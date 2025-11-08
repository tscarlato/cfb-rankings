# Use official Python image that includes Node.js
FROM nikolaik/python-nodejs:python3.11-nodejs20

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install Node.js dependencies
RUN npm install

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Build React app
RUN npm run build

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Start the FastAPI server (use shell form to support $PORT env var)
CMD python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
