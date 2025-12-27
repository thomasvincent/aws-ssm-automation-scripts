.PHONY: help register-docs validate-docs deploy-schedule-cfn deploy-schedule-tf

AWS_REGION ?= us-east-1
STACK_NAME ?= cost-savings-schedule
DOCUMENT_NAME ?= CostSavingsRemediation
AUTOMATION_ASSUME_ROLE_ARN ?=
SCHEDULE_EXPRESSION ?= cron(0 9 * * ? *)
IDLE_DAYS ?= 30
LOW_UTIL ?= 10
SNAPSHOT_BEFORE_DELETE ?= true
DRY_RUN ?= true
BASE ?= origin/main

help:
	@echo "Targets:"
	@echo "  register-docs        - Create/update all top-level *.yaml SSM Automation docs"
	@echo "  validate-docs        - aws ssm validate-document for top-level *.yaml"
	@echo "  deploy-schedule-cfn  - Deploy EventBridge schedule via CloudFormation"
	@echo "  deploy-schedule-tf   - Deploy EventBridge schedule via Terraform (in examples/terraform/cost_savings_schedule)"
	@echo "  pr-docs              - List changed top-level YAML and SSM Automation docs vs $(BASE)"
	@echo "  pr-validate-ssm      - Validate changed SSM Automation docs vs $(BASE) with aws ssm validate-document"

register-docs:
	@set -e; \
	for f in *.yaml; do \
	  [ -e "$$f" ] || continue; \
	  name=$${f%.yaml}; \
	  echo "Registering $$name from $$f in $(AWS_REGION)..."; \
	  if aws --region $(AWS_REGION) ssm create-document \
	        --name "$$name" --document-type Automation --content file://"$$f" >/dev/null 2>&1; then \
	    echo "Created $$name"; \
	  else \
	    echo "Updating $$name"; \
	    aws --region $(AWS_REGION) ssm update-document --name "$$name" --content file://"$$f" >/dev/null; \
	    latest=$$(aws --region $(AWS_REGION) ssm describe-document --name "$$name" --query 'Document.LatestVersion' --output text); \
	    aws --region $(AWS_REGION) ssm update-document-default-version --name "$$name" --document-version "$$latest" >/dev/null; \
	    echo "Set default version to $$latest for $$name"; \
	  fi; \
	done

validate-docs:
	@set -e; \
	for f in *.yaml; do \
	  [ -e "$$f" ] || continue; \
	  echo "Validating $$f"; \
	  aws --region $(AWS_REGION) ssm validate-document --document-type Automation --content file://"$$f" >/dev/null; \
	done; \
	echo "All documents validated."

deploy-schedule-cfn:
	@if [ -z "$(AUTOMATION_ASSUME_ROLE_ARN)" ]; then echo "AUTOMATION_ASSUME_ROLE_ARN is required"; exit 1; fi
	aws --region $(AWS_REGION) cloudformation deploy \
	  --stack-name $(STACK_NAME) \
	  --template-file examples/eventbridge/cost_savings_eventbridge.yaml \
	  --parameter-overrides \
	    DocumentName=$(DOCUMENT_NAME) \
	    AutomationAssumeRoleArn=$(AUTOMATION_ASSUME_ROLE_ARN) \
	    ScheduleExpression='$(SCHEDULE_EXPRESSION)' \
	    IdleDaysThreshold=$(IDLE_DAYS) \
	    LowUtilizationThreshold=$(LOW_UTIL) \
	    SnapshotBeforeDelete=$(SNAPSHOT_BEFORE_DELETE) \
	    DryRun=$(DRY_RUN)

deploy-schedule-tf:
	@cd examples/terraform/cost_savings_schedule && \
	terraform init && \
	terraform apply -auto-approve \
	  -var="document_name=$(DOCUMENT_NAME)" \
	  -var="automation_assume_role_arn=$(AUTOMATION_ASSUME_ROLE_ARN)" \
	  -var="schedule_expression=$(SCHEDULE_EXPRESSION)" \
	  -var="idle_days_threshold=$(IDLE_DAYS)" \
	  -var="low_utilization_threshold=$(LOW_UTIL)" \
	  -var="snapshot_before_delete=$(SNAPSHOT_BEFORE_DELETE)" \
	  -var="dry_run=$(DRY_RUN)"

pr-docs:
	@set -e; \
	git fetch origin >/dev/null 2>&1 || true; \
	base=$$(git merge-base HEAD $(BASE) || echo $(BASE)); \
	echo "Comparing against $$base"; \
	files=$$(git diff --name-only $$base HEAD | grep -E '^[^/]+\.ya?ml$$' || true); \
	echo "Changed top-level YAML:"; echo "$$files"; \
	ssm=$$(echo "$$files" | xargs -I{} sh -c 'grep -q "schemaVersion" {} && grep -q "assumeRole:" {} && echo {}' || true); \
	echo "Changed SSM Automation docs:"; echo "$$ssm"

pr-validate-ssm:
	@set -e; \
	$(MAKE) pr-docs >/dev/null; \
	git fetch origin >/dev/null 2>&1 || true; \
	base=$$(git merge-base HEAD $(BASE) || echo $(BASE)); \
	files=$$(git diff --name-only $$base HEAD | grep -E '^[^/]+\.ya?ml$$' || true); \
	ssm=$$(echo "$$files" | xargs -I{} sh -c 'grep -q "schemaVersion" {} && grep -q "assumeRole:" {} && echo {}' || true); \
	[ -z "$$ssm" ] && { echo "No changed SSM Automation docs."; exit 0; }; \
	for f in $$ssm; do \
	  echo "Validating $$f"; \
	  aws --region $(AWS_REGION) ssm validate-document --document-type Automation --content file://"$$f" >/dev/null; \
	done; \
	echo "Changed SSM docs validated."
