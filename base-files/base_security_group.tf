############################ base_security_group.tf
resource "aws_security_group" "allow_proxy_users" {
  name        = "allow_proxy_users"
  description = "Allow inbound traffic from proxy users."

  ingress {
    description = "Inbound traffic from proxy users."
    from_port   = 8888
    to_port     = 8888
    protocol    = "tcp"
    cidr_blocks = var.cidr_blocks
  }

    ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description      = "Outbound traffic allowed through all ports and protocols."
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}
############################ base_security_group.tf