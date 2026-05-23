resource "azurerm_resource_group" "main" {
  name     = "${var.name}-rg"
  location = var.location
  tags = {
    azd-env-name = var.name
  }
}

resource "azurerm_service_plan" "main" {
  name                = "${var.name}-service-plan"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku_name            = "S1"
  os_type             = "Linux"
  tags                = azurerm_resource_group.main.tags
}

resource "azurerm_linux_web_app" "web" {
  name                = "${var.name}-web"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    app_command_line = "src/entrypoint.sh"
    application_stack {
      python_version = "3.11"
    }
  }


  app_settings = {
    SCM_DO_BUILD_DURING_DEPLOYMENT = "true"
    AZURE_POSTGRESQL_CONNECTIONSTRING = format(
      "dbname=%s host=%s port=5432 sslmode=require user=%s password=%s",
      "postgres",
      azurerm_postgresql_flexible_server.postgres.fqdn,
      azurerm_postgresql_flexible_server.postgres.administrator_login,
      var.database_password
    )
    SECRET_KEY = var.secret_key
  }

  https_only = true
  tags       = azurerm_resource_group.main.tags
}

resource "azurerm_postgresql_flexible_server" "postgres" {
  name                          = "nextopspgt32"
  location                      = azurerm_resource_group.main.location
  resource_group_name           = azurerm_resource_group.main.name
  administrator_login           = "sqladmin"
  administrator_password        = var.database_password
  version                       = "12"
  sku_name                      = "B_Standard_B1ms"
  storage_mb                    = 32768
  public_network_access_enabled = true
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.postgres.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}
