import React from 'react'

const TestImageCard = ({ product }) => {
  console.log('TestImageCard rendering with product:', product)
  console.log('Image path:', product.image)
  
  return (
    <div style={{ 
      border: '2px solid #e91e63', 
      borderRadius: '12px', 
      padding: '20px', 
      margin: '20px',
      backgroundColor: 'white',
      boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
      maxWidth: '300px'
    }}>
      {/* Product Image */}
      <div style={{ marginBottom: '16px', textAlign: 'center' }}>
        <h4 style={{ margin: '0 0 8px 0', color: '#666' }}>Testing Image:</h4>
        <img
          src={product.image}
          alt={product.name}
          style={{
            width: '100%',
            height: '250px',
            objectFit: 'cover',
            borderRadius: '8px',
            border: '1px solid #ddd'
          }}
          onLoad={() => {
            console.log('✅ SUCCESS: Image loaded successfully:', product.image)
            console.log('Image dimensions:', event.target.naturalWidth, 'x', event.target.naturalHeight)
          }}
          onError={(event) => {
            console.log('❌ ERROR: Image failed to load:', product.image)
            console.log('Error details:', event)
          }}
        />
      </div>
      
      {/* Product Info */}
      <div style={{ textAlign: 'center' }}>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: 'bold', color: '#333' }}>
          {product.name}
        </h3>
        <p style={{ margin: '0 0 8px 0', color: '#666' }}>
          Size: {product.size} | Color: {product.color}
        </p>
        <p style={{ margin: '0', fontSize: '24px', fontWeight: 'bold', color: '#e91e63' }}>
          ${product.price}
        </p>
        <p style={{ margin: '8px 0 0 0', fontSize: '12px', color: '#999' }}>
          Image: {product.image}
        </p>
      </div>
    </div>
  )
}

export default TestImageCard
