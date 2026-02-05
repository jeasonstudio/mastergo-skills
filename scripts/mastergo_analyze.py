#!/usr/bin/env python3
"""
MasterGo DSL Analyzer

Analyze DSL structure and output human-readable summary to stdout.
Helps understand page structure before generating code.

Usage:
  # From URL (fetches and analyzes)
  python mastergo_analyze.py "https://mastergo.com/goto/xxx"
  
  # From stdin
  cat dsl.json | python mastergo_analyze.py --stdin
  
  # Different output formats
  python mastergo_analyze.py URL --format tree    # Tree view (default)
  python mastergo_analyze.py URL --format json    # JSON summary
  python mastergo_analyze.py URL --format flat    # Flat list

Zero dependencies, compatible with Python 3.6+
"""

import json
import sys
import argparse
from typing import Dict, List, Any, Optional

# Import from sibling module
try:
    from mastergo_get_dsl import get_dsl_from_url, extract_ids_from_url
except ImportError:
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from mastergo_get_dsl import get_dsl_from_url, extract_ids_from_url


# =============================================================================
# DSL Analysis
# =============================================================================

def analyze_node(node: Dict, depth: int = 0) -> Dict[str, Any]:
    """Analyze a single DSL node and return summary."""
    if not node or not isinstance(node, dict):
        return {}
    
    summary = {
        'id': node.get('id', ''),
        'name': node.get('name', ''),
        'type': node.get('type', ''),
        'depth': depth,
    }
    
    # Size info
    layout = node.get('layout', {})
    width = layout.get('width', {})
    height = layout.get('height', {})
    if width and height:
        w = width.get('value', '?')
        h = height.get('value', '?')
        summary['size'] = f"{w}x{h}"
    
    # Text content
    if node.get('type') == 'TEXT' or node.get('characters'):
        text = node.get('characters', '')
        if text:
            summary['text'] = text[:100] + ('...' if len(text) > 100 else '')
    
    # Component info
    comp_info = node.get('componentInfo', {})
    if comp_info:
        doc_links = comp_info.get('componentSetDocumentLink', [])
        if doc_links:
            summary['componentDoc'] = doc_links[0]
    
    # Interactive (navigation)
    interactive = node.get('interactive', [])
    for action in interactive:
        if action.get('type') == 'navigation':
            summary['navigateTo'] = action.get('targetLayerId')
    
    # Style tag
    style = node.get('style', {})
    if style.get('tag'):
        summary['tag'] = style.get('tag')
    
    # Token references
    token_alias = style.get('styleTokenAlias', {})
    if token_alias:
        summary['tokens'] = list(token_alias.keys())
    
    # Children
    children = node.get('children', [])
    if children:
        summary['children'] = [analyze_node(child, depth + 1) for child in children]
    
    return summary


def analyze_dsl(dsl_data: Dict) -> Dict[str, Any]:
    """Analyze complete DSL and return structured summary."""
    # Handle wrapped response (from get_dsl script)
    dsl = dsl_data.get('dsl', dsl_data)
    
    result = {
        'version': dsl.get('version', 'unknown'),
        'framework': dsl.get('framework', 'unknown'),
        'stats': {
            'totalNodes': 0,
            'textNodes': 0,
            'componentInstances': 0,
            'navigations': 0,
        },
        'componentDocs': [],
        'texts': [],
        'navigations': [],
        'structure': [],
    }
    
    # Collect data
    all_nodes = []
    
    def traverse(node: Dict, depth: int = 0):
        if not node:
            return
        
        result['stats']['totalNodes'] += 1
        
        # Collect text
        if node.get('type') == 'TEXT' and node.get('characters'):
            result['texts'].append({
                'id': node.get('id'),
                'name': node.get('name'),
                'text': node.get('characters'),
            })
            result['stats']['textNodes'] += 1
        
        # Collect component docs
        comp_info = node.get('componentInfo', {})
        doc_links = comp_info.get('componentSetDocumentLink', [])
        for link in doc_links:
            if link and link not in result['componentDocs']:
                result['componentDocs'].append(link)
                result['stats']['componentInstances'] += 1
        
        # Collect navigations
        for action in node.get('interactive', []):
            if action.get('type') == 'navigation':
                result['navigations'].append({
                    'sourceId': node.get('id'),
                    'sourceName': node.get('name'),
                    'targetLayerId': action.get('targetLayerId'),
                })
                result['stats']['navigations'] += 1
        
        # Recurse
        for child in node.get('children', []):
            traverse(child, depth + 1)
    
    # Process root or nodes array
    root = dsl.get('root')
    nodes = dsl.get('nodes', [])
    
    if root:
        traverse(root)
        result['structure'] = [analyze_node(root)]
    elif nodes:
        for node in nodes:
            traverse(node)
        result['structure'] = [analyze_node(n) for n in nodes]
    
    return result


# =============================================================================
# Output Formatters
# =============================================================================

def format_tree(analysis: Dict, indent: str = '') -> str:
    """Format analysis as tree view."""
    lines = []
    
    # Header
    lines.append(f"DSL Analysis (v{analysis['version']}, {analysis['framework']})")
    lines.append(f"Stats: {analysis['stats']['totalNodes']} nodes, "
                 f"{analysis['stats']['textNodes']} texts, "
                 f"{analysis['stats']['componentInstances']} components, "
                 f"{analysis['stats']['navigations']} navigations")
    lines.append('')
    
    # Component docs
    if analysis['componentDocs']:
        lines.append('Component Docs:')
        for doc in analysis['componentDocs']:
            lines.append(f"  - {doc}")
        lines.append('')
    
    # Structure tree
    lines.append('Structure:')
    
    def print_node(node: Dict, prefix: str = '', is_last: bool = True):
        if not node:
            return
        
        connector = '└── ' if is_last else '├── '
        node_type = node.get('type', '?')
        name = node.get('name', 'unnamed')
        size = node.get('size', '')
        
        line = f"{prefix}{connector}[{node_type}] {name}"
        if size:
            line += f" ({size})"
        if node.get('text'):
            text = node['text'][:50] + ('...' if len(node['text']) > 50 else '')
            line += f' "{text}"'
        if node.get('tag'):
            line += f" <{node['tag']}>"
        if node.get('navigateTo'):
            line += f" → {node['navigateTo']}"
        
        lines.append(line)
        
        children = node.get('children', [])
        child_prefix = prefix + ('    ' if is_last else '│   ')
        for i, child in enumerate(children):
            print_node(child, child_prefix, i == len(children) - 1)
    
    for i, node in enumerate(analysis.get('structure', [])):
        print_node(node, '', i == len(analysis['structure']) - 1)
    
    # Text contents
    if analysis['texts']:
        lines.append('')
        lines.append('Text Contents:')
        for t in analysis['texts'][:20]:  # Limit to 20
            text = t['text'][:80] + ('...' if len(t['text']) > 80 else '')
            lines.append(f"  [{t['id']}] {t['name']}: \"{text}\"")
        if len(analysis['texts']) > 20:
            lines.append(f"  ... and {len(analysis['texts']) - 20} more")
    
    # Navigations
    if analysis['navigations']:
        lines.append('')
        lines.append('Navigations:')
        for nav in analysis['navigations']:
            lines.append(f"  {nav['sourceName']} ({nav['sourceId']}) → {nav['targetLayerId']}")
    
    return '\n'.join(lines)


def format_flat(analysis: Dict) -> str:
    """Format as flat node list."""
    lines = []
    
    def flatten(node: Dict, path: str = ''):
        if not node:
            return
        
        name = node.get('name', 'unnamed')
        current_path = f"{path}/{name}" if path else name
        
        node_type = node.get('type', '?')
        size = node.get('size', '')
        text = node.get('text', '')
        
        line = f"[{node_type}] {current_path}"
        if size:
            line += f" | {size}"
        if text:
            line += f' | "{text[:50]}"'
        
        lines.append(line)
        
        for child in node.get('children', []):
            flatten(child, current_path)
    
    for node in analysis.get('structure', []):
        flatten(node)
    
    return '\n'.join(lines)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Analyze MasterGo DSL structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Analyze from URL
  python mastergo_analyze.py "https://mastergo.com/goto/xxx"
  
  # Analyze from stdin
  cat dsl.json | python mastergo_analyze.py --stdin
  
  # JSON summary output
  python mastergo_analyze.py URL --format json
  
  # Flat list output
  python mastergo_analyze.py URL --format flat
'''
    )
    
    parser.add_argument('url', nargs='?', help='MasterGo URL to analyze')
    parser.add_argument('--stdin', action='store_true', help='Read DSL JSON from stdin')
    parser.add_argument('--format', '-f', choices=['tree', 'json', 'flat'], 
                        default='tree', help='Output format (default: tree)')
    parser.add_argument('--token', '-t', help='API Token (defaults to MASTERGO_TOKEN)')
    
    args = parser.parse_args()
    
    try:
        # Get DSL data
        if args.stdin:
            dsl_data = json.load(sys.stdin)
        elif args.url:
            dsl_data = get_dsl_from_url(args.url, args.token)
        else:
            parser.error('Please provide URL or --stdin')
        
        # Analyze
        analysis = analyze_dsl(dsl_data)
        
        # Output
        if args.format == 'json':
            print(json.dumps(analysis, ensure_ascii=False, indent=2))
        elif args.format == 'flat':
            print(format_flat(analysis))
        else:
            print(format_tree(analysis))
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()
