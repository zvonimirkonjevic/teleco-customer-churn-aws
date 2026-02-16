terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "teleco-churn-terraform-state"
    key            = "global/s3/terraform.tfstate"
    region         = "eu-central-1"
    encrypt        = true
    profile        = "teleco-churn-terraform"
  }
}

provider "aws" {
    alias = "eu-central"
    region = "eu-central-1"
    profile = "teleco-churn-terraform"
}