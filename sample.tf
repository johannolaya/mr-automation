

module "other-tool-provision-application" {
  source                         = "git::ssh://git-test.git?ref=v5.1.3"
  provision_ecs_cluster          = var.provision_ecs_cluster
  parameter                      = "appgroup"
  tags                           = var.tags
}


module "tool-provision-application" {
  source                         = "git::ssh://git-test.git?ref=v5.1.3"
  provision_ecs_cluster          = var.provision_ecs_cluster
  parameter                      = "appgroup"
  tags                           = var.tags
}
