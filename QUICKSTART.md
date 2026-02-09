# 🚀 LoveZs 快速启动指南

## ✅ Phase 0 完成状态

恭喜！开发环境已经搭建完成。以下是已完成的工作：

### 1. 项目结构 ✓

```
LoveZs_New/
├── backend_django/          ✓ Django 项目已创建
│   ├── config/             ✓ 配置已拆分 (base/development/production)
│   ├── lovezs/             ✓ 应用已创建
│   ├── requirements.txt    ✓ 依赖已配置
│   └── manage.py          ✓ Django 管理脚本
│
├── frontend_vue/           ✓ Vue 3 + TypeScript 项目已创建
│   ├── src/               ✓ 目录结构已创建
│   ├── tailwind.config.js ✓ Tailwind CSS 已配置
│   └── package.json       ✓ 依赖已安装
│
├── docker-compose.dev.yml  ✓ Docker 配置已创建
├── .env                   ✓ 环境变量已配置
└── README.md              ✓ 项目文档已创建
```

### 2. 已安装的依赖

**后端 (Django)**:
- Django 5.2.11
- Django REST Framework 3.16.1
- django-cors-headers
- djangorestframework-simplejwt
- django-filter
- psycopg2-binary (PostgreSQL 驱动)
- Pillow (图片处理)

**前端 (Vue 3)**:
- Vue 3.5
- TypeScript
- Vue Router 4
- Pinia
- Axios
- Day.js
- Lucide Vue Next (图标)
- md-editor-v3 (Markdown 编辑器)
- Tailwind CSS 3.4

## 🎯 下一步：开始开发

### 选项 A: 使用 SQLite 快速开始（推荐用于初次运行）

如果你还没有安装 PostgreSQL，可以先使用 SQLite 快速测试：

```bash
# 修改配置
cd F:/LoveZs_New/backend_django/config/settings
# 编辑 base.py，将数据库部分改为：
"""
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
"""

# 运行迁移
cd F:/LoveZs_New/backend_django
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动服务器
python manage.py runserver
```

### 选项 B: 使用 PostgreSQL（完整功能）

1. **安装 Docker Desktop**（如果还没有）
   - 下载地址: https://www.docker.com/products/docker-desktop/

2. **启动数据库容器**
```bash
cd F:/LoveZs_New
docker compose -f docker-compose.dev.yml up -d
```

3. **运行 Django 迁移**
```bash
cd backend_django
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

4. **启动 Vue 前端**
```bash
cd frontend_vue
npm run dev
```

## 📝 第一次运行清单

- [ ] 数据库容器已启动 (或使用 SQLite)
- [ ] Django 迁移已完成 (`python manage.py migrate`)
- [ ] 超级用户已创建 (`python manage.py createsuperuser`)
- [ ] Django 后端已运行 (http://localhost:8000)
- [ ] Vue 前端已运行 (http://localhost:5173)

## 🧪 验证安装

### 后端验证

1. **访问 Django Admin**
   - 打开浏览器: http://localhost:8000/admin/
   - 使用创建的超级用户登录
   - 应该能看到管理界面

2. **访问 API**
   - 打开浏览器: http://localhost:8000/api/
   - 应该能看到 DRF 的 browsable API 界面

### 前端验证

1. **访问 Vue 应用**
   - 打开浏览器: http://localhost:5173
   - 应该能看到 Vite 的默认页面

## 📚 接下来的步骤

### Phase 1: 后端基础架构 (1周)

- [ ] 定义数据模型（Diary, Photo, Countdown, Album）
- [ ] 创建 Serializers
- [ ] 实现 ViewSets
- [ ] 配置 URL 路由
- [ ] 测试 API 端点

### Phase 2: 前端基础架构 (3-4天)

- [ ] 配置 Vue Router
- [ ] 配置 Pinia 状态管理
- [ ] 创建 API 服务层
- [ ] 创建 Layout 组件
- [ ] 配置 Tailwind CSS

### Phase 3: 数据模型迁移 (3-4天)

- [ ] 从 Express MongoDB Schema 转换到 Django Models
- [ ] 运行迁移
- [ ] 在 Django Admin 中测试数据模型

## 🔧 常用命令

### Django 后端

```bash
# 进入后端目录
cd F:/LoveZs_New/backend_django

# 运行开发服务器
python manage.py runserver

# 创建迁移
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 打开 Django Shell
python manage.py shell

# 检查项目
python manage.py check

# 收集静态文件
python manage.py collectstatic
```

### Vue 前端

```bash
# 进入前端目录
cd F:/LoveZs_New/frontend_vue

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### Docker

```bash
# 启动容器
docker compose -f docker-compose.dev.yml up -d

# 查看容器状态
docker compose -f docker-compose.dev.yml ps

# 查看日志
docker compose -f docker-compose.dev.yml logs -f

# 停止容器
docker compose -f docker-compose.dev.yml down

# 重启容器
docker compose -f docker-compose.dev.yml restart
```

## 🐛 遇到问题？

### Django 无法连接数据库

**错误**: `could not connect to server: Connection refused`

**解决方案**:
1. 检查 Docker 容器是否运行: `docker compose ps`
2. 检查 .env 文件中的数据库配置
3. 或者切换到 SQLite（见选项 A）

### npm 安装依赖失败

**错误**: `EACCES` 或网络错误

**解决方案**:
```bash
# 清除缓存
npm cache clean --force

# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 重新安装
npm install
```

### Vue 无法访问后端 API

**错误**: CORS 错误或连接被拒绝

**解决方案**:
1. 检查后端是否运行在 http://localhost:8000
2. 检查 .env 文件中的 `VITE_API_URL` 配置
3. 查看浏览器控制台的具体错误信息

## 📞 获取帮助

- 查看完整文档: `README.md`
- 查看迁移计划: `C:\Users\Hunesitu\.claude\plans\smooth-percolating-otter.md`
- Django 官方文档: https://docs.djangoproject.com/zh-hans/
- Vue 3 官方文档: https://cn.vuejs.org/

---

**准备好了吗？让我们开始 Phase 1 吧！** 🎉
