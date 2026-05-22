.PHONY: setup start stop logs restart

setup:
	pip install pipenv --quiet
	pipenv install
	pm2 start ecosystem.config.js
	pm2 save
	@echo "✅ Gateway corriendo. Usa 'make logs' para ver los logs."

start:
	pm2 start ecosystem.config.js

stop:
	pm2 stop telegram-gateway

restart:
	pm2 restart telegram-gateway

logs:
	pm2 logs telegram-gateway

status:
	pm2 status