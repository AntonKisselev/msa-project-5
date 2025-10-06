FROM gradle:8.10.0-jdk17 AS builder

WORKDIR /app
COPY . .

# Собираем проект без тестов (ускоряет процесс)
RUN gradle clean bootJar -x test

FROM eclipse-temurin:17-jre

WORKDIR /app

# Копируем собранный jar-файл
COPY --from=builder /app/build/libs/*.jar app.jar

# Указываем порт (для REST endpoint)
EXPOSE 8080

# Переменные окружения (можно переопределить при запуске)
ENV JAVA_OPTS="-Xms256m -Xmx512m"
ENV SPRING_PROFILES_ACTIVE=default

# Запуск Spring Boot приложения
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
