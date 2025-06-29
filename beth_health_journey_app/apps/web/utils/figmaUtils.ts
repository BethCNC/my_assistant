/**
 * Utility functions for working with Figma designs
 */

/**
 * Converts a Figma color object to CSS rgba format
 * @param color Figma color object with r,g,b,a values in 0-1 range
 * @returns CSS rgba string
 */
export const figmaColorToRgba = (color: { r: number; g: number; b: number; a: number }): string => {
  const { r, g, b, a } = color;
  return `rgba(${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)}, ${a})`;
};

/**
 * Converts a Figma color object to CSS hex format
 * @param color Figma color object with r,g,b values in 0-1 range
 * @returns CSS hex string
 */
export const figmaColorToHex = (color: { r: number; g: number; b: number }): string => {
  const { r, g, b } = color;
  const toHex = (value: number) => {
    const hex = Math.round(value * 255).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  };
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
};

/**
 * Extracts text styles from a Figma text node
 * @param textNode Figma text node
 * @returns Object with text style properties
 */
export const extractTextStyles = (textNode: any) => {
  if (!textNode || !textNode.style) return {};
  
  const { 
    fontFamily, 
    fontWeight, 
    fontSize, 
    lineHeightPx, 
    letterSpacing, 
    textCase, 
    textDecoration 
  } = textNode.style;
  
  return {
    fontFamily,
    fontWeight,
    fontSize: `${fontSize}px`,
    lineHeight: `${lineHeightPx}px`,
    letterSpacing: letterSpacing !== 0 ? `${letterSpacing}px` : 'normal',
    textTransform: 
      textCase === 'UPPER' ? 'uppercase' : 
      textCase === 'LOWER' ? 'lowercase' : 
      textCase === 'TITLE' ? 'capitalize' : 
      'none',
    textDecoration:
      textDecoration === 'UNDERLINE' ? 'underline' : 
      textDecoration === 'STRIKETHROUGH' ? 'line-through' : 
      'none'
  };
};

/**
 * Gets a Figma component URL
 * @param fileKey Figma file key
 * @param nodeId Figma node ID
 * @returns Figma component URL
 */
export const getFigmaComponentUrl = (fileKey: string, nodeId: string): string => {
  return `https://www.figma.com/file/${fileKey}?node-id=${nodeId}`;
};

/**
 * Parses Figma node ID from URL
 * @param url Figma URL
 * @returns Extracted node ID or null if not found
 */
export const parseNodeIdFromUrl = (url: string): string | null => {
  const nodeIdMatch = url.match(/node-id=([^&]+)/);
  return nodeIdMatch ? nodeIdMatch[1] : null;
};

/**
 * Parses Figma file key from URL
 * @param url Figma URL
 * @returns Extracted file key or null if not found
 */
export const parseFileKeyFromUrl = (url: string): string | null => {
  const fileKeyMatch = url.match(/file\/([^/?]+)/);
  return fileKeyMatch ? fileKeyMatch[1] : null;
}; 