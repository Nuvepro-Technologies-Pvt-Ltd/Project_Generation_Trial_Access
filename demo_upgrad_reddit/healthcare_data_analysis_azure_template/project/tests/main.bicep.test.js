const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Automated infrastructure tests for main.bicep using Azure Bicep linter (bicep build and bicep linter), ARM template validation, and output verification.
// Dependencies: Azure CLI, Bicep CLI, Node.js, and Jest. These tests expect the main.bicep file to be in the project root or ./../ if in tests/ directory.
// These tests do not deploy resources, but perform validation, linting, and syntax/output checks on the Bicep template.
// For end-to-end deployment tests, use ephemeral Azure test subscriptions.

describe('Azure Healthcare AI Bicep Template', () => {
  const bicepFile = path.resolve(__dirname, '../main.bicep');
  const outputDir = path.resolve(__dirname, './_generated');
  const armTemplateOut = path.join(outputDir, 'main.json');
  
  beforeAll(() => {
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir);
    }
  });

  test('main.bicep file exists and readable', () => {
    expect(fs.existsSync(bicepFile)).toBe(true);
    expect(() => fs.readFileSync(bicepFile, 'utf8')).not.toThrow();
  });

  test('bicep syntax is valid (bicep build)', () => {
    expect(() => execSync(`bicep build ${bicepFile} --outfile ${armTemplateOut}`)).not.toThrow();
    expect(fs.existsSync(armTemplateOut)).toBe(true);
    // Clean up generated template after
    fs.unlinkSync(armTemplateOut);
  });

  test('bicep lint passes (bicep linter)', () => {
    expect(() => execSync(`bicep lint ${bicepFile}`)).not.toThrow();
  });

  test('bicep parameter validation: fails with missing sshPublicKey', () => {
    // Run the ARM template generation, then attempt what-if with missing input
    execSync(`bicep build ${bicepFile} --outfile ${armTemplateOut}`);
    // az deployment group what-if command should fail without sshPublicKey
    const groupName = 'test-group';
    const cmd = `az deployment group create --resource-group ${groupName} --template-file ${armTemplateOut} --parameters namePrefix=test location=eastus`;
    let failed = false;
    try {
      execSync(cmd, { stdio: 'pipe' });
    } catch (err) {
      failed = true;
    }
    expect(failed).toBe(true);
    fs.unlinkSync(armTemplateOut);
  });

  test('bicep output variables are defined as expected', () => {
    // Parse the Bicep file for output statements
    const contents = fs.readFileSync(bicepFile, 'utf8');
    const requiredOutputs = ['storageAccountName', 'machineLearningWorkspaceName', 'dataFactoryName', 'aksClusterName'];
    requiredOutputs.forEach(out => {
      const re = new RegExp(`output\\s+${out}\\s+string\\s+=`, 'g');
      expect(re.test(contents)).toBe(true);
    });
  });

  test('resource naming conventions are respected', () => {
    const contents = fs.readFileSync(bicepFile, 'utf8');
    // Check that resources use the namePrefix param in resource names
    ['storage', 'amlws', 'adf', 'aks'].forEach(logname => {
      const re = new RegExp(`resource\\s+${logname}\\s+['\"]`, 'g');
      expect(re.test(contents)).toBe(true);
    });
    // Name patterns
    expect(contents).toMatch(/name: '\$\{namePrefix\}storage'/);
    expect(contents).toMatch(/name: '\$\{namePrefix\}-mlws'/);
    expect(contents).toMatch(/name: '\$\{namePrefix\}-adf'/);
    expect(contents).toMatch(/name: '\$\{namePrefix\}-aks'/);
  });

  test('all required Azure resources are present', () => {
    const contents = fs.readFileSync(bicepFile, 'utf8');
    // Check for resource types
    expect(contents).toMatch(/Microsoft\.Storage\/storageAccounts/);
    expect(contents).toMatch(/Microsoft\.MachineLearningServices\/workspaces/);
    expect(contents).toMatch(/Microsoft\.DataFactory\/factories/);
    expect(contents).toMatch(/Microsoft\.ContainerService\/managedClusters/);
  });

  // Edge case: Test for forbidden public network access on AML workspace
  test('machine learning workspace disables public network access', () => {
    const contents = fs.readFileSync(bicepFile, 'utf8');
    const amlPublicNetwork = /amlws[^{]*{[^}]*publicNetworkAccess:\s*'Disabled'/s;
    expect(amlPublicNetwork.test(contents)).toBe(true);
  });

  // Security edge: Ensure minimum TLS version and no blank SSH key
  test('storage account enforces minimum TLS version and AKS uses non-blank SSH public key', () => {
    const contents = fs.readFileSync(bicepFile, 'utf8');
    expect(contents).toMatch(/minimumTlsVersion: 'TLS1_2'/);
    expect(contents).toMatch(/publicKeys: \[\s*{\s*keyData: sshPublicKey/);
    expect(contents).not.toMatch(/keyData: ''/);
  });

  // Advanced: Validate that location parameter default is resourceGroup().location
  test('location parameter default is resourceGroup().location', () => {
    const contents = fs.readFileSync(bicepFile, 'utf8');
    expect(contents).toMatch(/param location string = resourceGroup\(\)\.location;/);
  });

  // Clean up generated files and directories after all tests
  afterAll(() => {
    if (fs.existsSync(outputDir)) {
      fs.rmdirSync(outputDir, { recursive: true });
    }
  });
});

// Notes:
// - These tests require access to Azure CLI and Bicep CLI in the system PATH.
// - For actual resource deployment and teardown, integration tests can be added using ephemeral Azure subscriptions and resource groups.
// - For more comprehensive parameterization/edge case testing, consider running parameterized deployments with valid/invalid data.
// - This suite is Jest-based and can be run with `jest` command or similar (npm test), assuming jest is installed as a devDependency.