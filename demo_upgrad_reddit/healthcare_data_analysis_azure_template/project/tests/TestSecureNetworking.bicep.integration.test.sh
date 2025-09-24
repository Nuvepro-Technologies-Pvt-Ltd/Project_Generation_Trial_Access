#!/bin/bash
set -e
# Import: Azure CLI must be installed and logged in
# Import: jq must be installed for JSON parsing
# Import: Environment variables for Azure subscription and resource group set


# Integration test suite for 'secure-networking.bicep'
# This shell script deploys the Bicep template and validates key resources and security settings for healthcare compliance
# Execute this script from project root. Requires az CLI, jq, and appropriate permissions.

# --------- SETUP SECTION ---------
RESOURCE_GROUP="test-healthcare-rg"
LOCATION="eastus"
NAME_PREFIX="tsthealthai"
ADMIN_OBJECT_ID="<provide-test-AAD-object-id>"  # Set this to a test user/object id
TEMPLATE_FILE="secure-networking.bicep"
DEPLOYMENT_NAME="healthcare-net-secure-test-$(date +%s)"

# Clean up any existing RG for idempotency
echo "Cleaning up any pre-existing test resource group..."
az group delete --name "$RESOURCE_GROUP" --yes --no-wait || true
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"

# --------- TEST 1: Template Deployment ---------
echo "[TEST 1] Deploying Bicep template..."
az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file "$TEMPLATE_FILE" \
  --name "$DEPLOYMENT_NAME" \
  --parameters namePrefix="$NAME_PREFIX" adminObjectId="$ADMIN_OBJECT_ID"

echo "[TEST 1 PASSED] Template deployed successfully."

# --------- TEST 2: Virtual Network and Subnet Configuration ---------
echo "[TEST 2] Validating VNet and subnets..."
VNET_NAME="${NAME_PREFIX}-vnet"
VN_JSON=$(az network vnet show -g "$RESOURCE_GROUP" -n "$VNET_NAME")
BACKEND_SUBNET_NAME="backend"
AKS_SUBNET_NAME="aks"
if [ $(echo "$VN_JSON" | jq -r ".subnets[] | select(.name == \"$BACKEND_SUBNET_NAME\") | .name") != "$BACKEND_SUBNET_NAME" ]; then
  echo "[ERROR] Backend subnet not found"; exit 1; fi
if [ $(echo "$VN_JSON" | jq -r ".subnets[] | select(.name == \"$AKS_SUBNET_NAME\") | .name") != "$AKS_SUBNET_NAME" ]; then
  echo "[ERROR] AKS subnet not found"; exit 1; fi
echo "[TEST 2 PASSED] VNet and both subnets exist."

# --------- TEST 3: Network Security Groups (NSGs) and Rules ---------
echo "[TEST 3] Validating NSGs and security rules..."
BACKEND_NSG_NAME="${NAME_PREFIX}-backend-nsg"
AKS_NSG_NAME="${NAME_PREFIX}-aks-nsg"
# Check NSG exists
az network nsg show -g "$RESOURCE_GROUP" -n "$BACKEND_NSG_NAME" >/dev/null
az network nsg show -g "$RESOURCE_GROUP" -n "$AKS_NSG_NAME" >/dev/null

# Check Backend NSG denies Internet inbound
DENY_RULE=$(az network nsg rule show -g "$RESOURCE_GROUP" --nsg-name "$BACKEND_NSG_NAME" --name Deny-Internet-All)
if [ $(echo "$DENY_RULE" | jq -r '.access') != "Deny" ]; then echo "[ERROR] Backend NSG does not deny Internet inbound."; exit 1; fi
if [ $(echo "$DENY_RULE" | jq -r '.direction') != "Inbound" ]; then echo "[ERROR] Backend NSG deny rule not inbound."; exit 1; fi

# Check AKS NSG rules
AKS_ALLOW_INTERNAL_RULE=$(az network nsg rule show -g "$RESOURCE_GROUP" --nsg-name "$AKS_NSG_NAME" --name Allow-Azure-Internal)
if [ $(echo "$AKS_ALLOW_INTERNAL_RULE" | jq -r '.access') != "Allow" ]; then echo "[ERROR] AKS NSG missing allow internal rule."; exit 1; fi
AKS_DENY_RULE=$(az network nsg rule show -g "$RESOURCE_GROUP" --nsg-name "$AKS_NSG_NAME" --name Deny-Internet-All)
if [ $(echo "$AKS_DENY_RULE" | jq -r '.access') != "Deny" ]; then echo "[ERROR] AKS NSG missing deny Internet rule."; exit 1; fi
echo "[TEST 3 PASSED] NSGs and security rules validated."

# --------- TEST 4: NSG Association ---------
echo "[TEST 4] Checking subnet-NSG associations..."
BACKEND_SUBNET=$(az network vnet subnet show -g "$RESOURCE_GROUP" --vnet-name "$VNET_NAME" -n "$BACKEND_SUBNET_NAME")
if [ $(echo "$BACKEND_SUBNET" | jq -r '.networkSecurityGroup.id' | grep "$BACKEND_NSG_NAME") ]; then : ; else
  echo "[ERROR] Backend subnet not associated with backend NSG"; exit 1; fi
AKS_SUBNET=$(az network vnet subnet show -g "$RESOURCE_GROUP" --vnet-name "$VNET_NAME" -n "$AKS_SUBNET_NAME")
if [ $(echo "$AKS_SUBNET" | jq -r '.networkSecurityGroup.id' | grep "$AKS_NSG_NAME") ]; then : ; else
  echo "[ERROR] AKS subnet not associated with aks NSG"; exit 1; fi
echo "[TEST 4 PASSED] NSG associations correct."

# --------- TEST 5: Private Endpoint for Storage ---------
echo "[TEST 5] Validating private endpoint for storage account..."
STORAGE_PE_NAME="${NAME_PREFIX}-storage-pe"
az network private-endpoint show -g "$RESOURCE_GROUP" -n "$STORAGE_PE_NAME" >/dev/null
PE_SUBNET_ID=$(az network private-endpoint show -g "$RESOURCE_GROUP" -n "$STORAGE_PE_NAME" | jq -r '.subnet.id')
EXPECTED_BACKEND_SUBNET_ID=$(echo "$BACKEND_SUBNET" | jq -r '.id')
if [ "$PE_SUBNET_ID" != "$EXPECTED_BACKEND_SUBNET_ID" ]; then
  echo "[ERROR] Private endpoint not deployed into backend subnet."; exit 1; fi
echo "[TEST 5 PASSED] Private endpoint in backend subnet."

# --------- TEST 6: RBAC Role Assignment ---------
echo "[TEST 6] Checking for correct RBAC assignment..."
OWNER_ROLE="8e3af657-a8ff-443c-a75c-2fe8c4bcb635"
ASSIGNMENT=$(az role assignment list --assignee "$ADMIN_OBJECT_ID" --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP" --role Owner)
if [ $(echo "$ASSIGNMENT" | jq length) -lt 1 ]; then
  echo "[ERROR] Admin object ID is NOT assigned as Owner on the resource group."; exit 1; fi
echo "[TEST 6 PASSED] RBAC assignment valid."

# --------- TEST 7: Security Compliance Edge Cases ---------
echo "[TEST 7] Verifying no public access on backend subnet..."
BACKEND_ROUTE_TABLE=$(echo "$BACKEND_SUBNET" | jq -r '.routeTable.id')
if [ -n "$BACKEND_ROUTE_TABLE" ]; then
  ROUTES=$(az network route-table route list --route-table-name $(basename "$BACKEND_ROUTE_TABLE") -g "$RESOURCE_GROUP")
  if echo "$ROUTES" | grep -q '0.0.0.0/0'; then
    echo "[ERROR] Backend subnet has default route to Internet."; exit 1;
  fi
fi
echo "[TEST 7 PASSED] No public Internet route on backend subnet."

# [OPTIONAL] You may expand for additional negative test scenarios (e.g. attempt to deploy VM in backend subnet with public IP and verify failure)

# --------- TEARDOWN SECTION (optional for CI/CD) ---------
# Uncomment below lines for automatic cleanup
echo "Cleaning up test resource group..."
az group delete --name "$RESOURCE_GROUP" --yes --no-wait

echo "All tests PASSED. Secure networking and compliance controls validated."

# END OF TESTS

# Notes:
# - Replace <provide-test-AAD-object-id> with a user/service principal in test context.
# - To thoroughly test negative cases and other edge compliance (e.g. deny public IP on backend, escalate privileges attempt), further scripts or policy tests can be added.
# - Script designed to be idempotent and cleanup after test run.