.PHONY: server client

server:
	cd server && python3 main.py

client:
	cd client && npm run serve