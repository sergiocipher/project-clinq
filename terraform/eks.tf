# WHY THIS FILE EXISTS:
# Creates the EKS cluster and its managed node group inside the private
# subnets of the VPC. Worker nodes live in private subnets (unreachable from
# the internet directly) but the cluster API endpoint is public so you can
# run kubectl from your laptop.
# The EBS CSI driver add-on is required to provision PersistentVolumeClaims
# (gp3 volumes) for the Postgres StatefulSet.

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = var.project_name
  cluster_version = var.kubernetes_version

  # Nodes go in private subnets; control plane in VPC subnets
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids

  # Public endpoint so kubectl works from a laptop
  cluster_endpoint_public_access = true

  # Gives the IAM identity that runs terraform full admin on the cluster
  enable_cluster_creator_admin_permissions = true

  # Core EKS add-ons — most_recent picks the latest validated version
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  eks_managed_node_groups = {
    default = {
      instance_types = var.node_instance_types
      min_size       = var.node_min_size
      max_size       = var.node_max_size
      desired_size   = var.node_desired_size

      # Grant the EBS CSI driver permission to manage volumes.
      # NOTE: this is a classroom shortcut (attach policy directly to node role).
      # In production you would use IRSA or EKS Pod Identity to give only the
      # driver pod — not every pod on the node — access to EBS.
      iam_role_additional_policies = {
        AmazonEBSCSIDriverPolicy = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
      }
    }
  }
}
