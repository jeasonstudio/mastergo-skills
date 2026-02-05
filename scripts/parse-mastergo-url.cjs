/**
 * Parse MasterGo URL to extract fileId and layerId
 * 
 * Pure utility function - no I/O dependencies.
 * For short links, pass directly to mcp__getDsl({ shortLink }) instead.
 * 
 * @example
 * parseMasterGoUrl("https://mastergo.com/file/155675508499265?layer_id=158:0002")
 * // => { fileId: "155675508499265", layerId: "158:0002" }
 */

/**
 * @param {string} url - MasterGo full URL
 * @returns {{ fileId: string, layerId: string } | null}
 */
function parseMasterGoUrl(url) {
  try {
    const urlObj = new URL(url);
    
    // Extract fileId: numeric segment in path
    const fileId = urlObj.pathname.split('/').find(s => /^\d+$/.test(s));
    
    // Extract layerId from query params
    const layerId = urlObj.searchParams.get('layer_id');
    
    if (!fileId || !layerId) return null;
    
    return { fileId, layerId };
  } catch {
    return null;
  }
}

/**
 * Check if URL is a MasterGo short link
 * @param {string} url
 * @returns {boolean}
 */
function isShortLink(url) {
  return url.includes('/goto/');
}

/**
 * Check if URL is a valid MasterGo URL
 * @param {string} url
 * @returns {boolean}
 */
function isValidMasterGoUrl(url) {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname.includes('mastergo') && 
           (urlObj.pathname.includes('/goto/') || urlObj.pathname.includes('/file/'));
  } catch {
    return false;
  }
}

module.exports = { parseMasterGoUrl, isShortLink, isValidMasterGoUrl };
