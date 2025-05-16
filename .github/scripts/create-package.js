#!/usr/bin/env node

/**
 * Script to create a package for release
 * Creates a zip archive with all SSM documents and supporting files
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Get package info
const packageJsonPath = path.join(process.cwd(), 'package.json');
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
const version = packageJson.version;

// Create dist directory if it doesn't exist
const distDir = path.join(process.cwd(), 'dist');
if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir);
}

// Define zip filename
const zipFile = path.join(distDir, `aws-ssm-automation-scripts-${version}.zip`);

// Clean up any existing package with the same name
if (fs.existsSync(zipFile)) {
  fs.unlinkSync(zipFile);
}

// Create a manifest file with version info
const manifestPath = path.join(process.cwd(), 'MANIFEST.json');
fs.writeFileSync(
  manifestPath,
  JSON.stringify(
    {
      name: packageJson.name,
      version: version,
      description: packageJson.description,
      author: packageJson.author,
      license: packageJson.license,
      createdAt: new Date().toISOString(),
      scripts: fs.readdirSync(process.cwd())
        .filter(file => file.endsWith('.yaml'))
        .map(file => ({
          name: file,
          description: extractDescription(path.join(process.cwd(), file))
        }))
    },
    null,
    2
  )
);

// Create zip package with scripts, shared modules, README, LICENSE, and MANIFEST
try {
  // Get all YAML files
  const yamlFiles = fs.readdirSync(process.cwd())
    .filter(file => file.endsWith('.yaml'))
    .map(file => file);
  
  // Build zip command
  const filesToZip = [
    ...yamlFiles,
    'README.md',
    'LICENSE',
    'MANIFEST.json',
    'shared'
  ].join(' ');
  
  // Create zip archive
  execSync(`zip -r "${zipFile}" ${filesToZip}`, { stdio: 'inherit' });
  console.log(`Package created: ${zipFile}`);
  
  // Clean up manifest file
  fs.unlinkSync(manifestPath);
} catch (error) {
  console.error('Error creating package:', error.message);
  process.exit(1);
}

// Helper function to extract description from YAML file
function extractDescription(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const match = content.match(/description:\s*(.+)/);
    return match ? match[1].trim() : 'No description available';
  } catch (error) {
    return 'No description available';
  }
}