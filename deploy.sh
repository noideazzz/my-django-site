#!/bin/bash
set -e

echo "========================================"
echo "  Django 项目一键部署脚本"
echo "  适用：腾讯云轻量应用服务器 (Ubuntu)"
echo "========================================"
echo ""

PROJECT_DIR="/opt/django_app"
REPO_URL="https://github.com/你的用户名/你的仓库.git"

# 1. 安装 Docker（如果还没装）
if ! command -v docker &> /dev/null; then
    echo ">>> 正在安装 Docker..."
    curl -fsSL https://get.docker.com | bash
    systemctl start docker
    systemctl enable docker
    echo ">>> Docker 安装完成"
else
    echo ">>> Docker 已安装"
fi

# 2. 安装 Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo ">>> 正在安装 Docker Compose..."
    apt-get update -qq && apt-get install -y -qq docker-compose-plugin
    echo ">>> Docker Compose 安装完成"
else
    echo ">>> Docker Compose 已安装"
fi

# 3. 克隆/更新项目
if [ -d "$PROJECT_DIR" ]; then
    echo ">>> 项目目录已存在，正在更新..."
    cd "$PROJECT_DIR"
    git pull
else
    echo ">>> 正在克隆项目..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# 4. 复制本地的 db.sqlite3（首次部署时需要把本地数据库上传）
# 如果你需要手动上传数据库文件，请取消下面的注释并修改路径
# cp /path/to/your/db.sqlite3 "$PROJECT_DIR/db.sqlite3"

# 5. 构建并启动
echo ">>> 正在构建 Docker 镜像..."
docker compose build --no-cache

echo ">>> 正在启动服务..."
docker compose up -d

echo ""
echo "========================================"
echo "  部署完成！"
echo "  访问地址: http://你的服务器IP"
echo "========================================"
echo ""
echo "查看日志: docker compose logs -f"
echo "重启服务: docker compose restart"
echo "停止服务: docker compose down"
