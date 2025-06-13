const shapeList = [
  'shapes/svg/shape=1.svg', 'shapes/svg/shape=2.svg', 'shapes/svg/shape=3.svg', 'shapes/svg/shape=4.svg', 'shapes/svg/shape=5.svg', 'shapes/svg/shape=6.svg'
]
const SuggestionShapes = () => (
  <div style={{display: 'flex', gap: 24}}>
    {shapeList.map(shape => (
      <img key={shape} src={`/assets/${shape}`} alt='' style={{width: 48, height: 48}} />
    ))}
  </div>
)

export default SuggestionShapes 