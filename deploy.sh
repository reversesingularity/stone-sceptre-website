#!/bin/bash
# Deploy script for The Stone and the Sceptre website

echo "🏰 Preparing The Stone and the Sceptre for deployment..."

# Create deployment package
echo "📦 Creating deployment package..."
zip -r "stone-sceptre-website.zip" index.html styles.css script.js images/ -x "*.DS_Store" "*.git*"

echo "✅ Deployment package created: stone-sceptre-website.zip"
echo ""
echo "🚀 Next steps:"
echo "1. Choose a hosting provider (GitHub Pages, Netlify, or traditional hosting)"
echo "2. Upload the zip file or individual files"
echo "3. Configure your domain settings in Squarespace"
echo ""
echo "📝 See deploy-instructions.md for detailed steps!"
