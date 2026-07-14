FROM alpine:latest

# 1. 這裡加上你要的 Java 17 和 Gradle
# 使用 --no-cache 可以避免下載的快取佔用 Image 空間，讓 Image 更輕量
RUN apk update && \
    apk add --no-cache openjdk17 gradle

# ---------------------------------------------------
# 以下是假設你原本 aws-env 裡面本來就有的設定（例如安裝 aws-cli）
# 請依據你原本真正的 Dockerfile 內容保留或調整
# ---------------------------------------------------
RUN apk add --no-cache aws-cli

# 設定工作目錄
WORKDIR /workspace

# 預設執行的指令
CMD ["sh"]