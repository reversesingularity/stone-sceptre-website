@echo off
echo 🏰 Preparing The Stone and the Sceptre for deployment...
echo.

echo 📦 Creating deployment package...
powershell -Command "Compress-Archive -Path 'index.html','styles.css','script.js','images' -DestinationPath 'stone-sceptre-website.zip' -Force"

echo ✅ Deployment package created: stone-sceptre-website.zip
echo.
echo 🚀 Next steps:
echo 1. Choose a hosting provider (GitHub Pages, Netlify, or traditional hosting)
echo 2. Upload the zip file or individual files  
echo 3. Configure your domain settings in Squarespace
echo.
echo 📝 See deploy-instructions.md for detailed steps!
pause
