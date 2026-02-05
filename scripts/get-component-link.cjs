#!/usr/bin/env node
/**
 * Get component documentation content from URL
 * 
 * Fetches Markdown/MDX content from component documentation URLs
 * found in DSL componentDocumentLinks array.
 * 
 * @example
 * node get-component-link.js "https://example.com/ant/button.mdx"
 */

const https = require('https');
const http = require('http');

/**
 * Make HTTP/HTTPS request
 */
function request(url) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const protocol = urlObj.protocol === 'https:' ? https : http;
    
    const req = protocol.get({
      hostname: urlObj.hostname,
      port: urlObj.port || (urlObj.protocol === 'https:' ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      headers: {
        'User-Agent': 'MasterGo-Skills/1.0',
        'Accept': 'text/markdown, text/plain, */*',
      },
      timeout: 30000,
    }, (res) => {
      // Handle redirects
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return resolve(request(res.headers.location));
      }
      
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        resolve({ statusCode: res.statusCode, data });
      });
    });
    
    req.on('error', reject);
    req.on('timeout', () => reject(new Error('Request timeout')));
  });
}

/**
 * Main entry point
 */
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || !args[0].startsWith('http')) {
    console.log(JSON.stringify({
      error: true,
      code: 'MISSING_URL',
      message: '缺少组件文档 URL',
      suggestion: '用法: node get-component-link.js <url>',
    }, null, 2));
    process.exit(1);
  }
  
  const url = args[0];
  
  try {
    const { statusCode, data } = await request(url);
    
    if (statusCode !== 200) {
      console.log(JSON.stringify({
        error: true,
        code: 'FETCH_FAILED',
        message: `获取组件文档失败: HTTP ${statusCode}`,
        suggestion: '请检查 URL 是否正确且可访问',
      }, null, 2));
      process.exit(1);
    }
    
    // Output the content directly (for piping) or as JSON
    if (process.stdout.isTTY) {
      console.log(JSON.stringify({
        url,
        content: data,
      }, null, 2));
    } else {
      console.log(data);
    }
  } catch (err) {
    console.log(JSON.stringify({
      error: true,
      code: 'REQUEST_FAILED',
      message: err.message,
      suggestion: '请检查网络连接和 URL 地址',
    }, null, 2));
    process.exit(1);
  }
}

main();
