#!/bin/bash

set -e

DOMAIN="${1:-lovezs.me}"

TEMPLATE_PATH="deploy/nginx/conf.d/lovezs.https.template.conf"
TARGET_PATH="deploy/nginx/conf.d/lovezs.https.conf"

if [ ! -f "$TEMPLATE_PATH" ]; then
    echo "错误: 模板不存在 $TEMPLATE_PATH"
    exit 1
fi

sed "s/{{DOMAIN}}/$DOMAIN/g" "$TEMPLATE_PATH" > "$TARGET_PATH"

echo "已生成 HTTPS Nginx 配置: $TARGET_PATH"
echo "下一步: 确保证书文件已上传到 deploy/nginx/ssl/ 目录"
