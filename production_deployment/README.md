# Production Deployment Package

## 🚀 Quick Start - Automated Deployment (Recommended)

### Step 1: Copy Files to Production Server

```bash
# From your local machine
# Copy deployment package
scp -r production_deployment/* root@178.156.194.174:/root/

# Copy infrastructure files (for updated service files with dependency management)
scp -r infrastructure/systemd/* root@178.156.194.174:/root/argo-alpine-workspace/infrastructure/systemd/
```

### Step 2: Run Automated Deployment

```bash
# SSH to production server
ssh root@178.156.194.174

# Run automated deployment script
cd /root
chmod +x deploy_to_production.sh
./deploy_to_production.sh
```

The script will automatically:
- ✅ Setup production dependencies and helper scripts
- ✅ Configure dual trading
- ✅ Create systemd services with dependency management
- ✅ Start both services
- ✅ Enable services on boot
- ✅ Verify deployment with health checks

### Step 3: Add Alpaca Credentials

After deployment, add your Alpaca API credentials to both config files:

**Argo Config** (`/root/argo-production-green/config.json`):
```json
{
  "alpaca": {
    "api_key": "YOUR_ARGO_API_KEY",
    "secret_key": "YOUR_ARGO_SECRET_KEY"
  }
}
```

**Prop Firm Config** (`/root/argo-production-prop-firm/config.json`):
```json
{
  "alpaca": {
    "prop_firm_test": {
      "api_key": "YOUR_PROP_FIRM_API_KEY",
      "secret_key": "YOUR_PROP_FIRM_SECRET_KEY"
    }
  }
}
```

Then restart services:
```bash
sudo systemctl restart argo-trading.service
sudo systemctl restart argo-trading-prop-firm.service
```

## 📋 Manual Deployment

If you prefer manual deployment, see `COMPLETE_DEPLOYMENT_GUIDE.md` for step-by-step instructions.

## 📚 Documentation

- `COMPLETE_DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `DUAL_TRADING_PRODUCTION_SETUP.md` - Detailed setup documentation
- `DEPLOYMENT_CHECKLIST.md` - Deployment checklist
- `FINAL_DUAL_TRADING_SETUP.md` - Summary and architecture

## 🔧 Scripts Included

- `deploy_to_production.sh` - Complete automated deployment
- `setup_production_dependencies.sh` - Setup dependency checking utilities (NEW)
- `create_systemd_services.sh` - Create systemd services with dependency management
- `fix_systemd_services.sh` - Fix/update systemd services
- `enable_dual_trading_production.sh` - Configure dual trading
- `verify_dual_trading_setup.py` - Verify deployment

## ✅ Verification

After deployment, verify both services:

```bash
# Check service status
sudo systemctl status argo-trading.service
sudo systemctl status argo-trading-prop-firm.service

# Check health
curl http://localhost:8000/health  # Argo
curl http://localhost:8001/health  # Prop Firm

# Run verification script
python3 verify_dual_trading_setup.py
```

## 🎯 Production Server

- **IP**: 178.156.194.174
- **User**: root
- **Argo Service**: Port 8000
- **Prop Firm Service**: Port 8001
