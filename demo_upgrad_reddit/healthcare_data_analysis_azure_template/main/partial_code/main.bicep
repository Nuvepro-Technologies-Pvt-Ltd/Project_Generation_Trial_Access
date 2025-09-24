// Minimal, valid, and deployable Bicep template for Healthcare AI platform backend resources
//
// This template should provision core Azure resources: Storage Account, Azure Machine Learning Workspace, Data Factory, and AKS cluster, all parameterized for healthcare data needs with encryption and IAM best practices.
//
// =========================== PARAMETERS ===============================
@description('Location for all resources')
param location string = resourceGroup().location;
@description('Name prefix for resource names (e.g., healthai)')
param namePrefix string = 'healthai';
@description('SSH public key for AKS cluster node access. Paste your valid SSH public key.')
param sshPublicKey string;

// =========================== STORAGE ACCOUNT ===========================
// INSTRUCTION: Create an Azure Storage Account resource. Name should use the namePrefix parameter and a fixed suffix. 
// Set the location from the 'location' parameter. Configure the SKU as 'Standard_LRS', kind as 'StorageV2'.
// In properties, set accessTier to 'Hot', minimumTlsVersion to 'TLS1_2', and disable blob public access.
// Enable encryption for blob and file services with Microsoft-managed keys.
// Ensure to reference all relevant parameters and security best practices.

// ======================== AZURE MACHINE LEARNING WORKSPACE =============
// INSTRUCTION: Create an Azure Machine Learning Workspace resource. Name should use namePrefix with an appropriate suffix.
// Set its location and sku (e.g., 'Basic').
// For properties: Set a friendlyName, assign the Storage Account from above (use the storage resource's id), disable public network access.
// This workspace should be connected securely to the storage account.

// ======================== AZURE DATA FACTORY ===========================
// INSTRUCTION: Provision an Azure Data Factory resource, named by combining namePrefix and a suitable suffix.
// Use the specified location, assign a SystemAssigned managed identity for it.
// No other special properties are required, but follow security best practices.

// ======================== AZURE KUBERNETES SERVICE =====================
// INSTRUCTION: Deploy an AKS (Azure Kubernetes Service) managed cluster resource.
// Name should combine namePrefix and an appropriate suffix. Use the 'location' parameter.
// Under properties:
//   - Create one agent pool: name 'agentpool', count 1, vmSize 'Standard_DS2_v2', mode 'System'.
//   - Set dnsPrefix using the namePrefix param.
//   - Configure linuxProfile: adminUsername as 'azureuser' and assign the sshPublicKey parameter for SSH access.
//   - Configure networkProfile: networkPlugin 'azure'.
//   - Assign a SystemAssigned managed identity.
//   - Enable RBAC for access control.

// =========================== OUTPUTS ===================================
// INSTRUCTION: At the end, create output variables that return the name of each resource created above: Storage Account, Machine Learning Workspace, Data Factory, and AKS Cluster.
// Output the .name property of each resource.

// ================== SAMPLE DEPLOYMENT COMMAND ==========================
// Save as 'main.bicep' and use Azure CLI to deploy, passing in your resource group, desired prefix, location, and your SSH public key.
// az deployment group create //   --resource-group <your-resource-group> //   --template-file main.bicep //   --parameters namePrefix=<prefix> location=<location> sshPublicKey="$(cat ~/.ssh/id_rsa.pub)"
// Replace placeholder values as needed.