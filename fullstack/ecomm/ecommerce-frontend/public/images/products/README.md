# Product Images Directory

This directory contains product images for the ecommerce frontend.

## Current Structure
- `placeholder.svg` - Default placeholder image used when product images fail to load
- `floral-dress.svg` - SVG placeholder for Floral Summer Dress
- `white-blouse.svg` - SVG placeholder for Elegant White Blouse
- `denim-jacket.svg` - SVG placeholder for Classic Denim Jacket
- `maxi-dress.svg` - SVG placeholder for Maxi Evening Dress
- `pencil-skirt.svg` - SVG placeholder for Professional Pencil Skirt
- `knit-sweater.svg` - SVG placeholder for Cozy Knit Sweater

## Current Status
✅ **SVG Placeholder Images**: All 6 product images are now loading as colorful SVG placeholders
✅ **No External Dependencies**: All images are served locally from the public directory
✅ **Consistent Design**: All placeholders follow the same design pattern with product names

## Adding Real Product Photos

To replace the SVG placeholders with real product photos:

1. **Supported Formats**: JPG, PNG, WebP (recommended for better performance)
2. **Recommended Dimensions**: 300x400px (aspect ratio 3:4)
3. **File Naming**: Use the exact same names as the SVG files:
   - `floral-dress.jpg` (or .png/.webp)
   - `white-blouse.jpg`
   - `denim-jacket.jpg`
   - `maxi-dress.jpg`
   - `pencil-skirt.jpg`
   - `knit-sweater.jpg`

4. **Image Optimization**: 
   - Compress images to reduce file size
   - Use WebP format for best performance
   - Keep file sizes under 100KB when possible

## How It Works

The system automatically detects image files and uses them in this priority order:
1. **Real product images** (JPG/PNG/WebP) - if they exist
2. **SVG placeholders** - as fallback if real images don't exist
3. **Generic placeholder** - as final fallback if everything fails

## Usage in Components

Images are referenced in components like this:
```jsx
{
  id: 1,
  name: "Floral Summer Dress",
  price: 89.99,
  image: "/images/products/floral-dress.jpg", // Will automatically use .svg if .jpg doesn't exist
  size: "M",
  color: "Blue"
}
```

## Development vs Production

- **Development**: Images are served from the `public` directory
- **Production**: Images are copied to the build output and served as static assets

## Next Steps

1. **Add real photos**: Replace SVG files with actual product photos
2. **Optimize images**: Compress and convert to WebP for better performance
3. **Add more products**: Create additional image files for new products
