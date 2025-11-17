# Cost Monitoring & Budget Alerts

Guide for monitoring AWS/infrastructure costs and setting up budget alerts.

## Table of Contents

1. [Overview](#overview)
2. [AWS Cost Monitoring](#aws-cost-monitoring)
3. [Budget Alerts](#budget-alerts)
4. [Cost Optimization](#cost-optimization)
5. [Cost Tracking Dashboard](#cost-tracking-dashboard)

---

## Overview

### Why Monitor Costs?

- **Budget Control**: Stay within budget limits
- **Cost Optimization**: Identify cost-saving opportunities
- **Anomaly Detection**: Detect unexpected cost spikes
- **Forecasting**: Predict future costs

### Cost Categories

- **Compute**: EC2, Lambda, ECS
- **Database**: RDS, ElastiCache
- **Storage**: S3, EBS
- **Networking**: Data transfer, CloudFront
- **Monitoring**: CloudWatch, X-Ray

---

## AWS Cost Monitoring

### AWS Cost Explorer

1. **Enable Cost Explorer** (if not already enabled):
   - Go to AWS Cost Management → Cost Explorer
   - Click "Enable Cost Explorer"
   - Wait 24 hours for data to populate

2. **View Costs**:
   - Daily, monthly, or custom date ranges
   - Filter by service, region, tags
   - Group by service, usage type, etc.

### Cost and Usage Reports

1. **Create Report**:
   ```bash
   aws cur put-report-definition \
     --report-definition file://cost-report-definition.json
   ```

2. **Report Definition** (`cost-report-definition.json`):
   ```json
   {
     "ReportName": "argo-alpine-cost-report",
     "TimeUnit": "DAILY",
     "Format": "Parquet",
     "Compression": "Parquet",
     "AdditionalSchemaElements": ["RESOURCES"],
     "S3Bucket": "your-cost-reports-bucket",
     "S3Prefix": "cost-reports/",
     "S3Region": "us-east-1",
     "RefreshClosedReports": true,
     "ReportVersioning": "OVERWRITE_REPORT"
   }
   ```

### Tagging Strategy

Tag all resources for cost tracking:

```bash
# Tag EC2 instances
aws ec2 create-tags \
  --resources i-1234567890abcdef0 \
  --tags Key=Project,Value=ArgoAlpine Key=Environment,Value=Production

# Tag RDS instances
aws rds add-tags-to-resource \
  --resource-name arn:aws:rds:us-east-1:123456789012:db:my-db \
  --tags Key=Project,Value=ArgoAlpine Key=Environment,Value=Production
```

**Required Tags**:
- `Project`: ArgoAlpine
- `Environment`: Production, Staging, Development
- `Service`: Argo, Alpine-Backend, Alpine-Frontend
- `CostCenter`: Engineering, Operations

---

## Budget Alerts

### AWS Budgets Setup

1. **Create Budget** via AWS Console:
   - Go to AWS Cost Management → Budgets
   - Click "Create budget"
   - Choose "Cost budget"
   - Set amount and period (monthly recommended)

2. **Create Budget via CLI**:

```bash
# Create monthly budget
aws budgets create-budget \
  --account-id 123456789012 \
  --budget file://monthly-budget.json \
  --notifications-with-subscribers file://budget-notifications.json
```

**Monthly Budget** (`monthly-budget.json`):
```json
{
  "BudgetName": "argo-alpine-monthly-budget",
  "BudgetLimit": {
    "Amount": "1000",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {
    "TagKeyValue": [
      "Project$ArgoAlpine"
    ]
  }
}
```

**Notifications** (`budget-notifications.json`):
```json
[
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "alerts@example.com"
      },
      {
        "SubscriptionType": "SNS",
        "Address": "arn:aws:sns:us-east-1:123456789012:cost-alerts"
      }
    ]
  },
  {
    "Notification": {
      "NotificationType": "FORECASTED",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 100,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "alerts@example.com"
      }
    ]
  }
]
```

### Alert Thresholds

Recommended thresholds:

- **80% of budget**: Warning alert
- **100% of budget**: Critical alert
- **120% of budget**: Emergency alert
- **Forecasted > 100%**: Early warning

### SNS Topic Setup

```bash
# Create SNS topic
aws sns create-topic --name cost-alerts

# Subscribe email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:cost-alerts \
  --protocol email \
  --notification-endpoint alerts@example.com

# Subscribe Slack (via Lambda)
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:cost-alerts \
  --protocol lambda \
  --notification-endpoint arn:aws:lambda:us-east-1:123456789012:function:slack-notifier
```

---

## Cost Optimization

### Right-Sizing

1. **EC2 Instances**:
   - Review CloudWatch metrics (CPU, memory, network)
   - Use AWS Compute Optimizer
   - Consider Reserved Instances for steady workloads

2. **RDS Instances**:
   - Monitor database performance metrics
   - Use RDS Performance Insights
   - Consider Aurora Serverless for variable workloads

3. **S3 Storage**:
   - Use lifecycle policies
   - Move old data to Glacier
   - Enable S3 Intelligent-Tiering

### Reserved Instances

For predictable workloads:

```bash
# Purchase Reserved Instance
aws ec2 purchase-reserved-instances-offering \
  --reserved-instances-offering-id <offering-id> \
  --instance-count 1
```

### Spot Instances

For fault-tolerant workloads:

```bash
# Request Spot Instances
aws ec2 request-spot-instances \
  --spot-price "0.05" \
  --instance-count 1 \
  --type "one-time" \
  --launch-specification file://spot-specification.json
```

### Cost Optimization Script

Create `scripts/cost-optimization/analyze-costs.py`:

```python
#!/usr/bin/env python3
"""Analyze AWS costs and suggest optimizations"""
import boto3
from datetime import datetime, timedelta
from collections import defaultdict

def analyze_costs():
    ce = boto3.client('ce')

    # Get costs for last 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date.isoformat(),
            'End': end_date.isoformat()
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'SERVICE'},
            {'Type': 'TAG', 'Key': 'Environment'}
        ]
    )

    costs_by_service = defaultdict(float)
    costs_by_env = defaultdict(float)

    for result in response['ResultsByTime']:
        for group in result['Groups']:
            service = group['Keys'][0]
            env = group['Keys'][1] if len(group['Keys']) > 1 else 'Unknown'
            cost = float(group['Metrics']['UnblendedCost']['Amount'])

            costs_by_service[service] += cost
            costs_by_env[env] += cost

    print("Costs by Service (Last 30 Days):")
    for service, cost in sorted(costs_by_service.items(), key=lambda x: x[1], reverse=True):
        print(f"  {service}: ${cost:.2f}")

    print("\nCosts by Environment:")
    for env, cost in sorted(costs_by_env.items(), key=lambda x: x[1], reverse=True):
        print(f"  {env}: ${cost:.2f}")

    # Suggestions
    print("\nOptimization Suggestions:")
    if costs_by_service.get('AmazonEC2', 0) > 100:
        print("  - Consider Reserved Instances for EC2")
    if costs_by_service.get('AmazonS3', 0) > 50:
        print("  - Review S3 lifecycle policies")
    if costs_by_env.get('Development', 0) > costs_by_env.get('Production', 0) * 0.3:
        print("  - Development environment costs are high, consider scaling down")

if __name__ == '__main__':
    analyze_costs()
```

---

## Cost Tracking Dashboard

### Grafana Dashboard

Create `infrastructure/monitoring/grafana-dashboards/cost-dashboard.json`:

```json
{
  "dashboard": {
    "title": "AWS Cost Monitoring",
    "panels": [
      {
        "title": "Daily Costs",
        "targets": [
          {
            "expr": "aws_cost_explorer_daily_cost",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Cost by Service",
        "targets": [
          {
            "expr": "sum(aws_cost_explorer_daily_cost) by (service)",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Budget vs Actual",
        "targets": [
          {
            "expr": "aws_budget_actual_cost",
            "legendFormat": "Actual"
          },
          {
            "expr": "aws_budget_budgeted_cost",
            "legendFormat": "Budgeted"
          }
        ]
      }
    ]
  }
}
```

### Prometheus Exporter

Create `scripts/cost-monitoring/cost-exporter.py`:

```python
#!/usr/bin/env python3
"""Export AWS costs to Prometheus"""
import boto3
from prometheus_client import Gauge, start_http_server
import time

cost_gauge = Gauge('aws_cost_explorer_daily_cost', 'Daily AWS cost', ['service', 'environment'])

def update_metrics():
    ce = boto3.client('ce')
    # Fetch costs and update metrics
    # ... implementation ...

if __name__ == '__main__':
    start_http_server(8000)
    while True:
        update_metrics()
        time.sleep(3600)  # Update hourly
```

---

## Best Practices

1. **Tag Everything**: All resources should have cost tags
2. **Set Budgets**: Create budgets for all environments
3. **Review Regularly**: Weekly cost reviews
4. **Right-Size**: Continuously optimize resource sizes
5. **Use Reserved Instances**: For predictable workloads
6. **Monitor Anomalies**: Set up alerts for unusual spending
7. **Automate Cleanup**: Auto-delete unused resources

---

## Resources

- [AWS Cost Management](https://aws.amazon.com/aws-cost-management/)
- [AWS Cost Explorer API](https://docs.aws.amazon.com/ce/latest/APIReference/)
- [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
