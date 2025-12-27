output "rule_name" {
  value       = aws_cloudwatch_event_rule.schedule.name
  description = "EventBridge rule name"
}

output "invoke_role_arn" {
  value       = aws_iam_role.events_invoke_automation.arn
  description = "Role ARN used by EventBridge to start the Automation"
}
