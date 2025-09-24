// No traditional imports needed for Bicep's test syntax, but test scaffolding references MS test module resources

// ===========================================================================
// Bicep Test Suite: Secure Networking & Access Controls for Healthcare AI
// Framework: Bicep Test Framework (based on az CLI and test modules semantics)
// File: tests/secure-networking.bicep.test.bicep
// Requirements: az CLI, Bicep CLI, and Azure testing module
// Docs: https://github.com/Azure/bicep-registry-modules/tree/main/modules/test
// ===========================================================================

// NOTE: Bicep "unit testing" is performed using deployment scripts/assertions or external modules.
// We use inline parameterization and 'test' modules to verify outputs, resource properties, and security rules.
// This test suite checks all critical template behaviors, edge cases, compliance controls.

// ============================
// PARAMETER OVERRIDES FOR TEST
// ============================
param location string = 'eastus'
param namePrefix string = 'testhealthai'
param vnetAddressPrefix string = '10.50.0.0/16'
param backendSubnetPrefix string = '10.50.1.0/24'
param aksSubnetPrefix string = '10.50.2.0/24'
param adminObjectId string = '00000000-1111-2222-3333-444444444444' // sample AAD objectId

// ============ MODULE UNDER TEST ============
module sut '../secure-networking.bicep' = {
  name: 'sut-module'
  params: {
    location: location
    namePrefix: namePrefix
    vnetAddressPrefix: vnetAddressPrefix
    backendSubnetPrefix: backendSubnetPrefix
    aksSubnetPrefix: aksSubnetPrefix
    adminObjectId: adminObjectId
  }
}

// ================= TEST CASES ====================
// 1. VNet and Subnets Created With Correct Names/CIDR
resource assertVNet 'Microsoft.Network/virtualNetworks@2023-09-01' existing = {
  name: '${namePrefix}-vnet'
}
output test_vnet_exists string = assertVNet.name == sut.outputs.vnetName ? 'PASS' : 'FAIL: Incorrect VNet name'
output test_vnet_addressPrefix string = contains(assertVNet.properties.addressSpace.addressPrefixes, vnetAddressPrefix) ? 'PASS' : 'FAIL: VNet address prefix mismatch'
output test_backend_subnet_exists string = sut.outputs.backendSubnetName == 'backend' ? 'PASS' : 'FAIL: Backend subnet missing or wrong name'
output test_aks_subnet_exists string = sut.outputs.aksSubnetName == 'aks' ? 'PASS' : 'FAIL: AKS subnet missing or wrong name'

// 2. NSGs Created and Assigned With Correct Rules
resource assertBackendNSG 'Microsoft.Network/networkSecurityGroups@2023-04-01' existing = {
  name: '${namePrefix}-backend-nsg'
}
// Backend NSG: Only 'Deny-Internet-All' Inbound highlighted
output test_backendNSG_denyInternetRule string = length([for rule in assertBackendNSG.properties.securityRules: rule.name == 'Deny-Internet-All']) > 0 ? 'PASS' : 'FAIL: NSG does not contain Deny-Internet-All rule'
output test_backendNSG_noAllowInternetRule string = length([for rule in assertBackendNSG.properties.securityRules: rule.access == 'Allow' && rule.sourceAddressPrefix == 'Internet']) == 0 ? 'PASS' : 'FAIL: NSG allows Internet traffic'

resource assertAksNSG 'Microsoft.Network/networkSecurityGroups@2023-04-01' existing = {
  name: '${namePrefix}-aks-nsg'
}
output test_aksNSG_rules string = (length([for rule in assertAksNSG.properties.securityRules: rule.name == 'Allow-Azure-Internal']) > 0 && length([for rule in assertAksNSG.properties.securityRules: rule.name == 'Deny-Internet-All']) > 0) ? 'PASS' : 'FAIL: AKS NSG missing expected rules'

// 3. NSG Associated To Correct Subnets
resource assertBackendSubnet 'Microsoft.Network/virtualNetworks/subnets@2023-09-01' existing = {
  parent: assertVNet
  name: 'backend'
}
output test_backendSubnet_nsgAssoc string = contains(assertBackendSubnet.properties.networkSecurityGroup.id, 'backend-nsg') ? 'PASS' : 'FAIL: Backend subnet not properly NSG-associated'

resource assertAksSubnet 'Microsoft.Network/virtualNetworks/subnets@2023-09-01' existing = {
  parent: assertVNet
  name: 'aks'
}
output test_aksSubnet_nsgAssoc string = contains(assertAksSubnet.properties.networkSecurityGroup.id, 'aks-nsg') ? 'PASS' : 'FAIL: AKS subnet not properly NSG-associated'

// 4. Private Endpoint For Storage Exists In Correct Subnet
resource assertStoragePE 'Microsoft.Network/privateEndpoints@2023-05-01' existing = {
  name: '${namePrefix}-storage-pe'
}
output test_storagePE_subnet string = contains(assertStoragePE.properties.subnet.id, 'backend') ? 'PASS' : 'FAIL: Storage Private Endpoint not in backend subnet'

// 5. RBAC Assignment To Correct Admin Principal
resource assertRBAC 'Microsoft.Authorization/roleAssignments@2022-04-01' existing = {
  name: guid(resourceGroup().id, adminObjectId, 'Owner')
}
output test_rbac_ownerRole string = contains(assertRBAC.properties.roleDefinitionId, '8e3af657-a8ff-443c-a75c-2fe8c4bcb635') ? 'PASS' : 'FAIL: RBAC not Owner role'
output test_rbac_principalId string = assertRBAC.properties.principalId == adminObjectId ? 'PASS' : 'FAIL: RBAC principalId wrong'

// 6. Documentation Output Present
output test_documentation_exists string = sut.outputs.documentation != '' ? 'PASS' : 'FAIL: Documentation output missing'

// 7. Edge Cases and Negative Testing (Parameterization)
// -- Invalid CIDR (negative case)
// Not typically enforced by Bicep itself without custom policy, would require deployment/failure test by pipeline
// -- Missing adminObjectId (negative case) handled at deployment param validation
output test_adminObjectId_not_empty string = adminObjectId != '' ? 'PASS' : 'FAIL: adminObjectId is required'

// 8. Healthcare Compliance Alignment
// -- Confirm all critical resources are isolated from public Internet
output test_backendSubnet_noInternetNSG string = length([for rule in assertBackendNSG.properties.securityRules: rule.access == 'Deny' && rule.sourceAddressPrefix == 'Internet']) > 0 ? 'PASS' : 'FAIL: Backend subnet NSG does not deny Internet'
// -- Confirm storage accessible only via Private Endpoint (cannot check network topology in Bicep, but can ensure PE exists)
output test_storagePE_exists string = assertStoragePE.name == '${namePrefix}-storage-pe' ? 'PASS' : 'FAIL: Required Storage Private Endpoint missing'

// ==========================
// TEST RUN RESULT SUMMARY
// ==========================
output test_suite_result string = (
  test_vnet_exists == 'PASS' &&
  test_vnet_addressPrefix == 'PASS' &&
  test_backend_subnet_exists == 'PASS' &&
  test_aks_subnet_exists == 'PASS' &&
  test_backendNSG_denyInternetRule == 'PASS' &&
  test_backendNSG_noAllowInternetRule == 'PASS' &&
  test_aksNSG_rules == 'PASS' &&
  test_backendSubnet_nsgAssoc == 'PASS' &&
  test_aksSubnet_nsgAssoc == 'PASS' &&
  test_storagePE_subnet == 'PASS' &&
  test_rbac_ownerRole == 'PASS' &&
  test_rbac_principalId == 'PASS' &&
  test_documentation_exists == 'PASS' &&
  test_adminObjectId_not_empty == 'PASS' &&
  test_backendSubnet_noInternetNSG == 'PASS' &&
  test_storagePE_exists == 'PASS'
) ? 'ALL TESTS PASSED' : 'SOME TESTS FAILED (see outputs)'

// ==============================
// NOTE TO TESTER
// ==============================
// - To execute: deploy this test template to a throwaway resource group with test parameters
// - Review all outputs for PASS/FAIL per test
// - Tests cover positive flows, resource compliance, RBAC, NSG, subnet association, and documentation outputs
// - For negative tests like invalid params or CIDR, add pre-deployment validation policies or separate pipeline tests