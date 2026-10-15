# WHY THIS FILE EXISTS:
# Creates the AWS VPC with public and private subnets across multiple
# availability zones. Public subnets host the internet-facing load balancer
# (created by the Kubernetes Ingress controller). Private subnets host the
# EKS worker nodes — they can reach the internet via the NAT gateway but
# are not directly reachable from the internet.
#
# ⚠️  COST WARNING: running this infrastructure costs approximately:
#   EKS control plane: ~$0.10/hour
#   NAT gateway:       ~$0.05/hour + data transfer
#   3 × t3.medium:     ~$0.12/hour each
#   Total:             ~$0.46/hour (~$11/day)
# Run `terraform destroy` (via scripts/pre-destroy.sh first) when done.

data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, var.az_count)
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = var.project_name
  cidr = var.vpc_cidr

  azs = local.azs

  # Public subnets: .0–.99 range (one per AZ, /24 each)
  public_subnets = [for i, az in local.azs : cidrsubnet(var.vpc_cidr, 8, i)]

  # Private subnets: .100–.199 range (one per AZ, /24 each)
  private_subnets = [for i, az in local.azs : cidrsubnet(var.vpc_cidr, 8, i + 100)]

  enable_nat_gateway   = true
  single_nat_gateway   = true  # single NAT saves cost; use one-per-AZ for production HA
  enable_dns_hostnames = true

  # Tags required by the AWS Load Balancer Controller to discover subnets
  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
  }
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = 1
  }
}
