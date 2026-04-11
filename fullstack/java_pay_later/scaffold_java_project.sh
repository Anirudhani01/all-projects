#!/usr/bin/env bash

set -euo pipefail

# Simple scaffolder for LazyPay Spring Boot + MongoDB (based on designjava.md)
# Usage: ./scaffold_java_project.sh [project_dir]
# Example: ./scaffold_java_project.sh lazypay

PROJECT_DIR=${1:-lazypay}
GROUP_ID=com.lazypay
ARTIFACT_ID=lazypay
VERSION=0.0.1-SNAPSHOT
JAVA_VERSION=17
SPRING_BOOT_BOM_VERSION=3.3.2

echo "Scaffolding project in: ${PROJECT_DIR}"
mkdir -p "${PROJECT_DIR}"

cd "${PROJECT_DIR}"

echo "Creating directories..."
mkdir -p \
  src/main/java/com/lazypay \
  src/main/java/com/lazypay/api \
  src/main/java/com/lazypay/domain/users \
  src/main/java/com/lazypay/domain/merchants \
  src/main/java/com/lazypay/domain/transactions \
  src/main/java/com/lazypay/dto \
  src/main/java/com/lazypay/repository \
  src/main/java/com/lazypay/service \
  src/main/java/com/lazypay/config \
  src/main/java/com/lazypay/exception \
  src/main/resources

echo "Writing pom.xml..."
cat > pom.xml <<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>com.lazypay</groupId>
  <artifactId>lazypay</artifactId>
  <version>0.0.1-SNAPSHOT</version>
  <name>lazypay</name>
  <description>LazyPay - Spring Boot + MongoDB</description>
  <packaging>jar</packaging>

  <properties>
    <java.version>17</java.version>
  </properties>

  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-dependencies</artifactId>
        <version>3.3.2</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>

  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-data-mongodb</artifactId>
    </dependency>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
    <dependency>
      <groupId>org.springdoc</groupId>
      <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
      <version>2.5.0</version>
    </dependency>
    <dependency>
      <groupId>io.micrometer</groupId>
      <artifactId>micrometer-registry-prometheus</artifactId>
    </dependency>
    <!-- Optional: Mongock for migrations/index creation -->
    <dependency>
      <groupId>io.mongock</groupId>
      <artifactId>mongock-springboot</artifactId>
      <version>5.4.2</version>
    </dependency>

    <!-- Test -->
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-test</artifactId>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.testcontainers</groupId>
      <artifactId>mongodb</artifactId>
      <version>1.20.1</version>
      <scope>test</scope>
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-maven-plugin</artifactId>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <configuration>
          <release>17</release>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>
XML

echo "Writing application.yml..."
cat > src/main/resources/application.yml <<'YAML'
spring:
  data:
    mongodb:
      uri: ${MONGODB_URI:mongodb://localhost:27017}
      database: ${MONGODB_DB:lazypay}
  mvc:
    problemdetails:
      enabled: true
server:
  port: ${PORT:8080}
  servlet:
    context-path: /api/v1
management:
  endpoints:
    web:
      exposure:
        include: prometheus,health,info
  metrics:
    tags:
      application: lazypay
YAML

echo "Writing entrypoint class..."
cat > src/main/java/com/lazypay/LazyPayApplication.java <<'JAVA'
package com.lazypay;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class LazyPayApplication {
    public static void main(String[] args) {
        SpringApplication.run(LazyPayApplication.class, args);
    }
}
JAVA

echo "Writing Mongo transaction config..."
cat > src/main/java/com/lazypay/config/MongoTxConfig.java <<'JAVA'
package com.lazypay.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.mongodb.MongoDatabaseFactory;
import org.springframework.data.mongodb.MongoTransactionManager;

@Configuration
public class MongoTxConfig {
    @Bean
    public MongoTransactionManager transactionManager(MongoDatabaseFactory dbFactory) {
        return new MongoTransactionManager(dbFactory);
    }
}
JAVA

echo "Writing .gitignore..."
cat > .gitignore <<'GIT'
# Maven
target/
!.mvn/wrapper/maven-wrapper.jar

# IDEs
.idea/
*.iml
.classpath
.project
.settings/

# OS
.DS_Store
GIT

echo "Writing README.md..."
cat > README.md <<'MD'
# LazyPay (Spring Boot + MongoDB)

This project was scaffolded from `designjava.md`.

## Prerequisites
- Java 17+
- Maven 3.9+
- MongoDB (replica set for transactions)

## Run locally
1. Start MongoDB (replica set recommended)
2. Build and run:
   ```bash
   mvn spring-boot:run
   ```
3. Open Swagger UI:
   - http://localhost:8080/swagger-ui.html

## Notes
- Project layout follows the design document (controllers, services, domain, DTOs, repositories, config, exception).
- `MongoTransactionManager` is provided. Ensure your MongoDB is a replica set for transactions to work.
MD

echo "Done. Next steps:"
echo "  cd ${PROJECT_DIR} && mvn spring-boot:run"


