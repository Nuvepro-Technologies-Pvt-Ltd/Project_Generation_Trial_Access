#!/usr/bin/env bash
# Requires: Azure CLI (az), Bicep CLI (bicep), jq

# ==================================================================
# Test Suite: Runtime and Static Validation of 'main.bicep' for Healthcare AI Backend
# Technology: Azure CLI + Bicep CLI + jq (JSON processor) + Bash
# Purpose: Validates Bicep template syntax, parameter handling, deployment logic and output correctness in a way executable in CI pipelines or locally
#
# Prerequisites:
#   - Azure CLI >=2.49, Bicep CLI >=0.24, jq >=1.6
#   - "az login" completed and default subscription set
#   - Sufficient permissions to create/delete resource groups
#   - The test will create and clean up one or more temporary resource groups
# ==================================================================

set -e
set -o pipefail

TEMPLATE="./main.bicep"
TEST_RG="test-healthai-$(openssl rand -hex 4)"
LOCATION="eastus"
SSH_KEY_VALID="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDk1vgc0IwTestkeyPlaceholder"
SSH_KEY_INVALID=""
SSH_KEY_OUTPUT="ssh-rsa OUTPUTKEY EXAMPLE"
LONG_PREFIX="thisisaverylongcustomprefixthatexceedsthemaxlenexpectedbyazureforresources"
INVALID_PREFIX="<>INVALIDPREFIX"

finish() {
  echo "Cleaning up: deleting test resource group $TEST_RG"
  az group delete --name "$TEST_RG" --yes --no-wait || true
}
trap finish EXIT

pass() { echo -e "\033[32m[PASS]\033[0m $1"; }
fail() { echo -e "\033[31m[FAIL]\033[0m $1" && exit 1; }
section() { echo; echo "# $1"; echo; }

section "1. Bicep Build and Lint"
if bicep build "$TEMPLATE"; then
  pass "Bicep template builds successfully."
else
  fail "Bicep fails to build."
fi
if bicep lint "$TEMPLATE"; then
  pass "Bicep template passes lint checks."
else
  fail "Bicep does not pass linter checks. Review warnings."
fi

section "2. Create Test Resource Group"
az group create -n "$TEST_RG" -l "$LOCATION" > /dev/null
pass "Test RG created: $TEST_RG."

# Helper to validate deployment
validate_deploy() {
  param_namePrefix=$1
  param_sshKey=$2
  echo "Validating with namePrefix='$param_namePrefix', location='$LOCATION', sshKey='${param_sshKey:0:12}...'"
  az deployment group validate \
    --resource-group "$TEST_RG" \
    --template-file "$TEMPLATE" \
    --parameters namePrefix="$param_namePrefix" location="$LOCATION" sshPublicKey="$param_sshKey" > tmp.validate.json 2> tmp.error.log && return 0 || return 1
}

deploy_and_assert() {
  param_namePrefix=$1
  param_sshKey=$2
  section "Deploying: namePrefix='$param_namePrefix'"
  deployment_out=$(az deployment group create \
    --resource-group "$TEST_RG" \
    --template-file "$TEMPLATE" \
    --parameters namePrefix="$param_namePrefix" location="$LOCATION" sshPublicKey="$param_sshKey" \
    --query "{properties:properties,outputs:properties.outputs}" --output json)
  echo "$deployment_out" > tmp.deploy.json
  pass "Deployment succeeded for prefix=$param_namePrefix."
}

# 3. Happy Path Validation
section "3. Parameter: Default and Required Value Handling (Valid SSH Key)"
if validate_deploy "healthai" "$SSH_KEY_VALID"; then
  pass "Validation with all required parameters succeeds."
else
  fail "Validation fails with valid parameters."
fi

deploy_and_assert "healthai" "$SSH_KEY_VALID"

# 4. Storage Account Resource Property Assertions
section "4. Check Storage Account Properties via ARM Query"
STORAGE=$(az resource list -g "$TEST_RG" --resource-type Microsoft.Storage/storageAccounts --query "[0]")
if [ -n "$STORAGE" ]; then
  SKU=$(echo "$STORAGE" | jq -r .sku.name)
  KIND=$(echo "$STORAGE" | jq -r .kind)
  if [[ "$SKU" == "Standard_LRS" && "$KIND" == "StorageV2" ]]; then
    pass "Storage Account SKU/Kind as expected."
  else
    fail "Storage Account SKU/Kind mismatch. Got SKU=$SKU, KIND=$KIND."
  fi
else
  fail "Storage Account not found."
fi

# 5. ML Workspace references correct Storage Account
section "5. Validate ML Workspace Storage Account Reference"
AMLWS=$(az resource list -g "$TEST_RG" --resource-type Microsoft.MachineLearningServices/workspaces --query "[0]")
STORAGE_ID=$(echo "$STORAGE" | jq -r .id)
AMLWS_STORAGE_REF=$(az resource show --ids $(echo "$AMLWS" | jq -r .id) --api-version 2023-04-01 --query "properties.storageAccount" -o tsv)
if [[ "$AMLWS_STORAGE_REF" == "$STORAGE_ID" ]]; then
  pass "ML Workspace references correct storage account ID."
else
  fail "ML Workspace does NOT reference storage account."
fi
AMLWS_PUBLIC_NET=$(az resource show --ids $(echo "$AMLWS" | jq -r .id) --api-version 2023-04-01 --query "properties.publicNetworkAccess" -o tsv)
if [[ "$AMLWS_PUBLIC_NET" == "Disabled" ]]; then
  pass "ML Workspace public network access is disabled."
else
  fail "ML Workspace public network access NOT disabled."
fi

# 6. Data Factory and AKS Resource Assertions
section "6. Validate Data Factory & AKS Properties"
ADF=$(az resource list -g "$TEST_RG" --resource-type Microsoft.DataFactory/factories --query "[0]")
ADF_IDENTITY=$(az resource show --ids $(echo "$ADF" | jq -r .id) --query "identity.type" -o tsv)
if [[ "$ADF_IDENTITY" == "SystemAssigned" ]]; then
  pass "Data Factory Managed Identity set to SystemAssigned."
else
  fail "ADF Managed Identity missing or incorrect ($ADF_IDENTITY)"
fi

AKS=$(az resource list -g "$TEST_RG" --resource-type Microsoft.ContainerService/managedClusters --query "[0]")
AKS_DNS=$(az resource show --ids $(echo "$AKS" | jq -r .id) --query "properties.dnsPrefix" -o tsv)
AKS_ADMIN=$(az resource show --ids $(echo "$AKS" | jq -r .id) --query "properties.linuxProfile.adminUsername" -o tsv)
if [[ "$AKS_DNS" == "healthaiaksdns" && "$AKS_ADMIN" == "azureuser" ]]; then
  pass "AKS DNS prefix and admin username valid."
else
  fail "AKS DNS=$AKS_DNS, or admin=$AKS_ADMIN, unexpected."
fi
# RBAC/Identity (AKS)
AKS_RBAC=$(az resource show --ids $(echo "$AKS" | jq -r .id) --query "properties.enableRBAC" -o tsv)
AKS_MI=$(az resource show --ids $(echo "$AKS" | jq -r .id) --query "identity.type" -o tsv)
if [[ "$AKS_RBAC" == "True" && "$AKS_MI" == "SystemAssigned" ]]; then
  pass "AKS RBAC enabled and MI correct."
else
  fail "AKS RBAC=$AKS_RBAC or MI=$AKS_MI incorrect."
fi

# 7. Output Values Test
section "7. Output Values Correctness"
OUTPUTS=$(cat tmp.deploy.json | jq .outputs)
STG_NAME=$(echo $OUTPUTS | jq -r .storageAccountName.value)
AMLWS_NAME=$(echo $OUTPUTS | jq -r .machineLearningWorkspaceName.value)
ADF_NAME=$(echo $OUTPUTS | jq -r .dataFactoryName.value)
AKS_NAME=$(echo $OUTPUTS | jq -r .aksClusterName.value)
if [[ "$STG_NAME" == healthaistorage ]]; then
  pass "Output: storageAccountName correct."
else
  fail "Output: storageAccountName wrong ($STG_NAME)"
fi
if [[ "$AMLWS_NAME" == "healthai-mlws" ]]; then
  pass "Output: machineLearningWorkspaceName correct."
else
  fail "Output: machineLearningWorkspaceName wrong ($AMLWS_NAME)"
fi
if [[ "$ADF_NAME" == "healthai-adf" ]]; then
  pass "Output: dataFactoryName correct."
else
  fail "Output: dataFactoryName wrong ($ADF_NAME)"
fi
if [[ "$AKS_NAME" == "healthai-aks" ]]; then
  pass "Output: aksClusterName correct."
else
  fail "Output: aksClusterName wrong ($AKS_NAME)"
fi

# 8. Negative Test: Blank SSH Key Fails Validation
section "8. Parameter Edge Case: SSH Public Key Empty (Should Fail)"
if validate_deploy "failtest" "$SSH_KEY_INVALID"; then
  echo 'WARNING: Validation succeeded with blank sshPublicKey—but this should be prevented by parameter definition.'
  fail "Deployment should fail when sshPublicKey is blank, Bicep should enforce minLength."
else
  pass "Validation fails as expected with blank sshPublicKey (requires Bicep template minLength enforcement)."
fi

# 9. Edge Test: Long Name Prefix (Resource Name Construction)
section "9. Parameter Edge Case: Exceptionally Long Name Prefix"
if validate_deploy "$LONG_PREFIX" "$SSH_KEY_VALID"; then
  pass "Validation with long namePrefix succeeded."
else
  fail "Validation must not fail just because of long namePrefix (should follow Azure resource naming rules)."
fi

# 10. Parameter Edge Case: Invalid Name Prefix (Illegal Characters)"
section "10. Parameter Validation: Invalid Characters in Name Prefix"
if validate_deploy "$INVALID_PREFIX" "$SSH_KEY_VALID"; then
  echo "WARNING: Validation succeeded with invalid characters in prefix. Bicep should enforce allowed regex."
  fail "Resource namePrefix with invalid chars should be restricted by allowed() or regex pattern in Bicep param definition."
else
  pass "Validation with invalid prefix fails as expected."
fi

echo "All runtime and parameterization tests have run. Manual review of Azure resources may be performed for additional validation."