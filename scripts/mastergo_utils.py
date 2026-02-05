#!/usr/bin/env python3
"""
MasterGo utility functions.

Pure utility functions for DSL processing - no external dependencies.
Compatible with Python 3.6+

Usage:
  # As module
  from mastergo_utils import extract_texts, extract_navigations, build_component_tree
  
  # As CLI (for testing)
  cat dsl.json | python mastergo_utils.py texts
  cat dsl.json | python mastergo_utils.py navigations
  cat dsl.json | python mastergo_utils.py tree
"""

import json
import sys
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict, List, Any


# =============================================================================
# URL Parsing
# =============================================================================

def parse_mastergo_url(url: str) -> Optional[Dict[str, str]]:
    """
    Extract fileId and layerId from MasterGo URL.
    
    Example:
        >>> parse_mastergo_url("https://mastergo.com/file/155675508499265?layer_id=158:0002")
        {'fileId': '155675508499265', 'layerId': '158:0002'}
    """
    try:
        parsed = urlparse(url)
        file_id = next((s for s in parsed.path.split('/') if s.isdigit()), None)
        layer_id = parse_qs(parsed.query).get('layer_id', [None])[0]
        return {'fileId': file_id, 'layerId': layer_id} if file_id and layer_id else None
    except Exception:
        return None


def is_short_link(url: str) -> bool:
    """Check if URL is a MasterGo short link (/goto/)."""
    return '/goto/' in url


def is_valid_mastergo_url(url: str) -> bool:
    """Check if URL is a valid MasterGo URL."""
    try:
        parsed = urlparse(url)
        return ('mastergo' in parsed.netloc and 
                ('/goto/' in parsed.path or '/file/' in parsed.path))
    except Exception:
        return False


# =============================================================================
# DSL Extraction
# =============================================================================

def get_dsl_root(dsl_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get the actual DSL root from response (handles wrapped format)."""
    return dsl_data.get('dsl', dsl_data)


def extract_component_links(dsl_data: Dict[str, Any]) -> List[str]:
    """
    Extract component documentation links from DSL.
    
    Example:
        >>> extract_component_links(dsl_response)
        ['https://example.com/ant/button.mdx', ...]
    """
    # Check for pre-extracted links
    if 'componentDocumentLinks' in dsl_data:
        return dsl_data['componentDocumentLinks']
    
    links = set()
    root = get_dsl_root(dsl_data)
    
    def traverse(node: Optional[Dict]) -> None:
        if not node:
            return
        try:
            doc_links = node.get('componentInfo', {}).get('componentSetDocumentLink', [])
            for link in doc_links:
                if link:
                    links.add(link)
        except (TypeError, IndexError):
            pass
        for child in node.get('children', []):
            traverse(child)
    
    for node in root.get('nodes', []):
        traverse(node)
    if root.get('root'):
        traverse(root['root'])
    
    return list(links)


def extract_navigations(dsl_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract navigation targets from DSL.
    
    Example:
        >>> extract_navigations(dsl_response)
        [{'sourceId': '1:12', 'sourceName': 'Button', 'targetLayerId': '0:3'}]
    """
    navigations = []
    root = get_dsl_root(dsl_data)
    
    def traverse(node: Optional[Dict]) -> None:
        if not node:
            return
        for interaction in node.get('interactive', []):
            if interaction.get('type') == 'navigation' and interaction.get('targetLayerId'):
                navigations.append({
                    'sourceId': node.get('id'),
                    'sourceName': node.get('name'),
                    'targetLayerId': interaction['targetLayerId']
                })
        for child in node.get('children', []):
            traverse(child)
    
    for node in root.get('nodes', []):
        traverse(node)
    if root.get('root'):
        traverse(root['root'])
    
    return navigations


def extract_texts(dsl_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract all text content from DSL.
    
    Example:
        >>> extract_texts(dsl_response)
        [{'id': '1:12', 'name': 'Title', 'text': 'Hello World'}]
    """
    texts = []
    root = get_dsl_root(dsl_data)
    
    def traverse(node: Optional[Dict]) -> None:
        if not node:
            return
        if node.get('type') == 'TEXT' and node.get('characters'):
            texts.append({
                'id': node.get('id'),
                'name': node.get('name'),
                'text': node.get('characters'),
            })
        for child in node.get('children', []):
            traverse(child)
    
    for node in root.get('nodes', []):
        traverse(node)
    if root.get('root'):
        traverse(root['root'])
    
    return texts


def extract_tokens(dsl_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Extract design tokens from DSL.
    
    Example:
        >>> extract_tokens(dsl_response)
        {'--brand-primary': {'name': 'brand-primary', 'value': '#1890ff'}}
    """
    tokens = {}
    root = get_dsl_root(dsl_data)
    
    for token_id, token in root.get('localStyleMap', {}).items():
        variable = token.get('variable', f'--{token_id}')
        tokens[variable] = {
            'id': token_id,
            'name': token.get('name', ''),
            'type': token.get('type', ''),
            'value': token.get('value', ''),
        }
    
    return tokens


def build_component_tree(dsl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build simplified component tree from DSL.
    
    Example:
        >>> build_component_tree(dsl_response)
        [{'type': 'FRAME', 'name': 'Page', 'tag': 'div', 'children': [...]}]
    """
    root = get_dsl_root(dsl_data)
    
    def build_node(node: Optional[Dict]) -> Optional[Dict]:
        if not node:
            return None
        
        style = node.get('style', {})
        layout = node.get('layout', {})
        
        result = {
            'id': node.get('id'),
            'type': node.get('type'),
            'name': node.get('name'),
            'tag': style.get('tag', 'div'),
        }
        
        # Size
        width = layout.get('width', {})
        height = layout.get('height', {})
        if width and height:
            result['size'] = f"{width.get('value', '?')}x{height.get('value', '?')}"
        
        # Text
        if node.get('characters'):
            result['text'] = node.get('characters')
        
        # Component doc
        comp_info = node.get('componentInfo', {})
        doc_links = comp_info.get('componentSetDocumentLink', [])
        if doc_links:
            result['componentDoc'] = doc_links[0]
        
        # Navigation
        for action in node.get('interactive', []):
            if action.get('type') == 'navigation':
                result['navigateTo'] = action.get('targetLayerId')
        
        # Children
        children = node.get('children', [])
        if children:
            result['children'] = [build_node(c) for c in children if c]
        
        return result
    
    trees = []
    for node in root.get('nodes', []):
        tree = build_node(node)
        if tree:
            trees.append(tree)
    
    if root.get('root'):
        tree = build_node(root['root'])
        if tree:
            trees.append(tree)
    
    return trees


def get_node_styles(node: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get merged style properties from a node.
    
    Returns combined UI styles and layout styles.
    """
    style = node.get('style', {})
    return {
        **style.get('value', {}),
        **style.get('layoutStyles', {}),
    }


# =============================================================================
# CLI
# =============================================================================

def main():
    """CLI for testing utilities."""
    import argparse
    
    parser = argparse.ArgumentParser(description='MasterGo DSL utilities')
    parser.add_argument('command', choices=['texts', 'navigations', 'components', 'tokens', 'tree'],
                        help='Extraction command')
    parser.add_argument('--pretty', '-p', action='store_true', help='Pretty print output')
    
    args = parser.parse_args()
    
    try:
        dsl_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {e}", file=sys.stderr)
        sys.exit(1)
    
    if args.command == 'texts':
        result = extract_texts(dsl_data)
    elif args.command == 'navigations':
        result = extract_navigations(dsl_data)
    elif args.command == 'components':
        result = extract_component_links(dsl_data)
    elif args.command == 'tokens':
        result = extract_tokens(dsl_data)
    elif args.command == 'tree':
        result = build_component_tree(dsl_data)
    
    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent))


if __name__ == '__main__':
    main()
