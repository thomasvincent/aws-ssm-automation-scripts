variable "region" {
  type        = string
  description = "AWS region"
  default     = null
}

variable "document_name" {
  type        = string
  description = "SSM Automation document name"
  default     = "CostSavingsRemediation"
}

variable "schedule_expression" {
  type        = string
  description = "EventBridge schedule expression"
  default     = "cron(0 9 * * ? *)" # 09:00 UTC daily
}

variable "automation_assume_role_arn" {
  type        = string
  description = "Role ARN passed to Automation (AutomationAssumeRole parameter)"
}

variable "idle_days_threshold" {
  type        = number
  default     = 30
}

variable "low_utilization_threshold" {
  type        = number
  default     = 10
}

variable "snapshot_before_delete" {
  type        = bool
  default     = true
}

variable "dry_run" {
  type        = bool
  default     = true
}

variable "notification_topic_arn" {
  type        = string
  default     = ""
}

variable "tags" {
  type        = map(string)
  default     = {}
}
