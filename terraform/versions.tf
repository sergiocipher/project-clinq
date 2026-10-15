# WHY THIS FILE EXISTS:
# Pins the Terraform CLI version and all provider versions so the plan is
# reproducible across machines and CI. The lock file (.terraform.lock.hcl)
# is committed to Git for the same reason — do not add it to .gitignore.

terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
