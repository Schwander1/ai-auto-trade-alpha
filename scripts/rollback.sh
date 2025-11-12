#!/bin/bash
set -e

# Instant rollback script (<30 seconds)
# Rolls back to previous working version

echo "🔄 Rolling back to previous version..."
echo "======================================"

# Check which service to rollback
SERVICE=${1:-"all"}

if [ "$SERVICE" = "argo" ] || [ "$SERVICE" = "all" ]; then
  echo ""
  echo "🔄 Rolling back Argo..."
  
  ARGO_SERVER="178.156.194.174"
  ARGO_USER="root"
  ARGO_PATH="/root/argo-production"
  BACKUP_PATH="/root/argo-production-backup"
  
  ssh ${ARGO_USER}@${ARGO_SERVER} "
    if [ -d ${BACKUP_PATH} ]; then
      echo 'Stopping current service...'
      pkill -f 'uvicorn main:app' || true
      sleep 2
      
      echo 'Restoring backup...'
      rm -rf ${ARGO_PATH}
      mv ${BACKUP_PATH} ${ARGO_PATH}
      
      echo 'Starting previous version...'
      cd ${ARGO_PATH}
      source venv/bin/activate
      nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/argo.log 2>&1 &
      sleep 5
      
      echo '✅ Argo rolled back'
    else
      echo '❌ No backup found for Argo'
    fi
  "
fi

if [ "$SERVICE" = "alpine" ] || [ "$SERVICE" = "all" ]; then
  echo ""
  echo "🔄 Rolling back Alpine..."
  
  ALPINE_SERVER="91.98.153.49"
  ALPINE_USER="root"
  
  # Determine current and previous colors
  CURRENT_COLOR=$(ssh ${ALPINE_USER}@${ALPINE_SERVER} "
    if docker ps | grep -q '8001:8000'; then
      echo 'blue'
    elif docker ps | grep -q '8002:8000'; then
      echo 'green'
    else
      echo 'unknown'
    fi
  " 2>/dev/null || echo "unknown")
  
  if [ "$CURRENT_COLOR" = "blue" ]; then
    PREVIOUS_COLOR="green"
    PREVIOUS_PORT="8002"
  elif [ "$CURRENT_COLOR" = "green" ]; then
    PREVIOUS_COLOR="blue"
    PREVIOUS_PORT="8001"
  else
    echo "⚠️  Could not determine current deployment"
    exit 1
  fi
  
  echo "Current: $CURRENT_COLOR, Rolling back to: $PREVIOUS_COLOR"
  
  ssh ${ALPINE_USER}@${ALPINE_SERVER} "
    # Switch nginx to previous color
    if [ -f /etc/nginx/sites-enabled/alpine ]; then
      if [ '$PREVIOUS_COLOR' = 'green' ]; then
        sed -i 's/8001/8002/g' /etc/nginx/sites-enabled/alpine
        sed -i 's/3000/3002/g' /etc/nginx/sites-enabled/alpine
      else
        sed -i 's/8002/8001/g' /etc/nginx/sites-enabled/alpine
        sed -i 's/3002/3000/g' /etc/nginx/sites-enabled/alpine
      fi
      nginx -t && systemctl reload nginx
      echo '✅ Traffic switched to $PREVIOUS_COLOR'
    fi
    
    # Stop current deployment
    if [ '$CURRENT_COLOR' = 'blue' ]; then
      cd /root/alpine-production-blue && docker compose down
    else
      cd /root/alpine-production-green && docker compose down
    fi
    
    echo '✅ Alpine rolled back to $PREVIOUS_COLOR'
  "
fi

echo ""
echo "🎉 Rollback complete!"

