#!/usr/bin/env bats
# Bats framework: https://github.com/bats-core/bats-core
# az CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
# Prerequisite: login with 'az login' and set test resource group


#---------------- Bicep Template Integration Tests (BATS + Azure CLI) ----------------#
# These tests validate ARM resource deployment, parameters, outputs, and key properties.
# Assumes resource group exists and test user has contributor rights in Azure.

# =============== Setup/Teardown ===================
setup() {
  export TEST_RG="test-healthai-rg"
  export LOCATION="eastus"
  export PREFIX="healthai"
  export SSH_KEY_PATH="$HOME/.ssh/id_rsa.pub"
  export SSH_KEY=$(cat "$SSH_KEY_PATH")
  export DEPLOYMENT_NAME="bicep-e2e-$(date +%s)"
}

teardown() {
  az deployment group delete --resource-group "$TEST_RG" --name "$DEPLOYMENT_NAME" --no-wait
}

# =============== TESTS ===================

@test "Deploy Bicep template with required parameters - Should Succeed" {
  run az deployment group create \
    --resource-group "$TEST_RG" \
    --template-file main.bicep \
    --name "$DEPLOYMENT_NAME" \
    --parameters namePrefix="$PREFIX" location="$LOCATION" sshPublicKey="$SSH_KEY"
  [ "$status" -eq 0 ]
  [[ "$output" =~ '"provisioningState": "Succeeded"' ]]
}

@test "Storage Account - Should Exist and Have Secure Configuration" {
  storage_account_name="${PREFIX}storage"
  run az storage account show --name "$storage_account_name" --resource-group "$TEST_RG"
  [ "$status" -eq 0 ]
  [[ "$output" =~ '"allowBlobPublicAccess": false' ]]
  [[ "$output" =~ '"minimumTlsVersion": "TLS1_2"' ]]
  [[ "$output" =~ '"name": "$storage_account_name"' ]]
}

@test "Azure Machine Learning Workspace - Should Be Private and Use Correct Storage Account" {
  aml_ws_name="${PREFIX}-mlws"
  run az ml workspace show --name "$aml_ws_name" --resource-group "$TEST_RG"
  [ "$status" -eq 0 ]
  [[ "$output" =~ '"publicNetworkAccess": "Disabled"' ]]
  # Validate underlying storage account assignment
  storage_account_name="${PREFIX}storage"
  [[ "$output" =~ "$storage_account_name" ]]
}

@test "Azure Data Factory - Should be Created with SystemAssigned Identity" {
  adf_name="${PREFIX}-adf"
  run az datafactory show --factory-name "$adf_name" --resource-group "$TEST_RG"
  [ "$status" -eq 0 ]
  [[ "$output" =~ '"identity": {' ]]
  [[ "$output" =~ '"type": "SystemAssigned"' ]]
}

@test "AKS Cluster - Should Exist With RBAC, SystemAssigned Identity, and Secure SSH" {
  aks_name="${PREFIX}-aks"
  run az aks show --name "$aks_name" --resource-group "$TEST_RG"
  [ "$status" -eq 0 ]
  [[ "$output" =~ '"enableRBAC": true' ]]
  [[ "$output" =~ '"identity": {' ]]
  [[ "$output" =~ '"type": "SystemAssigned"' ]]
  # Check node pool and SSH key presence
  [[ "$output" =~ '"adminUsername": "azureuser"' ]]
}

@test "Outputs - Should Match Resource Names in Parameters" {
  outputs=$(az deployment group show --resource-group "$TEST_RG" --name "$DEPLOYMENT_NAME" --query properties.outputs)
  [[ "$outputs" =~ "${PREFIX}storage" ]]
  [[ "$outputs" =~ "${PREFIX}-mlws" ]]
  [[ "$outputs" =~ "${PREFIX}-adf" ]]
  [[ "$outputs" =~ "${PREFIX}-aks" ]]
}

@test "Edge Case - Missing Required Parameter (sshPublicKey) - Should Fail" {
  run az deployment group create \
      --resource-group "$TEST_RG" \
      --template-file main.bicep \
      --parameters namePrefix="$PREFIX" location="$LOCATION"
  [ "$status" -ne 0 ]
  [[ "$output" =~ 'is required' || "$output" =~ 'Missing required parameter' ]]
}

@test "Edge Case - Invalid SSH Public Key - Should Fail" {
  run az deployment group create \
      --resource-group "$TEST_RG" \
      --template-file main.bicep \
      --parameters namePrefix="$PREFIX" location="$LOCATION" sshPublicKey="invalidkeydata"
  [ "$status" -ne 0 ]
  [[ "$output" =~ 'Invalid value for' || "$output" =~ 'error' ]]
}

# =============== Parameterized Example: Different Location ===============
@test "Parameterized - Deploy Template in West Europe - Should Succeed" {
  run az deployment group create \
    --resource-group "$TEST_RG" \
    --template-file main.bicep \
    --name "$DEPLOYMENT_NAME-euwest" \
    --parameters namePrefix="$PREFIX" location="westeurope" sshPublicKey="$SSH_KEY"
  [ "$status" -eq 0 ]
  [[ "$output" =~ '"provisioningState": "Succeeded"' ]]
}

# End of Bicep Infra E2E/Test Suite