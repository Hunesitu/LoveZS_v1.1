@echo off
REM LoveZs 开发环境启动脚本

echo ========================================
echo LoveZs 开发环境启动
echo ========================================

echo.
echo [1/3] 检查 Docker 容器状态...
docker compose -f docker-compose.dev.yml ps
echo.

echo [2/3] 启动 Django 后端 (端口 8000)...
cd backend_django
start cmd /k "python manage.py runserver 8000"
cd ..
echo Django 后端已启动: http://localhost:8000
echo.

timeout /t 3 /nobreak >nul

echo [3/3] 启动 Vue 前端 (端口 5173)...
cd frontend_vue
start cmd /k "npm run dev"
cd ..
echo Vue 前端已启动: http://localhost:5173
echo.

echo ========================================
echo 开发环境已全部启动！
echo ========================================
echo.
echo 后端 API: http://localhost:8000/api/
echo Django Admin: http://localhost:8000/admin/
echo 前端应用: http://localhost:5173
echo.
echo 按任意键退出...
pause >nul
