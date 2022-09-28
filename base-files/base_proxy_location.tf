############################ base_proxy_location.tf
terraform {
  required_version = "~>1.2.3"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">=4.16"
    }
  }
}

provider "aws" {
  // vars not allowed for keys
  region = var.region
  access_key = "<ACCESS_KEY>"
  secret_key = "<SECRET_KEY>"
  // below are specific to LocalStack usage
#    endpoints {
#    ec2            = "http://localhost:4566"
#  }
#  skip_credentials_validation = true
#  skip_metadata_api_check     = true
#  skip_requesting_account_id  = true
}
############################ base_proxy_location.tf