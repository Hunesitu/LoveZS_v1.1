# Repository Guidelines

## 项目结构与模块组织
仓库根目录包含 `backend_django`（Django/DRF 后端）、`frontend_vue`（Vue 3 + Vite 前端）、`docker-compose.dev.yml`（本地数据库与服务编排）以及 `.env`/`.env.example`。后端核心代码在 `backend_django/lovezs`，配置在 `backend_django/config/settings`，上传资源默认落在 `backend_django/media/uploads`。前端源码集中于 `frontend_vue/src`，其中 `api` 负责接口封装，`views` 为页面级组件，`components` 为通用组件，`stores` 为 Pinia 状态管理，`router` 为路由配置。

## 构建、测试与开发命令
本地启动数据库与依赖服务：`docker compose -f docker-compose.dev.yml up -d`。后端初始化与运行：`pip install -r requirements.txt`、`python manage.py migrate`、`python manage.py runserver`（工作目录：`backend_django`）。前端开发与构建：`npm install`、`npm run dev`、`npm run build`、`npm run preview`（工作目录：`frontend_vue`）。这些命令以 README 为准，确保路径正确且环境变量已配置。

## 编码风格与命名约定
后端遵循 PEP 8，4 空格缩进，函数/变量使用 `snake_case`，类与 Django Model 使用 `PascalCase`。前端 TypeScript/Vue 建议 2 空格缩进，组件名使用 `PascalCase`，组合式函数使用 `useXxx` 命名（例如 `useDiary`）。仓库未发现统一的格式化或 lint 配置，修改时以现有文件风格为基准，避免引入新的风格分歧。

## 测试指南
后端使用 Django 测试体系：`python manage.py test`，覆盖率可用 `coverage run --source='.' manage.py test`。测试文件建议放在 `backend_django/lovezs/tests` 或 `tests.py`，命名为 `test_*.py`。前端 `package.json` 当前未提供 `test` 脚本，如需添加单元或 E2E 测试，请同步补充脚本与工具说明。

## 提交与 Pull Request 规范
当前目录未检测到 `.git`，无法从历史中总结提交规范。建议采用 Conventional Commits（如 `feat: ...`、`fix: ...`、`docs: ...`），并在 PR 中提供：变更摘要、关联 Issue、验证步骤；涉及 UI 变更时附截图或录屏。

## 安全与配置提示
本地开发请从 `.env.example` 复制为 `.env`，生产环境使用单独的 `.env.prod`（如有）。不要提交密钥与数据库凭据；上传文件位于 `backend_django/media/uploads`，如需清理请先确认数据备份策略。
