data "aws_vpc" "padrao" {
  default = true
}

resource "aws_security_group" "edurag" {
  name        = "edurag-sem-entrada"
  description = "EduRAG: nenhuma entrada; acesso so pelo SSM"
  vpc_id      = data.aws_vpc.padrao.id
}

resource "aws_vpc_security_group_egress_rule" "https" {
  security_group_id = aws_security_group.edurag.id
  description       = "Saida HTTPS: SSM, dnf e GHCR"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}
