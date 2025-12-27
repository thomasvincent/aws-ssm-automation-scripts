# AWS Cost Optimization Automation

This repository includes SSM Automation documents designed to identify and remediate common sources of cloud waste. These scripts helped achieve **~50% AWS cost reduction** across client environments.

## Cost Optimization Scripts

### 1. `cost_optimization_recommendations.yaml`

Automated SSM document that identifies cost savings opportunities:

**What It Finds:**
- Idle and underutilized EC2 instances
- Orphaned EBS volumes (unattached)
- Unused Elastic IPs
- Oversized RDS instances
- Idle NAT Gateways
- Unattached EBS snapshots older than 90 days

**How It Works:**
1. Scans target accounts for resource utilization patterns
2. Correlates CloudWatch metrics with provisioned capacity
3. Generates actionable recommendations with estimated savings
4. Outputs to S3 for reporting and tracking

### 2. Resource Tagging (`create_and_tag_resources.yaml`)

Cost allocation starts with tagging. This document enforces consistent tagging across resources, enabling:
- Accurate cost allocation by team/project
- Identification of untagged (potentially orphaned) resources
- Automated cleanup policies based on tags

## Typical Savings Breakdown

Based on client implementations:

| Category | Typical Waste | Savings Method |
|----------|---------------|----------------|
| Idle EC2 instances | 15-25% of compute spend | Right-sizing + scheduling |
| Orphaned EBS volumes | 5-10% of storage spend | Automated cleanup |
| Over-provisioned RDS | 10-20% of database spend | Instance right-sizing |
| Unused Elastic IPs | $3.60/month each | Automated release |
| NAT Gateway idle time | 5-15% of networking spend | Traffic analysis + consolidation |

## Usage

```bash
# Run cost optimization scan
aws ssm start-automation-execution \
  --document-name "CostOptimizationRecommendations" \
  --parameters "TargetAccounts=['123456789012'],ReportBucket=my-reports-bucket"
```

## Integration with FinOps Workflows

These scripts are designed to integrate with:
- AWS Cost Explorer for trend analysis
- Slack/Teams notifications for alerts
- JIRA for ticket creation on actionable items
- Scheduled runs via EventBridge

## Results

In production environments, these automation scripts typically identify:
- **30-50%** of EC2 instances as candidates for right-sizing
- **10-20%** of EBS volumes as orphaned
- **$10K-100K+** annual savings depending on environment size

---

*Part of the [aws-ssm-automation-scripts](https://github.com/thomasvincent/aws-ssm-automation-scripts) collection.*
