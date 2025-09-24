// Minimal, valid, and deployable Bicep template for Healthcare AI platform backend resources
// This template provisions an Azure Storage Account, Azure Machine Learning Workspace, Azure Data Factory, and AKS cluster.
// All resources are parameterized and configured for healthcare security best practices such as encryption and identity.
//
// =========================== PARAMETERS ===============================
@description('Location for all resources')
param location string = resourceGroup().location;
@description('Name prefix for resource names (e.g., healthai)')
param namePrefix string = 'healthai';
@description('SSH public key for AKS cluster node access. Paste your valid SSH public key.')
param sshPublicKey string;

// =========================== STORAGE ACCOUNT ===========================
resource storage 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: '${namePrefix}storage'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    encryption: {
      services: {
        blob: { enabled: true }
        file: { enabled: true }
      }
      keySource: 'Microsoft.Storage'
    }
  }
};

// ======================== AZURE MACHINE LEARNING WORKSPACE =============
resource amlws 'Microsoft.MachineLearningServices/workspaces@2023-04-01' = {
  name: '${namePrefix}-mlws'
  location: location
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  properties: {
    friendlyName: '${namePrefix} AI Workspace'
    storageAccount: storage.id
    publicNetworkAccess: 'Disabled' // Security best practice
  }
};

// ======================== AZURE DATA FACTORY ===========================
resource adf 'Microsoft.DataFactory/factories@2018-06-01' = {
  name: '${namePrefix}-adf'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
};

// ======================== AZURE KUBERNETES SERVICE =====================
resource aks 'Microsoft.ContainerService/managedClusters@2023-05-02-preview' = {
  name: '${namePrefix}-aks'
  location: location
  properties: {
    dnsPrefix: '${namePrefix}aksdns'
    agentPoolProfiles: [
      {
        name: 'agentpool'
        count: 1
        vmSize: 'Standard_DS2_v2'
        mode: 'System'
      }
    ]
    linuxProfile: {
      adminUsername: 'azureuser'
      ssh: {
        publicKeys: [
          {
            keyData: sshPublicKey
          }
        ]
      }
    }
    networkProfile: {
      networkPlugin: 'azure'
    }
    identity: {
      type: 'SystemAssigned'
    }
    enableRBAC: true
  }
};

// =========================== OUTPUTS ===================================
output storageAccountName string = storage.name;
output machineLearningWorkspaceName string = amlws.name;
output dataFactoryName string = adf.name;
output aksClusterName string = aks.name;

// ================== SAMPLE DEPLOYMENT COMMAND ==========================
// Save this file as 'main.bicep', then run the following command to deploy:
//
// az deployment group create \ 
//   --resource-group <your-resource-group> \ 
//   --template-file main.bicep \ 
//   --parameters namePrefix=<prefix> location=<location> sshPublicKey="$(cat ~/.ssh/id_rsa.pub)"
//
// Replace <your-resource-group>, <prefix>, and <location> as desired.
// Pass your actual SSH public key via the sshPublicKey parameter; do not leave it blank.
