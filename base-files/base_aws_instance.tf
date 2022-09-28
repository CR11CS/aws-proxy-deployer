############################ base_aws_instance.tf
resource "aws_instance" "quick-proxy-deployer" {
  ami             = data.aws_ami.ubuntu.id
  instance_type   = "t2.micro"
  key_name        = "proxy-server-key"
  security_groups = ["allow_proxy_users"]
  // Waits for aws_key_pair resource generation first
  depends_on = [
    aws_key_pair.kp,
    aws_security_group.allow_proxy_users
  ]

  // Runs tinyproxy install & config script on EC2 instance
  provisioner "remote-exec" {
      connection {
    # The default username for our AMI
    user = "ubuntu"
    host = aws_instance.quick-proxy-deployer.public_dns
    type = "ssh"
    private_key = tls_private_key.pk.private_key_pem
  }
    scripts = [
      "../tinyproxy-install.sh"
    ]
  }
}
############################ base_aws_instance.tf