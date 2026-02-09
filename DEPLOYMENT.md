# LoveZs 生产部署指南（阿里云轻量应用服务器）

> 适用场景：阿里云轻量服务器（中国大陆节点）、Docker Compose、PostgreSQL。

## 0. 前置说明（大陆节点）

- 中国大陆节点使用域名对外提供网站，必须完成 ICP 备案。
- 备案完成前，可先使用公网 IP 进行上线验证（HTTP）。
- 备案完成后再切换域名并启用 HTTPS。

---

## 1. 服务器准备

在服务器（推荐 Ubuntu 22.04）执行：

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER
```

重新登录后，验证：

```bash
docker --version
docker compose version
```

阿里云控制台安全组放通：`22`、`80`（备案后再放通 `443`）。

---

## 2. 项目文件准备

将项目上传到服务器（示例目录）：

```bash
sudo mkdir -p /opt/lovezs
sudo chown -R $USER:$USER /opt/lovezs
cd /opt/lovezs
```

目录中应包含：

- `docker-compose.prod.yml`
- `backend_django/Dockerfile`
- `frontend_vue/Dockerfile`
- `deploy/nginx/conf.d/lovezs.http.conf`
- `backend_django/.env.prod.example`
- `.env.prod.example`

创建生产环境变量文件：

```bash
cp .env.prod.example .env.prod
cp backend_django/.env.prod.example backend_django/.env.prod
```

编辑 `.env.prod`：

- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `VITE_API_URL=/api`

编辑 `backend_django/.env.prod`：

- `DJANGO_SECRET_KEY`
- `JWT_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`（先填公网 IP）
- `CORS_ALLOWED_ORIGINS`（先填 `http://公网IP`）
- `DB_*` 与 `.env.prod` 一致
- `ENABLE_HTTPS_SECURITY=False`（IP 阶段）

---

## 3. 首次上线（IP 阶段）

```bash
cd /opt/lovezs
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

查看状态：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f backend
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f nginx
```

验证：

- `http://公网IP/`
- `http://公网IP/api/health/`

---

## 4. 备案与域名切换

1. 在阿里云完成 ICP 备案。
2. 备案通过后，域名 A 记录指向服务器公网 IP。
3. 将 `backend_django/.env.prod` 更新为：
   - `DJANGO_ALLOWED_HOSTS=你的域名,公网IP`
   - `CORS_ALLOWED_ORIGINS=https://你的域名`
   - `ENABLE_HTTPS_SECURITY=True`

---

## 5. 启用 HTTPS

### 5.1 申请证书（示例：certbot）

```bash
sudo apt-get install -y certbot
sudo certbot certonly --standalone -d your-domain.com
```

### 5.2 生成 HTTPS Nginx 配置

在本地仓库执行（PowerShell）：

```powershell
powershell -ExecutionPolicy Bypass -File "deploy/scripts/switch-to-https.ps1" -Domain "your-domain.com"
```

生成文件：`deploy/nginx/conf.d/lovezs.https.conf`

### 5.3 切换 compose 的 nginx 配置挂载

将 `docker-compose.prod.yml` 中 nginx 配置挂载：

- 从：`lovezs.http.conf`
- 改为：`lovezs.https.conf`

并增加端口映射：

- `80:80`
- `443:443`

同时挂载证书目录（只读）：

- `/etc/letsencrypt:/etc/letsencrypt:ro`

重启：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

---

## 6. 常用运维命令

重启：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml restart
```

更新后重建：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

停止：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml down
```

---

## 7. 上线验收清单

- [ ] 首页可访问：`/`
- [ ] 健康检查可访问：`/api/health/`
- [ ] 可新建日记
- [ ] 可上传并查看图片
- [ ] 重启后数据仍在（PostgreSQL 与 media 持久化）
- [ ] 日志可读且无连续错误
- [ ] （域名阶段）HTTPS 证书有效、HTTP 自动跳转 HTTPS

