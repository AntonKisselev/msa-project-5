FROM openjdk:24-slim
# 8080
WORKDIR /tmp
COPY build/libs/*.jar app.jar
COPY src/main/resources/* *
EXPOSE 8080
ENTRYPOINT ["java","-jar","/tmp/app.jar"]