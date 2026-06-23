#!/usr/bin/env bash
set -e

SERVER=root@46.62.141.87
SSH_KEY=~/.ssh/hetzner_bluevision
NGINX_CONF=/root/intelligent-blue-economy/nginx/nginx.conf
NGINX_CONTAINER=intelligent-blue-economy_nginx_1

echo "==> Building frontend..."
cd frontend && npm run build && cd ..

echo "==> Committing and pushing..."
git add -f frontend/dist/
git add -u
git diff --cached --quiet && echo "Nothing to commit" || git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M')"
git push

echo "==> Deploying to server..."
ssh -i $SSH_KEY $SERVER bash << 'REMOTE'
  set -e
  cd /root/worldcup2026
  git pull
  docker rm -f worldcup 2>/dev/null || true
  docker compose up -d --build

  # Ensure worldcup nginx block is present — add it if missing
  if ! grep -q "worldcup.bluevision-ai.org" /root/intelligent-blue-economy/nginx/nginx.conf; then
    echo "Adding worldcup nginx block..."
    python3 -c "
c = open('/root/intelligent-blue-economy/nginx/nginx.conf').read()
block = '''
    upstream worldcup {
        server worldcup:8000;
    }
'''
server = '''
    server {
        listen 80;
        server_name worldcup.bluevision-ai.org;
        location / {
            proxy_pass http://worldcup;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }
    }
'''
c = c.replace('    upstream api {', block + '    upstream api {')
c = c.rstrip().rstrip('}') + server + '}\n'
open('/root/intelligent-blue-economy/nginx/nginx.conf','w').write(c)
"
    docker restart "$NGINX_CONTAINER"
  else
    docker exec "$NGINX_CONTAINER" nginx -s reload
  fi
REMOTE

echo "==> Done. https://worldcup.bluevision-ai.org"
