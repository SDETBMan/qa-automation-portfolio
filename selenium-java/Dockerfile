# 1. Use an official Maven image with JDK 17 (Same as your CI)
FROM maven:3.9.6-eclipse-temurin-17

# 2. Set working directory
WORKDIR /app

# 3. Copy project files (Source code, POM, XMLs)
COPY . .

# 4. (Optional) Go Offline - Downloads dependencies so they are cached in the image
# This makes starting the container much faster on subsequent runs
RUN mvn dependency:go-offline

# 5. Define the Entry Point
# We use "ENTRYPOINT" so we can pass extra arguments if needed.
# notice we removed "-Dheadless=true" because BrowserStack handles the display.
ENTRYPOINT ["mvn", "clean", "test", "-DsuiteXmlFile=testng.xml", "-DskipAppUpload=true"]