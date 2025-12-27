data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

provider "aws" {
  region = coalesce(var.region, data.aws_region.current.name)
}

locals {
  document_arn = "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:automation-definition/${var.document_name}:$DEFAULT"

  input_payload = jsonencode({
    AutomationAssumeRole      = [var.automation_assume_role_arn]
    IdleDaysThreshold         = [tostring(var.idle_days_threshold)]
    LowUtilizationThreshold   = [tostring(var.low_utilization_threshold)]
    SnapshotBeforeDelete      = [var.snapshot_before_delete ? "true" : "false"]
    DryRun                    = [var.dry_run ? "true" : "false"]
    NotificationTopicArn      = [var.notification_topic_arn]
  })
}

resource "aws_iam_role" "events_invoke_automation" {
  name               = "events-invoke-ssm-automation"
  assume_role_policy = data.aws_iam_policy_document.events_assume_role.json
  tags               = var.tags
}

data "aws_iam_policy_document" "events_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "invoke_permissions" {
  name   = "invoke-ssm-automation"
  role   = aws_iam_role.events_invoke_automation.id
  policy = data.aws_iam_policy_document.invoke_policy.json
}

data "aws_iam_policy_document" "invoke_policy" {
  statement {
    sid     = "StartAutomationExecution"
    effect  = "Allow"
    actions = ["ssm:StartAutomationExecution"]
    resources = [
      local.document_arn
    ]
  }

  statement {
    sid     = "PassAutomationRole"
    effect  = "Allow"
    actions = ["iam:PassRole"]
    resources = [var.automation_assume_role_arn]
  }
}

resource "aws_cloudwatch_event_rule" "schedule" {
  name                = "cost-savings-${var.document_name}-schedule"
  description         = "Schedule SSM Automation execution for cost savings remediation"
  schedule_expression = var.schedule_expression
  tags                = var.tags
}

resource "aws_cloudwatch_event_target" "automation" {
  rule      = aws_cloudwatch_event_rule.schedule.name
  target_id = "StartCostSavingsAutomation"
  arn       = local.document_arn
  role_arn  = aws_iam_role.events_invoke_automation.arn
  input     = local.input_payload
}
