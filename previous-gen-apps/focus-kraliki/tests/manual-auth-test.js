#!/usr/bin/env node

/**
 * Manual Authentication Test Script
 *
 * This script demonstrates manual testing of user registration and login
 * functionality using curl commands to verify the Focus by Kraliki authentication system.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const BASE_URL = 'http://127.0.0.1:3018';
const API_URL = `${BASE_URL}/trpc`;

// Test data
const testUser = {
  email: `manualtest${Date.now()}@example.com`,
  password: 'SecurePassword123!',
  name: 'Manual Test User'
};

console.log('🧪 Focus by Kraliki Authentication Manual Test');
console.log('=====================================\n');

// Utility function to run curl commands
function runCurlCommand(command, description) {
  try {
    console.log(`🔧 ${description}...`);
    const result = execSync(command, { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 });
    console.log('✅ Success');
    return { success: true, data: result };
  } catch (error) {
    console.log('❌ Failed');
    return { success: false, error: error.message };
  }
}

// 1. Test Health Endpoint
console.log('1. Testing Health Endpoint');
console.log('-------------------------');
const healthResult = runCurlCommand(
  `curl -s ${BASE_URL}/health`,
  'Checking if backend is healthy'
);

if (healthResult.success) {
  try {
    const healthData = JSON.parse(healthResult.data);
    console.log(`   Status: ${healthData.status}`);
    console.log(`   Database: ${healthData.database.connected ? 'Connected' : 'Disconnected'}`);
    console.log(`   AI Services: ${healthData.ai.available ? 'Available' : 'Unavailable'}`);
  } catch (e) {
    console.log('   Failed to parse health response');
  }
}
console.log('');

// 2. Test User Registration
console.log('2. Testing User Registration');
console.log('---------------------------');
console.log(`   Email: ${testUser.email}`);
console.log(`   Name: ${testUser.name}`);
console.log(`   Password: ${testUser.password.replace(/./g, '*')}`);

const registerData = JSON.stringify({
  json: {
    email: testUser.email,
    password: testUser.password,
    name: testUser.name
  }
});

const registerResult = runCurlCommand(
  `curl -s -X POST ${API_URL}/auth.register \
   -H "Content-Type: application/json" \
   -d '${registerData}'`,
  'Registering new user'
);

if (registerResult.success) {
  try {
    const response = JSON.parse(registerResult.data);
    if (response.result && response.result.data) {
      console.log('   ✅ User registered successfully!');
      console.log(`   User ID: ${response.result.data.user.id}`);
      console.log(`   Name: ${response.result.data.user.name}`);
      console.log(`   Email: ${response.result.data.user.email}`);
      testUser.token = response.result.data.token;
    } else {
      console.log('   ⚠️  Unexpected response format');
      console.log(`   Response: ${registerResult.data}`);
    }
  } catch (e) {
    console.log('   ⚠️  Failed to parse registration response');
    console.log(`   Raw response: ${registerResult.data}`);
  }
} else {
  console.log(`   Error: ${registerResult.error}`);
}
console.log('');

// 3. Test User Login
console.log('3. Testing User Login');
console.log('----------------------');

const loginData = JSON.stringify({
  json: {
    email: testUser.email,
    password: testUser.password
  }
});

const loginResult = runCurlCommand(
  `curl -s -X POST ${API_URL}/auth.login \
   -H "Content-Type: application/json" \
   -d '${loginData}'`,
  'Logging in with registered credentials'
);

if (loginResult.success) {
  try {
    const response = JSON.parse(loginResult.data);
    if (response.result && response.result.data) {
      console.log('   ✅ Login successful!');
      console.log(`   User ID: ${response.result.data.user.id}`);
      console.log(`   Name: ${response.result.data.user.name}`);
      console.log(`   Email: ${response.result.data.user.email}`);
      testUser.token = response.result.data.token;

      // 4. Test Protected Endpoint
      console.log('');
      console.log('4. Testing Protected Endpoint');
      console.log('---------------------------');

      const protectedResult = runCurlCommand(
        `curl -s -X POST ${API_URL}/auth.me \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer ${testUser.token}" \
         -d '{"json":{}}'`,
        'Accessing protected user profile endpoint'
      );

      if (protectedResult.success) {
        try {
          const protectedResponse = JSON.parse(protectedResult.data);
          if (protectedResponse.result && protectedResponse.result.data) {
            console.log('   ✅ Protected endpoint accessed successfully!');
            console.log(`   User ID: ${protectedResponse.result.data.user.id}`);
            console.log(`   Name: ${protectedResponse.result.data.user.name}`);
            console.log(`   Email: ${protectedResponse.result.data.user.email}`);
          } else {
            console.log('   ⚠️  Unexpected protected response format');
          }
        } catch (e) {
          console.log('   ⚠️  Failed to parse protected response');
        }
      } else {
        console.log(`   Error: ${protectedResult.error}`);
      }
    } else {
      console.log('   ⚠️  Unexpected login response format');
      console.log(`   Response: ${loginResult.data}`);
    }
  } catch (e) {
    console.log('   ⚠️  Failed to parse login response');
    console.log(`   Raw response: ${loginResult.data}`);
  }
} else {
  console.log(`   Error: ${loginResult.error}`);
}
console.log('');

// 5. Test Invalid Login
console.log('5. Testing Invalid Login');
console.log('-----------------------');

const invalidLoginData = JSON.stringify({
  json: {
    email: testUser.email,
    password: 'wrongpassword'
  }
});

const invalidLoginResult = runCurlCommand(
  `curl -s -X POST ${API_URL}/auth.login \
   -H "Content-Type: application/json" \
   -d '${invalidLoginData}'`,
  'Attempting login with wrong password'
);

if (invalidLoginResult.success) {
  try {
    const response = JSON.parse(invalidLoginResult.data);
    if (response.error) {
      console.log('   ✅ Invalid login properly rejected!');
      console.log(`   Error: ${response.error.json.message}`);
    } else {
      console.log('   ⚠️  Invalid login should have been rejected');
    }
  } catch (e) {
    console.log('   ⚠️  Failed to parse invalid login response');
  }
} else {
  console.log(`   Error: ${invalidLoginResult.error}`);
}
console.log('');

// Summary
console.log('📋 Test Summary');
console.log('===============');
console.log('✅ Backend health check completed');
console.log('✅ User registration tested');
console.log('✅ User login tested');
console.log('✅ Protected endpoint access tested');
console.log('✅ Invalid login rejection tested');
console.log('');
console.log('🎯 Manual Testing Complete!');
console.log('');
console.log('📝 Manual Testing Instructions:');
console.log('1. Open http://localhost:5175 in your browser');
console.log('2. Click "Sign Up" to create a new account');
console.log('3. Fill in the registration form with valid credentials');
console.log('4. Verify successful registration and redirect');
console.log('5. Log out and test login with the same credentials');
console.log('6. Try logging in with wrong credentials to see error handling');
console.log('');
console.log('🔍 Expected Behavior:');
console.log('- Successful registration should create user and redirect to dashboard');
console.log('- Successful login should show user dashboard');
console.log('- Invalid credentials should show appropriate error messages');
console.log('- All API calls should work without CORS errors');