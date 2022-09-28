########################### base_key_export_linux.tf
resource "tls_private_key" "pk" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

// Create aws_key_pair resource
resource "aws_key_pair" "kp" {
  key_name   = "proxy-server-key"
  public_key = chomp(tls_private_key.pk.public_key_openssh)

  // Executes local code to write private key to local folder, same as downloading from EC2 (then modifies perms to make private)
  provisioner "local-exec" {
    command = "echo '${tls_private_key.pk.private_key_pem}' > ./proxy-server-key.pem && chmod 400 proxy-server-key.pem"
  }
}
########################### base_key_export_linux.tf