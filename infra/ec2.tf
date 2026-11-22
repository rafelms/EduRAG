# O provider valida a AMI com DescribeImages antes de lançar, e essa API
# não aceita "resolve:ssm:...". Lemos o parâmetro público e passamos o ID.
data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

resource "aws_instance" "edurag" {
  ami                    = data.aws_ssm_parameter.al2023.insecure_value
  instance_type          = "t3.small"
  iam_instance_profile   = aws_iam_instance_profile.edurag_ec2.name
  vpc_security_group_ids = [aws_security_group.edurag.id]

  user_data                   = file("${path.module}/user_data.sh")
  user_data_replace_on_change = true

  credit_specification {
    cpu_credits = "standard"
  }

  root_block_device {
    volume_type = "gp3"
    volume_size = 30
    encrypted   = true
  }

  metadata_options {
    http_tokens = "required"
  }

  tags = {
    Name = "edurag"
  }
}
