# Operations Guide
**Generated:** Sun Nov  9 11:46:48 AM EST 2025

## 🚀 Deployment
```bash
cd ~/argo-production
docker compose down
docker compose up -d --build
docker compose ps
```

## 🔧 Maintenance
```bash
# View logs
docker compose logs -f argo-api

# Restart services
docker compose restart

# Check health
curl http://localhost:8000/health
```

## 📞 Support
- Technical contact: Available 24/7
- System monitoring: Automated via Prometheus
