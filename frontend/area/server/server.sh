#!/bin/bash

# Define the port
PORT=8081

# Install required packages
apt-get update && apt-get install -y python3

# Create necessary directories
mkdir -p /app/build/web

# Wait for the APK to be available (timeout after 60 seconds)
TIMEOUT=60
COUNTER=0
while [ ! -f /app/build/client.apk ] && [ $COUNTER -lt $TIMEOUT ]; do
    echo "Waiting for APK to be available... ($COUNTER seconds)"
    sleep 1
    COUNTER=$((COUNTER + 1))
done

if [ -f /app/build/client.apk ]; then
    # Copy the APK to the web directory for serving
    cp /app/build/client.apk /app/build/web/
    echo "APK copied successfully"
else
    echo "Warning: APK not found after timeout"
fi

# Copy the Flutter web build files
echo "Copying web build files..."
cp -r /app/build/web/* /app/web/build/

# Start the web server from the directory containing the Flutter web build
cd /app/web/build/
echo "Starting web server on port $PORT"
python3 -m http.server $PORT