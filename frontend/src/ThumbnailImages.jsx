const thumbList = [
  'thumb-1.jpg', 'thumb-2.jpg', 'thumb-3.jpg', 'thumb-4.jpg'
]
const ThumbnailImages = () => (
  <div style={{display: 'flex', gap: 16}}>
    {thumbList.map(thumb => (
      <img key={thumb} src={`/assets/${thumb}`} alt='' style={{width: 48, height: 48, borderRadius: 8}} />
    ))}
  </div>
)

export default ThumbnailImages 