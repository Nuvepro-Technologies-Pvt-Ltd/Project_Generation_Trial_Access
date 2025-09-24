// Bicep template: Secure Networking & Access Controls for Healthcare AI Platform
// Applies network isolation, private endpoints, NSGs, and RBAC for core resources (Storage, AML, AKS, Data Factory)
// All critical controls are documented for healthcare compliance alignment

@description('Azure location for all resources')
param location string = resourceGroup().location
@description('Name prefix for resource identifiers')
param namePrefix string = 'healthai'
@description('Virtual Network CIDR (main network segment)')
param vnetAddressPrefix string = '10.10.0.0/16'
@description('Subnet CIDR for backend resources')
param backendSubnetPrefix string = '10.10.1.0/24'
@description('Subnet CIDR for AKS nodes')
param aksSubnetPrefix string = '10.10.2.0/24'
@description('Admin AAD Object ID for least-privilege RBAC')
param adminObjectId string

// ================== VIRTUAL NETWORK & SUBNETS =======================
// Define a virtual network resource with address space and multiple subnets
// - Create a 'backend' subnet with the backendSubnetPrefix
// - Create an 'aks' subnet with the aksSubnetPrefix
// HINT: Use Microsoft.Network/virtualNetworks resource

// =================== NETWORK SECURITY GROUPS (NSG) ===================
// Define NSG resources for backend and aks subnets
// - For backendNSG, deny inbound traffic from Internet
// - For aksNSG, allow VirtualNetwork inbound, deny Internet inbound
// HINT: Use Microsoft.Network/networkSecurityGroups resource

// NSG Association to subnets
// Associate backendNSG to the backend subnet and aksNSG to the aks subnet
// HINT: Use Microsoft.Network/virtualNetworks/subnets/networkSecurityGroups resource and reference the correct subnet indexes

// ============ PRIVATE ENDPOINT: STORAGE (Restrict to VNet Only) ===========
// Reference an existing storage account resource
// Create a private endpoint resource for the storage account (for 'blob')
// - Attach to the backend subnet
// - Setup privateLinkServiceConnections for 'blob'
// NOTE: Private DNS Zone config is required for actual access but is omitted here

// ============= RBAC: LEAST PRIVILEGE, ADMIN TO ALL RESOURCES ===========
// Assign the Owner role (or other appropriate role) to adminObjectId scoped to the resource group
// HINT: Use Microsoft.Authorization/roleAssignments resource and generate 'name' with guid(), pass in principalId, and use the correct roleDefinitionId for Owner
// - For full least-privilege, add additional role assignments as needed, scoped to particular resources

// =================== DOCUMENTATION (DESCRIPTIVE OUTPUTS) =================
// Output important resource names and documentation for compliance review
// - vnetName, backendSubnetName, aksSubnetName, backendNSGName, aksNSGName, adminRBACScope
// - documentation: Describe how these settings ensure network isolation and compliance for healthcare

// ================== SAMPLE DEPLOYMENT COMMAND =============================
// Provide sample deployment command
// This is a comment section to instruct how to deploy the template using Azure CLI
// Mention how to pass namePrefix and adminObjectId parameters
