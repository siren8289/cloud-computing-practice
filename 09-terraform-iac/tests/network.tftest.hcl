run "subnet_cidrs" {
  command = plan

  assert {
    condition     = local.public_subnet == "10.0.1.0/24"
    error_message = "Public subnet CIDR does not match."
  }

  assert {
    condition     = local.private_subnet == "10.0.2.0/24"
    error_message = "Private subnet CIDR does not match."
  }
}

run "resource_dependency" {
  command = plan

  assert {
    condition = (
      terraform_data.public_subnet.input.parent_vpc == "dev-study-vpc"
    )
    error_message = "Public subnet is not linked to the simulated VPC."
  }
}

run "production_label" {
  command = plan

  variables {
    environment = "prod"
  }

  assert {
    condition     = terraform_data.vpc.input.name == "prod-study-vpc"
    error_message = "Environment variable was not applied."
  }
}
