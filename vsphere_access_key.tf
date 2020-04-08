resource "tls_private_key" "generated" {
  algorithm = "RSA"
}

resource "random_pet" "random" {
  length    = 1
}

locals {
  public_key_filename  = "./keys/generated-access-key-${random_pet.random.id}.pub"
  private_key_filename = "./keys/generated-access-key-${random_pet.random.id}.pem"
}

resource "local_file" "public_key_openssh" {
  content  = tls_private_key.generated.public_key_openssh
  filename = local.public_key_filename
  file_permission      = "0700"
}

resource "local_file" "private_key_pem" {
  content  = tls_private_key.generated.private_key_pem
  filename = local.private_key_filename
  file_permission      = "0700"
}
