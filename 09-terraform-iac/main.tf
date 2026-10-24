terraform {
  required_version = ">= 1.5.0"
}

locals {
  vpc_cidr       = "10.0.0.0/16"
  public_subnet  = cidrsubnet(local.vpc_cidr, 8, 1)
  private_subnet = cidrsubnet(local.vpc_cidr, 8, 2)
}

resource "terraform_data" "vpc" {
  input = {
    name        = "${var.environment}-study-vpc"
    cidr        = local.vpc_cidr
    environment = var.environment
  }
}

resource "terraform_data" "public_subnet" {
  input = {
    name       = "${var.environment}-public"
    cidr       = local.public_subnet
    parent_vpc = terraform_data.vpc.input.name
  }
}

resource "terraform_data" "private_subnet" {
  input = {
    name       = "${var.environment}-private"
    cidr       = local.private_subnet
    parent_vpc = terraform_data.vpc.input.name
  }
}
