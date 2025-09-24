const path = require('path');
const { validate, deploy, getOutput, getResource } = require('@azure/bicep-test');
// @azure/bicep-test: A hypothetical Node.js utility for Bicep template unit/integration tests
const { mocked } = require('jest-mock');

// Comprehensive Jest-based test suite for Bicep template validation and deployment logic
// These are framework-agnostic test principles, adapted for Infrastructure-as-Code (IaC) using JavaScript and Jest
// 'bicep-test' is a stand-in library illustrating Bicep test conventions—replace with actual toolchain in your CI

const templatePath = path.resolve(__dirname, '../main.bicep');


describe('Healthcare AI Azure Resource Blueprint Bicep Template', () => {
  describe('Template Syntax & Schema', () => {
    test('validate_template_syntax_and_schema_shouldPass', async () => {
      // Arrange: Only test that base template compiles and is deployable
      const result = await validate(templatePath);
      // Assert: Template passes Bicep linter validation
      expect(result.isValid).toBe(true);
      expect(result.errors).toEqual([]);
    });
  });

  describe('Parameter Validation', () => {
    test('parameters_defaultValues_shouldApplyOnOmission', async () => {
      // Arrange: Do not provide optional parameters
      const result = await validate(templatePath);
      // Assert: Default parameters should be used
      expect(result.parameters.location).toBeDefined();
      expect(result.parameters.namePrefix).toBe('healthai');
    });
    test('parameters_nullSshPublicKey_shouldFailDeployment', async () => {
      // Arrange: sshPublicKey is required and may not be null or empty
      const params = { sshPublicKey: '' };
      // Act
      const result = await validate(templatePath, params);
      // Assert: Should fail validation
      expect(result.isValid).toBe(false);
      expect(result.errors).toContainEqual(
        expect.objectContaining({ message: expect.stringContaining('sshPublicKey') })
      );
    });
    test('parameters_invalidLocation_shouldFailDeployment', async () => {
      // Arrange: Invalid Azure region
      const params = {
        sshPublicKey: 'ssh-rsa AAAA....',
        location: 'invalid-region',
        namePrefix: 'testproject'
      };
      const result = await validate(templatePath, params);
      // Assert
      expect(result.isValid).toBe(false);
      expect(result.errors).toContainEqual(
        expect.objectContaining({ message: expect.stringContaining('location') })
      );
    });
    test('parameters_validInputs_shouldPassDeployment', async () => {
      // Arrange
      const params = {
        sshPublicKey: 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD2...',
        location: 'eastus2',
        namePrefix: 'testai'
      };
      // Act
      const result = await validate(templatePath, params);
      // Assert
      expect(result.isValid).toBe(true);
    });
  });

  describe('Resource Definitions', () => {
    let output, deployment;
    beforeAll(async () => {
      // Use valid, unique parameter values
      deployment = await deploy(templatePath, {
        sshPublicKey: 'ssh-rsa AAAAB3fakeKeyData==',
        location: 'eastus',
        namePrefix: 'testhak'
      });
      output = deployment.outputs;
    });
    test('resources_provisioned_storageAccount_schemaAndValues_shouldBeCorrect', async () => {
      const storage = await getResource(deployment, 'Microsoft.Storage/storageAccounts', 'testhakstorage');
      expect(storage).toBeDefined();
      expect(storage.location).toBe('eastus');
      expect(storage.sku.name).toBe('Standard_LRS');
      expect(storage.kind).toBe('StorageV2');
      expect(storage.properties.accessTier).toBe('Hot');
      expect(storage.properties.minimumTlsVersion).toBe('TLS1_2');
    });
    test('resources_provisioned_amlws_schemaAndReferences_shouldBeCorrect', async () => {
      const amlws = await getResource(deployment, 'Microsoft.MachineLearningServices/workspaces', 'testhak-mlws');
      expect(amlws).toBeDefined();
      expect(amlws.sku.name).toBe('Basic');
      expect(amlws.properties.storageAccount).toContain('testhakstorage'); // Reference to storage account
      expect(amlws.properties.publicNetworkAccess).toBe('Disabled');
    });
    test('resources_provisioned_adf_schemaAndIdentity_shouldBeCorrect', async () => {
      const adf = await getResource(deployment, 'Microsoft.DataFactory/factories', 'testhak-adf');
      expect(adf).toBeDefined();
      expect(adf.identity.type).toBe('SystemAssigned');
    });
    test('resources_provisioned_aks_propertiesAndNetworking_shouldBeCorrect', async () => {
      const aks = await getResource(deployment, 'Microsoft.ContainerService/managedClusters', 'testhak-aks');
      expect(aks).toBeDefined();
      expect(aks.properties.dnsPrefix).toBe('testhakaksdns');
      expect(aks.properties.agentPoolProfiles[0].count).toBe(1);
      expect(aks.properties.agentPoolProfiles[0].vmSize).toBe('Standard_DS2_v2');
      expect(aks.properties.linuxProfile.adminUsername).toBe('azureuser');
      expect(aks.properties.linuxProfile.ssh.publicKeys[0].keyData).toBe('ssh-rsa AAAAB3fakeKeyData==');
      expect(aks.properties.networkProfile.networkPlugin).toBe('azure');
    });
  });

  describe('Output Verification', () => {
    test('outputs_shouldExposeResourceNamesCorrectly', async () => {
      // Arrange
      const params = {
        sshPublicKey: 'ssh-rsa AAAAB3prodKeyData==',
        location: 'westeurope',
        namePrefix: 'hiqa'
      };
      // Act
      const deployment = await deploy(templatePath, params);
      const outputs = deployment.outputs;
      // Assert
      expect(outputs.storageAccountName).toBe('hiqastorage');
      expect(outputs.machineLearningWorkspaceName).toBe('hiqa-mlws');
      expect(outputs.dataFactoryName).toBe('hiqa-adf');
      expect(outputs.aksClusterName).toBe('hiqa-aks');
    });
  });

  describe('Security & Best Practices', () => {
    test('amlws_publicNetworkAccess_shouldBeDisabledForSecurity', async () => {
      // Arrange
      const params = {
        sshPublicKey: 'ssh-rsa AAAAB3prodKeyData==',
        location: 'centralus',
        namePrefix: 'hiprod'
      };
      const deployment = await deploy(templatePath, params);
      const amlws = await getResource(deployment, 'Microsoft.MachineLearningServices/workspaces', 'hiprod-mlws');
      // Assert
      expect(amlws.properties.publicNetworkAccess).toBe('Disabled');
    });
    test('aks_sshPublicKey_shouldNotAllowBlankOrInvalidKey', async () => {
      // Arrange: Intentionally supply a blank SSH key
      const params = {
        sshPublicKey: '',
        location: 'eastus',
        namePrefix: 'hiprod'
      };
      const result = await validate(templatePath, params);
      // Assert: Bicep validation should fail
      expect(result.isValid).toBe(false);
      expect(result.errors).toContainEqual(
        expect.objectContaining({ message: expect.stringContaining('sshPublicKey') })
      );
    });
  });

  describe('Edge Conditions', () => {
    test('namePrefix_boundaryLengthAtMaxAllowed_shouldSucceed', async () => {
      // Arrange: Azure resource name max length for storage account is 24 chars
      const prefix = 'abcdefghijklmno123456'; // 21 chars + 'storage' = 28 > allowed for storage, but test boundary
      const params = {
        sshPublicKey: 'ssh-rsa AAAAB3bigKeyData==',
        location: 'eastus',
        namePrefix: prefix
      };
      const result = await validate(templatePath, params);
      // Assert: Should fail validation due to Azure resource length limits
      expect(result.isValid).toBe(false);
      expect(result.errors).toContainEqual(
        expect.objectContaining({ message: expect.stringMatching(/name.*length/i) })
      );
    });
  });

  // (Optional) Additional parameterized or data-driven tests can be added for different Azure regions, SKUs, node counts, etc.
  // (Optional) Performance/load test hooks for template deployment duration can be integrated via CI pipeline metrics.
});

// Note: Mocks and test doubles would be used if these functions interacted with real Azure infrastructure—these test patterns allow CI safety without incurring actual cloud costs, while verifying Bicep template logic and outputs.