# Use Apify's Python base image with Playwright
FROM apify/actor-python-playwright:3.11

# Copy all files
COPY . ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers with system dependencies
RUN playwright install --with-deps chromium

# Run the actor
CMD ["python", "main.py"]
