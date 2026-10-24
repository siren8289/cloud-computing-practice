output "network_plan" {
  description = "Simulated network layout, not a real cloud VPC"
  value = {
    vpc     = terraform_data.vpc.output
    public  = terraform_data.public_subnet.output
    private = terraform_data.private_subnet.output
  }
}
