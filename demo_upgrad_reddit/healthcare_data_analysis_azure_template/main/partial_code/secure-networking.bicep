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
// TODO: Create a Virtual Network resource named with the prefix provided by namePrefix and apply the vnetAddressPrefix for the address space.
//       Define two subnets within the virtual network: one named 'backend' using backendSubnetPrefix and another named 'aks' using aksSubnetPrefix.
//       Use location for deployment region. Document the healthcare compliance requirements for subnet segmentation and isolation.
// Example variables to use: namePrefix, location, vnetAddressPrefix, backendSubnetPrefix, aksSubnetPrefix.

// =================== NETWORK SECURITY GROUPS (NSG) ===================
// TODO: Create a Network Security Group (NSG) for the backend subnet named with '${namePrefix}-backend-nsg'.
//       Add an inbound security rule to deny all traffic from 'Internet' (priority 100), and, as needed, permit inbound Azure service/monitoring traffic.
// TODO: Create a similar NSG for the AKS subnet named '${namePrefix}-aks-nsg'.
//       Add inbound security rules to allow intra-virtual network traffic (priority 100) and deny all from Internet (priority 200).
//       Document all rules and their alignment with healthcare isolation requirements.
// Example variable: namePrefix, location

// TODO: Associate each NSG with its corresponding subnet (backendNSG â backend subnet, aksNSG â aks subnet).
//       Use references between resources, and ensure correct parent/child relationships for NSG association.

// ============ PRIVATE ENDPOINT: STORAGE (Restrict to VNet Only) ===========
// TODO: Reference an existing storage account named '${namePrefix}storage'.
//       Create a Private Endpoint for the storage account within the backend subnet (
//            use vnet.properties.subnets[0].id for subnet reference).
//       The private endpoint should connect to the 'blob' group of the storage account.
//       Document the compliance rationale for using private endpoints.
// Note: Private DNS Zone association is required for endpoint resolutionâadd as needed for a full solution.
// Example variables: storage.id, vnet.properties.subnets[0].id, namePrefix, location

// ============= RBAC: LEAST PRIVILEGE, ADMIN TO ALL RESOURCES ===========
// TODO: Assign an Owner role assignment at the resource group level to the specified AAD Object ID (adminObjectId).
//       Use the built-in Owner role definition id ('8e3af657-a8ff-443c-a75c-2fe8c4bcb635') and use guid for deterministic name.
//       Document the RBAC assignment and suggest creating additional least-privilege role assignments as needed per resource.
// Example variables: adminObjectId, resourceGroup().id

// =================== DOCUMENTATION (DESCRIPTIVE OUTPUTS) =================
// TODO: Output the names of created resources for documentation purposes: vnetName, backendSubnetName, aksSubnetName,
//       backendNSGName, aksNSGName, adminRBACScope.
//       In documentation output, summarize the security posture: network isolation, NSGs, private endpoints, and RBAC
//       as they relate to healthcare compliance (only accessible from authorized networks/principals, public access blocked).

// ================== SAMPLE DEPLOYMENT COMMAND =============================
// TODO: Add instructions to deploy the template using the Azure CLI (az deployment group create), indicating required parameters such as resource group, namePrefix, and adminObjectId.
//       Remind the user to replace placeholders as appropriate for their environment.
