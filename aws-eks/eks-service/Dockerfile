# ==========================================
# 第一階段：Build 階段 (使用包含 Maven 的環境)
# ==========================================
FROM maven:3.9.6-eclipse-temurin-17-alpine AS builder

# 設定工作目錄
WORKDIR /app

# 先複製 pom.xml 並下載依賴 (利用 Docker 快取機制，如果 pom 沒變，這步就不會重跑，大幅加速打包)
COPY pom.xml .
RUN mvn dependency:go-offline -B

# 複製所有原始碼 (包含 src/, src/main/resources/ 底下的 schema.sql 和 data.sql 等)
COPY src ./src

# 執行編譯與打包，跳過測試以加速 build 過程
RUN mvn clean package -DskipTests

# ==========================================
# 第二階段：Run 階段 (只留下執行所需的輕量環境)
# ==========================================
FROM eclipse-temurin:17-jdk-alpine

WORKDIR /app

# 從第一階段 (builder) 把包好的 JAR 檔複製過來，並重命名為 app.jar
COPY --from=builder /app/target/*.jar app.jar

# 建立一個非 root 的安全使用者來執行程式 (CKAD 安全性最佳實踐！)
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

# 宣告 Port (Spring Boot 預設 8080)
EXPOSE 8080

# 啟動指令
ENTRYPOINT ["java", "-jar", "app.jar"]