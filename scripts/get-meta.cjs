#!/usr/bin/env node
/**
 * Get site/page metadata from MasterGo API
 * 
 * Returns XML metadata containing page list and site configuration.
 * Used for multi-page site building workflow.
 * 
 * @example
 * node get-meta.js --fileId=155675508499265 --layerId=158:0001
 * node get-meta.js "https://mastergo.com/file/155675508499265?layer_id=158:0001"
 */

const https = require('https');
const { parseMasterGoUrl, isShortLink } = require('./parse-mastergo-url.cjs');

// Configuration
const API_URL = process.env.MASTERGO_API_URL || 'https://mastergo.com';
const TOKEN = process.env.MASTERGO_TOKEN;

// Error codes and suggestions
const ERROR_MAP = {
  401: { code: 'TOKEN_INVALID', message: 'Token 无效或已过期', suggestion: '请在 MasterGo 个人设置 → 安全设置重新生成 Token' },
  403: { code: 'PERMISSION_DENIED', message: '无权访问此文件', suggestion: '请检查: 1) 账户为团队版或以上 2) 文件在团队项目中（非草稿）' },
  404: { code: 'NOT_FOUND', message: '文件或图层不存在', suggestion: '请检查链接是否正确' },
  408: { code: 'TIMEOUT', message: '请求超时', suggestion: '请检查网络连接，稍后重试' },
  504: { code: 'TIMEOUT', message: '请求超时', suggestion: '请检查网络连接，稍后重试' },
};

/**
 * Make HTTPS request with authentication
 */
function request(url) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const req = https.request({
      hostname: urlObj.hostname,
      port: urlObj.port || 443,
      path: urlObj.pathname + urlObj.search,
      method: 'GET',
      headers: {
        'X-MG-UserAccessToken': TOKEN,
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        resolve({ statusCode: res.statusCode, headers: res.headers, data });
      });
    });
    req.on('error', reject);
    req.on('timeout', () => reject(new Error('Request timeout')));
    req.end();
  });
}

/**
 * Resolve short link to full URL
 */
async function resolveShortLink(shortUrl) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(shortUrl);
    https.get({
      hostname: urlObj.hostname,
      path: urlObj.pathname,
      headers: { 'User-Agent': 'MasterGo-Skills/1.0' },
    }, (res) => {
      if (res.statusCode === 302 && res.headers.location) {
        resolve(res.headers.location);
      } else {
        reject(new Error(`Failed to resolve short link: ${res.statusCode}`));
      }
    }).on('error', reject);
  });
}

/**
 * Format error response
 */
function formatError(statusCode, rawMessage) {
  const err = ERROR_MAP[statusCode] || {
    code: 'UNKNOWN_ERROR',
    message: rawMessage || `HTTP ${statusCode}`,
    suggestion: '请稍后重试或联系支持'
  };
  return { error: true, ...err };
}

/**
 * Parse XML to extract actions
 */
function parseMetaXml(xml) {
  const actions = [];
  const actionRegex = /<action\s+title="([^"]+)"\s+layerId="([^"]+)"\s*\/>/g;
  let match;
  while ((match = actionRegex.exec(xml)) !== null) {
    actions.push({ title: match[1], layerId: match[2] });
  }
  return actions;
}

/**
 * Get meta from MasterGo API
 */
async function getMeta(fileId, layerId) {
  const url = `${API_URL}/mcp/meta?fileId=${encodeURIComponent(fileId)}&layerId=${encodeURIComponent(layerId)}`;
  
  const { statusCode, data } = await request(url);
  
  if (statusCode !== 200) {
    return formatError(statusCode, data);
  }
  
  const parsed = JSON.parse(data);
  const actions = parseMetaXml(parsed.result || '');
  
  return {
    result: parsed.result,
    actions,
    rules: parsed.rules || [
      '遍历所有 action 的 layerId 获取各页面 DSL',
      '解析 interactive 字段发现页面导航关系',
      '递归获取目标页面直到无更多导航',
    ],
  };
}

/**
 * Main entry point
 */
async function main() {
  // Check token
  if (!TOKEN) {
    console.log(JSON.stringify({
      error: true,
      code: 'TOKEN_MISSING',
      message: '未设置 MASTERGO_TOKEN 环境变量',
      suggestion: '请设置环境变量: export MASTERGO_TOKEN="your_token"',
    }, null, 2));
    process.exit(1);
  }
  
  // Parse arguments
  const args = process.argv.slice(2);
  let fileId, layerId;
  
  if (args.length === 0) {
    console.log(JSON.stringify({
      error: true,
      code: 'MISSING_ARGS',
      message: '缺少参数',
      suggestion: '用法: node get-meta.js <url> 或 node get-meta.js --fileId=xxx --layerId=xxx',
    }, null, 2));
    process.exit(1);
  }
  
  // Check for URL argument
  const urlArg = args.find(a => a.startsWith('http'));
  if (urlArg) {
    if (isShortLink(urlArg)) {
      try {
        const fullUrl = await resolveShortLink(urlArg);
        const parsed = parseMasterGoUrl(fullUrl);
        if (!parsed) throw new Error('Could not extract layerId from URL');
        fileId = parsed.fileId;
        layerId = parsed.layerId;
      } catch (err) {
        console.log(JSON.stringify({
          error: true,
          code: 'SHORT_LINK_FAILED',
          message: err.message,
          suggestion: '请使用完整链接格式',
        }, null, 2));
        process.exit(1);
      }
    } else {
      const parsed = parseMasterGoUrl(urlArg);
      if (!parsed) {
        console.log(JSON.stringify({
          error: true,
          code: 'INVALID_URL',
          message: '无效的 MasterGo URL',
          suggestion: '请使用格式: https://mastergo.com/file/{fileId}?layer_id={layerId}',
        }, null, 2));
        process.exit(1);
      }
      fileId = parsed.fileId;
      layerId = parsed.layerId;
    }
  } else {
    // Parse --fileId and --layerId
    for (const arg of args) {
      if (arg.startsWith('--fileId=')) fileId = arg.split('=')[1];
      if (arg.startsWith('--layerId=')) layerId = arg.split('=')[1];
    }
    
    if (!fileId || !layerId) {
      console.log(JSON.stringify({
        error: true,
        code: 'MISSING_ARGS',
        message: '缺少 fileId 或 layerId',
        suggestion: '用法: node get-meta.js --fileId=xxx --layerId=xxx',
      }, null, 2));
      process.exit(1);
    }
  }
  
  // Get meta
  try {
    const result = await getMeta(fileId, layerId);
    console.log(JSON.stringify(result, null, 2));
    if (result.error) process.exit(1);
  } catch (err) {
    console.log(JSON.stringify({
      error: true,
      code: 'REQUEST_FAILED',
      message: err.message,
      suggestion: '请检查网络连接和 API 地址',
    }, null, 2));
    process.exit(1);
  }
}

main();
