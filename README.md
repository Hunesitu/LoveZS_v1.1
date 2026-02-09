# LoveZs - Django + Vue 版本

情侣关系管理系统，采用 Django + DRF + PostgreSQL + Vue 3 技术栈。

## 📋 项目概述

**LoveZs** 是一个帮助情侣记录美好时光的Web应用，功能包括：
- 📝 日记管理（支持Markdown、标签、心情）
- 📸 相册管理（照片上传、分类、EXIF信息）
- 📅 重要日提醒（纪念日、生日、事件倒计时）
- 💾 数据备份导出

## 🛠️ 技术栈

### 后端
- **框架**: Django 5.2 + Django REST Framework 3.16
- **数据库**: PostgreSQL 15
- **认证**: JWT (djangorestframework-simplejwt)
- **图片处理**: Pillow
- **API文档**: DRF 自带 browsable API

### 前端
- **框架**: Vue 3.5 + TypeScript
- **构建工具**: Vite 6
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **样式**: Tailwind CSS 3.4
- **图标**: Lucide Vue Next
- **Markdown编辑器**: md-editor-v3

### 开发工具
- **容器化**: Docker & Docker Compose
- **API客户端**: Axios
- **日期处理**: Day.js

## 📁 项目结构

```
LoveZs_New/
├── backend_django/          # Django 后端
│   ├── config/             # 项目配置
│   │   ├── settings/       # 环境配置文件
│   │   │   ├── base.py     # 基础配置
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py         # 根路由
│   │   └── wsgi.py         # WSGI入口
│   ├── lovezs/             # 主应用
│   │   ├── models.py       # 数据模型
│   │   ├── serializers.py  # DRF序列化器
│   │   ├── views.py        # API视图
│   │   ├── urls.py         # 应用路由
│   │   └── admin.py        # Django Admin配置
│   ├── media/uploads/       # 用户上传文件
│   ├── requirements.txt     # Python依赖
│   └── manage.py           # Django管理脚本
│
├── frontend_vue/           # Vue 前端
│   ├── src/
│   │   ├── api/           # API服务层
│   │   ├── components/    # 共享组件
│   │   ├── views/         # 页面组件
│   │   ├── stores/        # Pinia状态管理
│   │   ├── router/        # 路由配置
│   │   ├── composables/   # 组合式函数
│   │   ├── types/         # TypeScript类型
│   │   └── assets/        # 静态资源
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── package.json
│
├── docker-compose.dev.yml  # 开发环境Docker配置
├── .env                   # 环境变量
└── README.md
```

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+（或使用Docker）
- Git

### 1. 克隆项目

```bash
git clone <repository-url>
cd LoveZs_New
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库等信息
```

### 3. 启动数据库（使用Docker）

```bash
docker compose -f docker-compose.dev.yml up -d
```

或使用本地PostgreSQL：

```bash
# 创建数据库
createdb lovezs_dev
```

### 4. 后端设置

```bash
cd backend_django

# 安装依赖
pip install -r requirements.txt

# 运行迁移
python manage.py migrate

# 创建超级用户（可选，用于Django Admin）
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

访问 http://localhost:8000/api/ 查看API
访问 http://localhost:8000/admin/ 管理数据

### 5. 前端设置

```bash
cd frontend_vue

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173

## 📚 核心功能文档

### API端点

#### 日记 (Diaries)
```
GET    /api/diaries/          # 获取日记列表
GET    /api/diaries/{id}/     # 获取单篇日记
POST   /api/diaries/          # 创建日记
PUT    /api/diaries/{id}/     # 更新日记
DELETE /api/diaries/{id}/     # 删除日记
POST   /api/diaries/{id}/photos/  # 关联照片
GET    /api/diaries/meta/categories/  # 获取分类列表
GET    /api/diaries/meta/tags/        # 获取标签列表
```

#### 照片 (Photos)
```
GET    /api/photos/           # 获取照片列表
POST   /api/photos/upload/    # 上传照片
DELETE /api/photos/{id}/      # 删除照片
```

#### 相册 (Albums)
```
GET    /api/albums/           # 获取相册列表
POST   /api/albums/           # 创建相册
PUT    /api/albums/{id}/      # 更新相册
DELETE /api/albums/{id}/      # 删除相册
```

#### 重要日 (Countdowns)
```
GET    /api/countdowns/       # 获取重要日列表
GET    /api/countdowns/{id}/  # 获取单个重要日
POST   /api/countdowns/       # 创建重要日
PUT    /api/countdowns/{id}/  # 更新重要日
DELETE /api/countdowns/{id}/  # 删除重要日
```

#### 备份 (Backup)
```
GET    /api/backup/export/    # 导出数据为ZIP
```

## 🧪 测试

### 后端测试

```bash
cd backend_django

# 运行所有测试
python manage.py test

# 运行特定应用测试
python manage.py test lovezs

# 查看测试覆盖率
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### 前端测试

```bash
cd frontend_vue

# 运行单元测试
npm run test

# 运行E2E测试
npm run test:e2e
```

## 📦 部署

### 生产环境部署

详见 `DEPLOYMENT.md`（待创建）

简要步骤：

1. **构建前端**
```bash
cd frontend_vue
npm run build
```

2. **配置生产环境变量**
```bash
cp .env.example .env.prod
# 编辑生产配置
```

3. **使用Docker Compose部署**
```bash
docker compose -f docker-compose.prod.yml up -d
```

## 🔧 开发指南

### Django 开发流程

1. 修改 Model (`lovezs/models.py`)
2. 创建迁移 `python manage.py makemigrations`
3. 查看迁移SQL `python manage.py sqlmigrate lovezs 0001`
4. 执行迁移 `python manage.py migrate`
5. 创建/修改 Serializer (`lovezs/serializers.py`)
6. 创建/修改 ViewSet (`lovezs/views.py`)
7. 注册路由 (`lovezs/urls.py`)
8. 测试 API

### Vue 开发流程

1. 创建 Composable (`src/composables/`)
2. 创建/修改 Vue 组件 (`src/views/` 或 `src/components/`)
3. 配置路由 (`src/router/index.ts`)
4. 测试功能

## 🐛 常见问题

### Django

**Q: 如何调试SQL查询？**
A: 查看 `LOGGING` 配置中的 `django.db.backends` 日志

**Q: 如何处理N+1查询问题？**
A: 使用 `select_related()` 和 `prefetch_related()`

### Vue 3

**Q: ref 和 reactive 的区别？**
A: ref 用于基本类型（需要 .value），reactive 用于对象

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

- 项目地址: [GitHub](https://github.com/your-repo/lovezs)
- 问题反馈: [Issues](https://github.com/your-repo/lovezs/issues)
