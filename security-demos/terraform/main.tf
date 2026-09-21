# DEMO ONLY: never apply. Checkov should flag public exposure and missing controls.
resource "aws_security_group" "open_demo" {
  name = "training-open-security-group"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
