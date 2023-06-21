.PHONY: server client

server:
	cd server && python3 wsgi.py

client:
	cd client && npm run serve