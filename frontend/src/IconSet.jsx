const iconList = [
  'icon-paperclip.svg', 'icon-camera.svg', 'icon-send.svg', 'icon-plus.svg', 'icon-arrow.svg', 'icon-minus.svg', 'icon-trash.svg'
]
const IconSet = () => (
  <div style={{display: 'flex', gap: 24}}>
    {iconList.map(icon => (
      <img key={icon} src={`/assets/${icon}`} alt='' style={{width: 32, height: 32}} />
    ))}
  </div>
)

export default IconSet 