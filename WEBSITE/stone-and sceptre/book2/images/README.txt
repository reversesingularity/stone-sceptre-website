# Image Specifications and Guidelines
## The Red Hand & The Eternal Throne: A Bard's Chronicle Website

This file contains specifications and guidelines for all images used in the book website.

## Required Images

### 1. Book Cover Image
- **Filename**: `book-cover.jpg`
- **Dimensions**: 600x900 pixels (2:3 aspect ratio)
- **Format**: JPEG
- **File Size**: Maximum 200KB
- **Description**: High-quality book cover image featuring Celtic/medieval design elements
- **Usage**: Main hero section, book preview modal, social media sharing
- **Color Palette**: Should complement the website's royal theme (#d4af37 gold, #1a1a2e dark blue)

### 2. Author Photo
- **Filename**: `author-photo.jpg`
- **Dimensions**: 400x400 pixels (1:1 aspect ratio)
- **Format**: JPEG
- **File Size**: Maximum 100KB
- **Description**: Professional author headshot
- **Usage**: About the Author section
- **Style**: Professional, clear background preferred

### 3. Character Portrait Placeholders
- **Filenames**: 
  - `character-theron.jpg`
  - `character-ewan.jpg`
  - `character-fenella.jpg`
  - `character-malcolm.jpg`
  - `character-morag.jpg`
  - `character-duncan.jpg`
- **Dimensions**: 300x400 pixels
- **Format**: JPEG
- **File Size**: Maximum 80KB each
- **Description**: Character illustrations or placeholder images
- **Usage**: Character gallery section
- **Style**: Medieval/Celtic theme consistent with book aesthetic

### 4. Background Textures (Optional)
- **Filenames**: 
  - `parchment-texture.jpg`
  - `stone-texture.jpg`
  - `celtic-border.png`
- **Dimensions**: Vary based on usage
- **Format**: JPEG for textures, PNG for borders with transparency
- **File Size**: Maximum 150KB each
- **Description**: Subtle background textures to enhance medieval atmosphere
- **Usage**: Section backgrounds, decorative elements

## Image Optimization Guidelines

### Quality Standards
1. **Resolution**: Optimize for web delivery while maintaining quality
2. **Compression**: Use 80-85% JPEG quality for photographs
3. **Progressive JPEG**: Enable progressive loading for better user experience
4. **Alt Text**: All images must have descriptive alt text for accessibility

### File Naming Convention
- Use lowercase letters only
- Separate words with hyphens (-)
- Be descriptive but concise
- Include image purpose in filename

Examples:
```
✅ Good:
- book-cover.jpg
- author-photo.jpg
- character-theron-portrait.jpg
- celtic-border-decoration.png

❌ Avoid:
- IMG_001.jpg
- photo.jpeg
- image1.png
- COVER.JPG
```

### Responsive Images
Consider creating multiple sizes for responsive design:

```
book-cover.jpg          (600x900 - desktop)
book-cover-medium.jpg   (400x600 - tablet)
book-cover-small.jpg    (200x300 - mobile)
```

## Technical Specifications

### Color Profile
- **Color Space**: sRGB
- **Bit Depth**: 8-bit per channel (24-bit total)
- **Profile**: Embed sRGB color profile

### Metadata
- Remove EXIF data for privacy and file size optimization
- Keep copyright information if applicable
- Add relevant keywords for SEO

### Format Guidelines

#### JPEG
- Use for photographs and complex images
- Quality setting: 80-85%
- Progressive encoding recommended
- Remove unnecessary metadata

#### PNG
- Use for graphics with transparency
- Use for simple graphics with few colors
- Optimize with tools like TinyPNG
- Consider PNG-8 for simple graphics

#### WebP (Future Enhancement)
- Modern format with better compression
- Provide JPEG/PNG fallbacks
- Use for supporting browsers

## Image Creation Tools

### Professional Tools
- **Adobe Photoshop**: Industry standard for image editing
- **Adobe Illustrator**: Vector graphics and logos
- **GIMP**: Free alternative to Photoshop
- **Canva**: User-friendly design tool for non-designers

### AI-Generated Images
If using AI tools for character portraits:
- **Midjourney**: High-quality artistic images
- **DALL-E**: Versatile AI image generation
- **Stable Diffusion**: Open-source alternative
- **Artbreeder**: Portrait generation and mixing

### Optimization Tools
- **TinyPNG**: Compress PNG and JPEG files
- **ImageOptim**: Mac-based image optimization
- **Squoosh**: Web-based image optimizer
- **GIMP**: Free image editor with export options

## Celtic/Medieval Design Elements

### Visual Themes
- Intricate knotwork patterns
- Ancient manuscripts and illuminated letters
- Medieval weaponry and armor
- Celtic crosses and symbols
- Stone textures and aged parchment
- Rich jewel tones (emerald, sapphire, ruby)
- Metallic accents (gold, bronze, silver)

### Color Palette Harmony
Ensure images complement the website's color scheme:
- **Primary Gold**: #d4af37
- **Deep Navy**: #1a1a2e
- **Accent Red**: #8b0000
- **Royal Purple**: #4b0082
- **Neutral Cream**: #f4f1e8

### Typography Integration
Images should work well with the chosen fonts:
- **Headers**: Cinzel (elegant serif)
- **Body**: Cormorant Garamond (readable serif)
- Ensure sufficient contrast between text and image backgrounds

## Accessibility Requirements

### Alt Text Guidelines
Write descriptive alt text for all images:

```html
<!-- Good examples -->
<img src="book-cover.jpg" alt="The Red Hand & The Eternal Throne book cover featuring a Celtic warrior with ornate armor against a misty highland backdrop">
<img src="character-theron.jpg" alt="Theron, a noble Celtic warrior with auburn hair and determined expression, wearing traditional Highland garb">
<img src="author-photo.jpg" alt="Author portrait showing [Author Name] in professional attire">

<!-- Avoid -->
<img src="image1.jpg" alt="image">
<img src="cover.jpg" alt="book cover">
```

### Color Contrast
- Ensure sufficient contrast between text and background images
- Test with accessibility tools
- Provide alternative content for users with visual impairments

## Performance Considerations

### File Size Targets
- **Hero Images**: Under 200KB
- **Character Portraits**: Under 80KB
- **Background Textures**: Under 150KB
- **Icons/Decorative**: Under 50KB

### Loading Strategy
1. **Critical Images**: Load immediately (book cover, hero background)
2. **Below-the-fold**: Lazy load character portraits and other images
3. **Progressive Enhancement**: Start with placeholder, load full quality

### CDN Considerations
For future optimization:
- Consider using image CDN (Cloudinary, ImageKit)
- Automatic format selection (WebP for supported browsers)
- Dynamic resizing based on device
- Global edge caching

## Legal and Copyright

### Original Artwork
- Ensure all images are original or properly licensed
- Keep documentation of image sources and licenses
- Credit artists appropriately

### Stock Photography
If using stock images:
- Purchase appropriate licenses
- Check commercial use permissions
- Avoid overused stock photos
- Ensure images align with book's unique aesthetic

### AI-Generated Content
- Review terms of service for AI image generators
- Ensure commercial usage rights
- Consider uniqueness and originality
- Document generation process for transparency

## Current Status

### Placeholder Images in Use
The website currently uses placeholder images with the following structure:

```css
/* CSS placeholder styling */
.placeholder-image {
    background: linear-gradient(135deg, #1a1a2e, #4b0082);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #d4af37;
    font-family: 'Cinzel', serif;
}
```

### Next Steps
1. **Book Cover**: Replace placeholder with actual book cover
2. **Author Photo**: Add professional author headshot
3. **Character Portraits**: Create or commission character artwork
4. **Background Textures**: Add subtle Celtic-themed textures
5. **Optimization**: Compress all images for web delivery

## Testing Checklist

Before deploying images:
- [ ] All images optimized for web
- [ ] Alt text added to all images
- [ ] File sizes within recommended limits
- [ ] Images display correctly on all devices
- [ ] Color palette consistency maintained
- [ ] Loading performance tested
- [ ] Accessibility compliance verified

---

Replace this README.txt with actual optimized images following the specifications above. The placeholder styling will automatically be replaced when real images are added to the images/ directory.