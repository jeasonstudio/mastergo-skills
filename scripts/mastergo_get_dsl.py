#!/usr/bin/env python3
"""
MasterGo DSL Fetcher

Fetch DSL data from MasterGo design files. Supports:
- Direct fileId + layerId
- Short links (https://{domain}/goto/xxx)
- Full URLs

Zero dependencies, compatible with Python 3.6+
"""

import json
import os
import ssl
import sys
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# =============================================================================
# Configuration
# =============================================================================

DEFAULT_ENDPOINT = "https://mastergo.com"
REQUEST_TIMEOUT = 30  # seconds


def get_token() -> str:
    """Get API token from MASTERGO_TOKEN env var (required)"""
    return os.environ.get("MASTERGO_TOKEN", "")


def get_endpoint() -> str:
    """Get API endpoint from MASTERGO_ENDPOINT env var (optional, has default)"""
    url = os.environ.get("MASTERGO_ENDPOINT", DEFAULT_ENDPOINT)
    parsed = urlparse(url)
    # Keep only scheme + host + port
    base = f"{parsed.scheme}://{parsed.netloc}"
    return base if parsed.netloc else DEFAULT_ENDPOINT


# =============================================================================
# URL Parsing
# =============================================================================

def parse_mastergo_url(url: str) -> Optional[Dict[str, str]]:
    """
    Extract fileId and layerId from MasterGo URL.
    
    Supported formats:
    - https://mastergo.com/file/123456?layer_id=1:0001
    - https://mastergo.com/goto/xxx (short link, needs resolution)
    """
    try:
        parsed = urlparse(url)
        # Extract fileId from path (numeric only)
        file_id = next((s for s in parsed.path.split('/') if s.isdigit()), None)
        # Extract layer_id from query
        layer_id = parse_qs(parsed.query).get('layer_id', [None])[0]
        
        if file_id and layer_id:
            return {'fileId': file_id, 'layerId': layer_id}
        return None
    except Exception:
        return None


def is_short_link(url: str) -> bool:
    """Check if URL is a short link"""
    return '/goto/' in url


def resolve_short_link(url: str) -> str:
    """
    Resolve short link to get the full redirect URL.
    
    Short links return 3xx redirect, we need to get target URL from Location header.
    """
    # Create SSL context without verification (consistent with original TS impl)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = Request(url, method='GET')
    req.add_header('User-Agent', 'MasterGo-DSL-Tool/1.0')
    
    try:
        # Normally short links will redirect
        with urlopen(req, timeout=REQUEST_TIMEOUT, context=ctx) as resp:
            # If no redirect, return final URL
            return resp.url
    except HTTPError as e:
        # 3xx redirect throws exception, get Location from headers
        if 300 <= e.code < 400:
            location = e.headers.get('Location')
            if location:
                return location
        raise ValueError(f"Failed to resolve short link: HTTP {e.code}")


def extract_ids_from_url(url: str) -> Tuple[str, str]:
    """
    Extract fileId and layerId from URL.
    
    Automatically handles short link resolution.
    """
    target_url = url
    
    # Handle short links
    if is_short_link(url):
        target_url = resolve_short_link(url)
    
    # Parse URL
    result = parse_mastergo_url(target_url)
    if not result:
        raise ValueError(f"Cannot extract fileId or layerId from URL: {target_url}")
    
    return result['fileId'], result['layerId']


# =============================================================================
# DSL Fetching
# =============================================================================

def get_dsl(file_id: str, layer_id: str, token: str = None, endpoint: str = None) -> Dict:
    """
    Fetch MasterGo DSL data.
    
    Args:
        file_id: File ID
        layer_id: Layer ID
        token: API Token (optional, defaults to MASTERGO_TOKEN env var)
        endpoint: API endpoint (optional, defaults to MASTERGO_ENDPOINT env var)
    
    Returns:
        Dict containing dsl, componentDocumentLinks, and rules
    """
    token = token or get_token()
    endpoint = endpoint or get_endpoint()
    
    if not token:
        raise ValueError("MASTERGO_TOKEN env var is required but not set")
    
    # Build request
    api_url = f"{endpoint}/mcp/dsl?fileId={file_id}&layerId={layer_id}"
    
    req = Request(api_url, method='GET')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept', 'application/json')
    req.add_header('X-MG-UserAccessToken', token)
    
    # SSL config (consistent with original impl, skip certificate verification)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        with urlopen(req, timeout=REQUEST_TIMEOUT, context=ctx) as resp:
            dsl_data = json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else str(e)
        raise ValueError(f"API request failed: HTTP {e.code} - {error_body}")
    except URLError as e:
        raise ValueError(f"Network error: {e.reason}")
    
    # Extract component document links
    component_links = extract_component_links(dsl_data)
    
    return {
        'dsl': dsl_data,
        'componentDocumentLinks': component_links,
        'rules': build_dsl_rules(),
    }


def get_dsl_from_url(url: str, token: str = None, endpoint: str = None) -> Dict:
    """
    Fetch DSL data from MasterGo URL (convenience method).
    
    Automatically parses fileId and layerId from URL.
    """
    file_id, layer_id = extract_ids_from_url(url)
    return get_dsl(file_id, layer_id, token, endpoint)


# =============================================================================
# DSL Processing
# =============================================================================

def extract_component_links(dsl: Dict) -> list:
    """Extract component document links from DSL"""
    links = set()
    
    def traverse(node):
        if not node or not isinstance(node, dict):
            return
        # Extract componentSetDocumentLink
        try:
            link = node.get('componentInfo', {}).get('componentSetDocumentLink', [None])[0]
            if link:
                links.add(link)
        except (TypeError, IndexError, AttributeError):
            pass
        # Recursively process children
        for child in node.get('children', []):
            traverse(child)
    
    # Traverse nodes array
    for node in dsl.get('nodes', []):
        traverse(node)
    
    return list(links)


def build_dsl_rules() -> list:
    """Build DSL usage rules"""
    rules = [
        "token field must be generated as a variable (colors, shadows, fonts, etc.) "
        "and the token field must be displayed in the comment",
        "componentDocumentLinks is a list of frontend component documentation links used in the DSL layer, "
        "designed to help you understand how to use the components. "
        "When it exists and is not empty, you need to fetch all component documentation content, "
        "understand component usage, and generate code using the components.",
    ]
    
    # Load extra rules from environment variable
    env_rules = os.environ.get('RULES', '[]')
    try:
        extra_rules = json.loads(env_rules)
        if isinstance(extra_rules, list):
            rules.extend(extra_rules)
    except json.JSONDecodeError:
        pass
    
    return rules


# =============================================================================
# CLI
# =============================================================================

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fetch DSL data from MasterGo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Using URL
  python mastergo_get_dsl.py "https://mastergo.com/file/123456?layer_id=1:0001"
  
  # Using short link
  python mastergo_get_dsl.py "https://mastergo.com/goto/xxx"
  
  # Using fileId and layerId
  python mastergo_get_dsl.py --file-id 123456 --layer-id "1:0001"

Environment Variables:
  MASTERGO_TOKEN     API Token (required)
  MASTERGO_ENDPOINT  API endpoint (optional, default: https://mastergo.com)
'''
    )
    
    parser.add_argument('url', nargs='?', help='MasterGo URL or short link')
    parser.add_argument('--file-id', '-f', help='File ID')
    parser.add_argument('--layer-id', '-l', help='Layer ID')
    parser.add_argument('--token', '-t', help='API Token (defaults to MASTERGO_TOKEN)')
    parser.add_argument('--endpoint', '-e', help='API endpoint (defaults to MASTERGO_ENDPOINT)')
    parser.add_argument('--pretty', '-p', action='store_true', help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    try:
        if args.url:
            result = get_dsl_from_url(args.url, args.token, args.endpoint)
        elif args.file_id and args.layer_id:
            result = get_dsl(args.file_id, args.layer_id, args.token, args.endpoint)
        else:
            parser.error('Please provide URL or --file-id and --layer-id')
        
        # Output JSON
        indent = 2 if args.pretty else None
        print(json.dumps(result, ensure_ascii=False, indent=indent))
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()
