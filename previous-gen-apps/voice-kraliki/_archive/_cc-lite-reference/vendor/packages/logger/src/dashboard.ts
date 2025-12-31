/**
 * Stack 2025 Logger Monitoring Dashboard
 * Real-time log monitoring and metrics visualization
 */

import Fastify from 'fastify';
import websocket from '@fastify/websocket';
import { Stack2025Logger } from './logger.js';
import { LogEntry, LogLevel } from './types.js';

export interface DashboardConfig {
  port?: number;
  host?: string;
  logger: Stack2025Logger;
  refreshInterval?: number;
}

export class LoggerDashboard {
  private server: any;
  private config: DashboardConfig;
  private clients: Set<any> = new Set();
  private logBuffer: LogEntry[] = [];
  private maxBufferSize = 1000;

  constructor(config: DashboardConfig) {
    this.config = {
      port: 9090,
      host: '127.0.0.1',
      refreshInterval: 1000,
      ...config
    };
    
    this.server = Fastify();
  }

  async start(): Promise<void> {
    // Register WebSocket plugin
    await this.server.register(websocket);
    
    // Serve dashboard HTML
    this.server.get('/', async (request: any, reply: any) => {
      reply.type('text/html').send(this.getDashboardHTML());
    });
    
    // API endpoints
    this.server.get('/api/metrics', async (request: any, reply: any) => {
      const metrics = this.config.logger.getMetrics();
      reply.send(metrics);
    });
    
    this.server.get('/api/logs', async (request: any, reply: any) => {
      const { level, limit = 100 } = request.query;
      const logs = this.logBuffer
        .filter(log => !level || log.level === level)
        .slice(-limit);
      reply.send(logs);
    });
    
    // WebSocket for real-time updates
    const dashboard = this;
    this.server.register(async function (fastify: any) {
      fastify.get('/ws', { websocket: true }, (connection: any, req: any) => {
        const { socket } = connection;
        dashboard.clients.add(socket);
        
        // Send initial state
        socket.send(JSON.stringify({
          type: 'init',
          data: {
            metrics: dashboard.config.logger.getMetrics(),
            logs: dashboard.logBuffer.slice(-100)
          }
        }));
        
        socket.on('close', () => {
          dashboard.clients.delete(socket);
        });
      });
    });
    
    // Start metrics broadcast
    this.startMetricsBroadcast();
    
    // Start server
    await this.server.listen({
      port: this.config.port,
      host: this.config.host
    });
    
    console.log(`Logger Dashboard running at http://${this.config.host}:${this.config.port}`);
  }

  async stop(): Promise<void> {
    await this.server.close();
  }

  private startMetricsBroadcast(): void {
    setInterval(() => {
      const metrics = this.config.logger.getMetrics();
      const message = JSON.stringify({
        type: 'metrics',
        data: metrics
      });
      
      this.clients.forEach(client => {
        if (client.readyState === 1) { // WebSocket.OPEN
          client.send(message);
        }
      });
    }, this.config.refreshInterval);
  }

  addLog(entry: LogEntry): void {
    this.logBuffer.push(entry);
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer.shift();
    }
    
    // Broadcast to connected clients
    const message = JSON.stringify({
      type: 'log',
      data: entry
    });
    
    this.clients.forEach(client => {
      if (client.readyState === 1) {
        client.send(message);
      }
    });
  }

  private getDashboardHTML(): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Stack 2025 Logger Dashboard</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #0a0a0a;
      color: #e0e0e0;
      padding: 20px;
    }
    .container { max-width: 1400px; margin: 0 auto; }
    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 20px;
      border-radius: 10px;
      margin-bottom: 20px;
    }
    h1 { color: white; margin-bottom: 10px; }
    .subtitle { color: rgba(255,255,255,0.9); }
    
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 20px;
    }
    
    .card {
      background: #1a1a1a;
      border: 1px solid #333;
      border-radius: 8px;
      padding: 20px;
    }
    .card h3 {
      color: #667eea;
      margin-bottom: 15px;
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .metric {
      font-size: 32px;
      font-weight: bold;
      color: white;
      margin-bottom: 5px;
    }
    .label { color: #888; font-size: 12px; }
    
    .logs-container {
      background: #1a1a1a;
      border: 1px solid #333;
      border-radius: 8px;
      padding: 20px;
      height: 500px;
      overflow-y: auto;
    }
    .logs-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;
    }
    .logs-title {
      color: #667eea;
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .log-filters {
      display: flex;
      gap: 10px;
    }
    .filter-btn {
      background: #2a2a2a;
      border: 1px solid #444;
      color: #999;
      padding: 5px 10px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
    }
    .filter-btn.active {
      background: #667eea;
      color: white;
      border-color: #667eea;
    }
    
    .log-entry {
      font-family: 'Monaco', 'Courier New', monospace;
      font-size: 12px;
      line-height: 1.5;
      padding: 8px;
      border-bottom: 1px solid #2a2a2a;
    }
    .log-entry:hover { background: #222; }
    
    .log-error { border-left: 3px solid #ff4444; }
    .log-warn { border-left: 3px solid #ffaa00; }
    .log-info { border-left: 3px solid #00aaff; }
    .log-debug { border-left: 3px solid #888; }
    
    .timestamp { color: #666; margin-right: 10px; }
    .level {
      display: inline-block;
      width: 50px;
      margin-right: 10px;
      font-weight: bold;
    }
    .level-error { color: #ff4444; }
    .level-warn { color: #ffaa00; }
    .level-info { color: #00aaff; }
    .level-debug { color: #888; }
    
    .message { color: #e0e0e0; }
    .context { color: #666; margin-left: 10px; }
    
    .status-indicator {
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      margin-right: 5px;
      animation: pulse 2s infinite;
    }
    .status-healthy { background: #00ff00; }
    .status-warning { background: #ffaa00; }
    .status-critical { background: #ff4444; }
    
    @keyframes pulse {
      0% { opacity: 1; }
      50% { opacity: 0.5; }
      100% { opacity: 1; }
    }
    
    .chart-container {
      background: #1a1a1a;
      border: 1px solid #333;
      border-radius: 8px;
      padding: 20px;
      margin-top: 20px;
      height: 300px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🔍 Stack 2025 Logger Dashboard</h1>
      <div class="subtitle">
        <span class="status-indicator status-healthy"></span>
        Real-time monitoring and metrics
      </div>
    </div>
    
    <div class="grid">
      <div class="card">
        <h3>Total Logs</h3>
        <div class="metric" id="total-logs">0</div>
        <div class="label">All time</div>
      </div>
      
      <div class="card">
        <h3>Error Rate</h3>
        <div class="metric" id="error-rate">0%</div>
        <div class="label">Last 5 minutes</div>
      </div>
      
      <div class="card">
        <h3>Logs/Second</h3>
        <div class="metric" id="logs-per-second">0</div>
        <div class="label">Current rate</div>
      </div>
      
      <div class="card">
        <h3>P95 Response</h3>
        <div class="metric" id="p95-response">0ms</div>
        <div class="label">95th percentile</div>
      </div>
      
      <div class="card">
        <h3>Memory Usage</h3>
        <div class="metric" id="memory-usage">0MB</div>
        <div class="label">Peak usage</div>
      </div>
      
      <div class="card">
        <h3>Health Status</h3>
        <div class="metric" id="health-status">Healthy</div>
        <div class="label" id="health-issues">No issues</div>
      </div>
    </div>
    
    <div class="logs-container">
      <div class="logs-header">
        <div class="logs-title">Live Logs</div>
        <div class="log-filters">
          <button class="filter-btn active" data-level="all">All</button>
          <button class="filter-btn" data-level="error">Errors</button>
          <button class="filter-btn" data-level="warn">Warnings</button>
          <button class="filter-btn" data-level="info">Info</button>
          <button class="filter-btn" data-level="debug">Debug</button>
        </div>
      </div>
      <div id="logs"></div>
    </div>
    
    <div class="chart-container">
      <h3 style="color: #667eea; margin-bottom: 15px;">Log Volume Over Time</h3>
      <canvas id="chart"></canvas>
    </div>
  </div>
  
  <script>
    let ws;
    let currentFilter = 'all';
    let logs = [];
    
    function connect() {
      ws = new WebSocket('ws://localhost:9090/ws');
      
      ws.onopen = () => {
        console.log('Connected to logger dashboard');
      };
      
      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        
        switch(message.type) {
          case 'init':
            updateMetrics(message.data.metrics);
            logs = message.data.logs;
            renderLogs();
            break;
          case 'metrics':
            updateMetrics(message.data);
            break;
          case 'log':
            logs.push(message.data);
            if (logs.length > 1000) logs.shift();
            renderLogs();
            break;
        }
      };
      
      ws.onclose = () => {
        console.log('Disconnected from logger dashboard');
        setTimeout(connect, 3000);
      };
    }
    
    function updateMetrics(metrics) {
      if (!metrics) return;
      
      document.getElementById('total-logs').textContent = 
        metrics.logs?.totalLogs?.toLocaleString() || '0';
      
      const errorRate = metrics.logs?.totalLogs > 0 
        ? ((metrics.logs.errorCount / metrics.logs.totalLogs) * 100).toFixed(1)
        : '0';
      document.getElementById('error-rate').textContent = errorRate + '%';
      
      document.getElementById('logs-per-second').textContent = 
        (metrics.logs?.totalLogs / ((Date.now() - performance.timing.navigationStart) / 1000)).toFixed(1);
      
      document.getElementById('p95-response').textContent = 
        (metrics.performance?.p95 || 0) + 'ms';
      
      const memoryMB = ((metrics.logs?.peakMemoryUsage || 0) / 1024 / 1024).toFixed(1);
      document.getElementById('memory-usage').textContent = memoryMB + 'MB';
      
      // Update health status
      const healthStatus = document.getElementById('health-status');
      const healthIssues = document.getElementById('health-issues');
      
      if (errorRate > 10) {
        healthStatus.textContent = 'Critical';
        healthStatus.style.color = '#ff4444';
        healthIssues.textContent = 'High error rate';
      } else if (errorRate > 5) {
        healthStatus.textContent = 'Warning';
        healthStatus.style.color = '#ffaa00';
        healthIssues.textContent = 'Elevated errors';
      } else {
        healthStatus.textContent = 'Healthy';
        healthStatus.style.color = '#00ff00';
        healthIssues.textContent = 'No issues';
      }
    }
    
    function renderLogs() {
      const container = document.getElementById('logs');
      const filteredLogs = currentFilter === 'all' 
        ? logs 
        : logs.filter(log => log.level === currentFilter);
      
      const html = filteredLogs.slice(-100).reverse().map(log => {
        const timestamp = new Date(log.timestamp).toLocaleTimeString();
        const levelClass = 'level-' + log.level;
        const entryClass = 'log-' + log.level;
        
        return \`<div class="log-entry \${entryClass}">
          <span class="timestamp">\${timestamp}</span>
          <span class="level \${levelClass}">\${log.level.toUpperCase()}</span>
          <span class="message">\${log.message}</span>
          \${log.context ? '<span class="context">' + JSON.stringify(log.context) + '</span>' : ''}
        </div>\`;
      }).join('');
      
      container.innerHTML = html;
    }
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentFilter = e.target.dataset.level;
        renderLogs();
      });
    });
    
    // Connect to WebSocket
    connect();
  </script>
</body>
</html>`;
  }
}

export function createDashboard(config: DashboardConfig): LoggerDashboard {
  return new LoggerDashboard(config);
}