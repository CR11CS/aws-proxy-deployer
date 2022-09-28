############################ base_key_export_windows.tf
resource "tls_private_key" "pk" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

// Create aws_key_pair resource
resource "aws_key_pair" "kp" {
  key_name   = "proxy-server-key"
  public_key = chomp(tls_private_key.pk.public_key_openssh)

  // Executes local PowerShell code to write private key to local folder, same as downloading from EC2
  provisioner "local-exec" {
    command     = <<EOT
    '${tls_private_key.pk.private_key_pem}' | % {$_ -replace "`r", ""} | Set-Content -NoNewline ./'proxy-server-key.pem' -Force
    EOT
    interpreter = ["PowerShell", "-Command"]
  }
}
############################ base_key_export_windows.tf