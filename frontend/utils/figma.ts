export type FetchFigmaNodeParams = {
  fileKey: string
  nodeId: string
  token: string
}

export type FigmaNodeResponse = {
  document: unknown
  components?: unknown
  styles?: unknown
  // Add more as needed
}

export const fetchFigmaNode = async ({fileKey, nodeId, token}: FetchFigmaNodeParams): Promise<FigmaNodeResponse> => {
  const url = `https://api.figma.com/v1/files/${fileKey}/nodes?ids=${encodeURIComponent(nodeId)}`
  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  })
  if (!res.ok) {
    const errText = await res.text()
    throw new Error(`Figma API error: ${res.status} ${res.statusText} - ${errText}`)
  }
  const data = await res.json()
  if (!data.nodes || !data.nodes[nodeId]) {
    throw new Error(`Node ${nodeId} not found in Figma file ${fileKey}`)
  }
  return data.nodes[nodeId]
} 