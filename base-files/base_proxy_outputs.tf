############################ base_proxy_outputs.tf
output "Server-IP" {
  value = aws_instance.quick-proxy-deployer.public_ip
}

output "Server-DNS" {
  value = aws_instance.quick-proxy-deployer.public_dns
}
############################ base_proxy_outputs.tf