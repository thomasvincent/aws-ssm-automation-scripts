#!/usr/bin/env node

/**
 * Script to bump version in package.json
 * Usage: node version-bump.js [major|minor|patch]
 */

const fs = require('fs');
const path = require('path');

// Get package.json path
const packageJsonPath = path.join(process.cwd(), 'package.json');

// Read package.json
let packageJson;
try {
  packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
} catch (error) {
  console.error('Error reading package.json:', error.message);
  process.exit(1);
}

// Get current version
const currentVersion = packageJson.version;
const versionParts = currentVersion.split('.').map(Number);

// Get bump type from command line argument
const bumpType = process.argv[2] || 'patch';

// Bump version based on type
switch (bumpType.toLowerCase()) {
  case 'major':
    versionParts[0] += 1;
    versionParts[1] = 0;
    versionParts[2] = 0;
    break;
  case 'minor':
    versionParts[1] += 1;
    versionParts[2] = 0;
    break;
  case 'patch':
  default:
    versionParts[2] += 1;
    break;
}

// Update version in package.json
const newVersion = versionParts.join('.');
packageJson.version = newVersion;

// Write updated package.json
fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2) + '\n');

console.log(`Version bumped from ${currentVersion} to ${newVersion}`);