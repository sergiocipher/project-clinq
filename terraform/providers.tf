# WHY THIS FILE EXISTS:
# Configures the AWS provider with a default region and a set of tags that
# are automatically applied to every resource Terraform creates. This ensures
# every resource is labelled with the project and the fact it is managed by
# Terraform — useful for cost attribution and auditing.

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project    = var.project_name
      ManagedBy  = "terraform"
      Course     = "devops-capstone"
    }
  }
}
