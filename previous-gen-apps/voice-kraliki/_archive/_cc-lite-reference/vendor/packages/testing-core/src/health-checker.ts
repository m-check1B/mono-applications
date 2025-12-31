/**
 * Health Checker - Verifies apps are running and accessible
 */

import axios from 'axios';
import chalk from 'chalk';
import { AppConfig } from './types';

export class HealthChecker {
  async checkApp(config: AppConfig): Promise<boolean> {
    console.log(chalk.blue(`\n🔍 Checking ${config.name}...`));
    
    const results = {
      frontend: false,
      backend: false,
      auth: false,
    };

    // Check frontend
    try {
      const frontendResponse = await axios.get(config.frontendUrl, {
        timeout: 5000,
        validateStatus: () => true,
      });
      results.frontend = frontendResponse.status < 500;
      console.log(
        results.frontend 
          ? chalk.green(`✓ Frontend: ${config.frontendUrl}`)
          : chalk.red(`✗ Frontend: ${config.frontendUrl} (${frontendResponse.status})`)
      );
    } catch (error: any) {
      console.log(chalk.red(`✗ Frontend: ${config.frontendUrl} (${error.message})`));
    }

    // Check backend
    try {
      const backendResponse = await axios.get(
        config.healthEndpoint || `${config.backendUrl}/health`,
        { timeout: 5000, validateStatus: () => true }
      );
      results.backend = backendResponse.status < 500;
      console.log(
        results.backend
          ? chalk.green(`✓ Backend: ${config.backendUrl}`)
          : chalk.red(`✗ Backend: ${config.backendUrl} (${backendResponse.status})`)
      );
    } catch (error: any) {
      console.log(chalk.red(`✗ Backend: ${config.backendUrl} (${error.message})`));
    }

    // Check auth endpoint if provided
    if (config.authEndpoint) {
      try {
        const authResponse = await axios.post(
          config.authEndpoint,
          {},
          { 
            timeout: 5000, 
            validateStatus: () => true,
            headers: { 'Content-Type': 'application/json' }
          }
        );
        // Auth endpoints typically return 400 for missing credentials, that's ok
        results.auth = authResponse.status < 500;
        console.log(
          results.auth
            ? chalk.green(`✓ Auth endpoint: ${config.authEndpoint}`)
            : chalk.red(`✗ Auth endpoint: ${config.authEndpoint} (${authResponse.status})`)
        );
      } catch (error: any) {
        console.log(chalk.red(`✗ Auth endpoint: ${config.authEndpoint} (${error.message})`));
      }
    }

    const allHealthy = results.frontend && results.backend;
    console.log(
      allHealthy
        ? chalk.green(`\n✅ ${config.name} is healthy!`)
        : chalk.red(`\n❌ ${config.name} has issues!`)
    );

    return allHealthy;
  }

  async checkMultipleApps(configs: AppConfig[]): Promise<Map<string, boolean>> {
    const results = new Map<string, boolean>();
    
    console.log(chalk.cyan('\n🏥 Starting health checks for all apps...\n'));
    
    for (const config of configs) {
      const isHealthy = await this.checkApp(config);
      results.set(config.name, isHealthy);
    }

    // Summary
    console.log(chalk.cyan('\n📊 Health Check Summary:'));
    console.log(chalk.cyan('========================'));
    
    let allHealthy = true;
    results.forEach((isHealthy, appName) => {
      console.log(
        isHealthy
          ? chalk.green(`✅ ${appName}: Healthy`)
          : chalk.red(`❌ ${appName}: Unhealthy`)
      );
      if (!isHealthy) allHealthy = false;
    });

    return results;
  }
}