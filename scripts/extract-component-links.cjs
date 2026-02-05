/**
 * Extract component links and navigation targets from MasterGo DSL
 * 
 * Pure utility functions - no I/O dependencies.
 * Pass DSL object directly, returns extracted data.
 */

/**
 * Extract component documentation links from DSL
 * @param {object} dsl - DSL object (raw or wrapped { dsl: {...} })
 * @returns {string[]} - Unique documentation URLs
 * 
 * @example
 * extractComponentLinks(dslResponse)
 * // => ["https://example.com/ant/button.mdx", ...]
 */
function extractComponentLinks(dsl) {
  const links = new Set();
  const root = dsl.dsl || dsl;
  
  function traverse(node) {
    if (!node) return;
    
    const link = node?.componentInfo?.componentSetDocumentLink?.[0];
    if (link) links.add(link);
    
    node.children?.forEach(traverse);
  }
  
  root.nodes?.forEach(traverse);
  traverse(root);
  
  return [...links];
}

/**
 * Extract navigation targets from DSL
 * @param {object} dsl - DSL object
 * @returns {Array<{sourceId: string, targetLayerId: string}>}
 * 
 * @example
 * extractNavigations(dslResponse)
 * // => [{ sourceId: "1:12", targetLayerId: "0:3" }]
 */
function extractNavigations(dsl) {
  const navigations = [];
  const root = dsl.dsl || dsl;
  
  function traverse(node) {
    if (!node) return;
    
    node.interactive?.forEach(i => {
      if (i.type === 'navigation' && i.targetLayerId) {
        navigations.push({ sourceId: node.id, targetLayerId: i.targetLayerId });
      }
    });
    
    node.children?.forEach(traverse);
  }
  
  root.nodes?.forEach(traverse);
  traverse(root);
  
  return navigations;
}

module.exports = { extractComponentLinks, extractNavigations };
