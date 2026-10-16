# WHY THIS FILE EXISTS:
# Exposes key values after `terraform apply` so you do not have to dig through
# the AWS console. The configure_kubectl output is a ready-to-run command that
# connects your local kubectl to the new cluster.

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets (used by the load balancer)"
  value       = module.vpc.public_subnets
}

output "private_subnet_ids" {
  description = "IDs of the private subnets (used by EKS worker nodes)"
  value       = module.vpc.private_subnets
}

# EKS outputs — uncomment after enabling the EKS module
# output "cluster_name" {
#   description = "Name of the EKS cluster"
#   value       = module.eks.cluster_name
# }
#
# output "cluster_endpoint" {
#   description = "Kubernetes API server endpoint"
#   value       = module.eks.cluster_endpoint
# }
#
# output "configure_kubectl" {
#   description = "Run this command to configure kubectl to talk to the cluster"
#   value       = "aws eks update-kubeconfig --region ${var.region} --name ${module.eks.cluster_name}"
# }
