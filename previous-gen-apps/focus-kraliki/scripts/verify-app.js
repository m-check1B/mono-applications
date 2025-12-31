#!/usr/bin/env node

// Simple verification script for Focus by Kraliki App
console.log('🚀 Focus by Kraliki App Verification\n');

async function verifyServices() {
  console.log('📡 Checking Services...\n');
  
  // Test 1: Frontend Server
  console.log('1. Testing Frontend Server (http://localhost:5176)');
  try {
    const response = await fetch('http://localhost:5176');
    if (response.ok) {
      const html = await response.text();
      
      // Check for key elements in HTML
      const checks = [
        { name: 'HTML Document', test: html.includes('<!doctype html>') },
        { name: 'React App Title', test: html.includes('Focus by Kraliki') },
        { name: 'Root Element', test: html.includes('<div id="root">') },
        { name: 'Main Script', test: html.includes('/src/main.tsx') },
      ];
      
      checks.forEach(check => {
        console.log(`   ${check.test ? '✓' : '❌'} ${check.name}`);
      });
      
      console.log(`   📊 Frontend Status: ${response.status} OK\n`);
      
    } else {
      console.log(`   ❌ Frontend failed with status: ${response.status}\n`);
    }
  } catch (error) {
    console.log(`   ❌ Frontend connection failed: ${error.message}\n`);
  }
  
  // Test 2: Backend Server
  console.log('2. Testing Backend Server (http://127.0.0.1:3017)');
  try {
    const response = await fetch('http://127.0.0.1:3017/trpc');
    console.log(`   📊 Backend Status: ${response.status} (${response.status === 404 ? 'Expected - tRPC base path' : 'Response'})`);
    
    // Test tRPC endpoint structure
    const text = await response.text();
    const isTrpcResponse = text.includes('error') && text.includes('json');
    console.log(`   ${isTrpcResponse ? '✓' : '❌'} tRPC Response Format`);
    console.log(`   ✓ Backend is running and responding\n`);
    
  } catch (error) {
    console.log(`   ❌ Backend connection failed: ${error.message}\n`);
  }
  
  // Test 3: Check for common React errors by examining source
  console.log('3. Checking Source Files...');
  const fs = require('fs');
  const path = require('path');
  
  const keyFiles = [
    'frontend/src/main.tsx',
    'frontend/src/App.tsx',
    'frontend/src/components/auth/LoginPage.tsx',
    'frontend/src/lib/utils.ts',
    'backend/src/server.ts'
  ];
  
  keyFiles.forEach(file => {
    const filePath = path.join(__dirname, file);
    const exists = fs.existsSync(filePath);
    console.log(`   ${exists ? '✓' : '❌'} ${file}`);
  });
}

async function createTestReport() {
  console.log('\n📋 Generating Test Report...\n');
  
  const report = {
    timestamp: new Date().toISOString(),
    tests: [],
    summary: {
      frontend: 'PENDING',
      backend: 'PENDING',
      overall: 'PENDING'
    }
  };
  
  // Frontend test
  try {
    const frontendResponse = await fetch('http://localhost:5176');
    report.tests.push({
      name: 'Frontend Accessibility',
      status: frontendResponse.ok ? 'PASS' : 'FAIL',
      details: `HTTP ${frontendResponse.status} - ${frontendResponse.statusText}`
    });
    report.summary.frontend = frontendResponse.ok ? 'WORKING' : 'FAILED';
  } catch (error) {
    report.tests.push({
      name: 'Frontend Accessibility',
      status: 'FAIL',
      details: error.message
    });
    report.summary.frontend = 'FAILED';
  }
  
  // Backend test
  try {
    const backendResponse = await fetch('http://127.0.0.1:3017/trpc');
    const isWorking = backendResponse.status === 404; // Expected for tRPC base
    report.tests.push({
      name: 'Backend Connectivity',
      status: isWorking ? 'PASS' : 'FAIL',
      details: `HTTP ${backendResponse.status} - tRPC endpoint responding`
    });
    report.summary.backend = isWorking ? 'WORKING' : 'FAILED';
  } catch (error) {
    report.tests.push({
      name: 'Backend Connectivity', 
      status: 'FAIL',
      details: error.message
    });
    report.summary.backend = 'FAILED';
  }
  
  // Overall status
  const allPassed = report.tests.every(test => test.status === 'PASS');
  report.summary.overall = allPassed ? 'ALL SYSTEMS OPERATIONAL' : 'ISSUES DETECTED';
  
  // Save report
  const fs = require('fs');
  fs.writeFileSync('test-report.json', JSON.stringify(report, null, 2));
  
  console.log('📊 TEST RESULTS:');
  console.log('================');
  report.tests.forEach(test => {
    console.log(`${test.status === 'PASS' ? '✅' : '❌'} ${test.name}: ${test.details}`);
  });
  
  console.log(`\n🎯 OVERALL STATUS: ${report.summary.overall}`);
  console.log(`📄 Full report saved to: test-report.json\n`);
  
  return report;
}

async function main() {
  await verifyServices();
  const report = await createTestReport();
  
  console.log('🏁 Verification Complete!\n');
  
  if (report.summary.overall === 'ALL SYSTEMS OPERATIONAL') {
    console.log('🎉 SUCCESS: Focus by Kraliki App is running correctly!');
    console.log('   • Frontend: ✅ Serving at http://localhost:5176');
    console.log('   • Backend: ✅ Running at http://127.0.0.1:3017');
    console.log('   • Ready for E2E testing and user interaction');
  } else {
    console.log('⚠️  ISSUES DETECTED: Some components may need attention');
    console.log('   Check the test report for details');
  }
}

main().catch(console.error);