import {fetchFigmaNode} from './figma'

const fileKey = '8dak7GzHKjjMohUxhu9M9A'
const nodeId = '4002:13310'
const token = process.env.FIGMA_ACCESS_TOKEN || ''

if (!token) {
  console.error('FIGMA_ACCESS_TOKEN not set in environment')
  process.exit(1)
}

fetchFigmaNode({fileKey, nodeId, token})
  .then(node => {
    console.log('Figma node:', JSON.stringify(node, null, 2))
  })
  .catch(err => {
    console.error('Error fetching Figma node:', err)
    process.exit(1)
  }) 