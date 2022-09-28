############################ base_vars.tf
variable "region" {
  type = string
  default = <REGION>
}

variable "cidr_blocks" {
  type = list(string)
  default = [<CIDR_BLOCKS>]
}
############################ base_vars.tf