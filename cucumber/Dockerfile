# Use the same JDK 17 Maven image as CI
FROM maven:3.9.6-eclipse-temurin-17

WORKDIR /app

# Copy project files
COPY . .

# Pre-download dependencies so they are cached in the image layer
RUN mvn dependency:go-offline -q

# Default: headless Chrome against Selenium Grid
# Override at runtime: docker run ... -e TARGET=browserstack -e BS_USER=... -e BS_KEY=...
ENTRYPOINT ["mvn", "clean", "test", "-Dheadless=true"]
