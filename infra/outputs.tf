output "instance_id" {
  description = "ID da instância, para o aws ssm start-session"
  value       = aws_instance.edurag.id
}

output "public_ip" {
  description = "IPv4 público, só para o nmap de fora"
  value       = aws_instance.edurag.public_ip
}
