# Web App Settings Backup
## The Stone and the Sceptre Chronicles - Complete Configuration

**Backup Date**: October 1, 2025  
**Repository**: https://github.com/reversesingularity/stone-sceptre-website  
**Live URLs**:
- Book 1: https://reversesingularity.github.io/stone-sceptre-website/
- Book 2: https://reversesingularity.github.io/stone-sceptre-website/book2/

---

## 📁 **Repository Structure**

```
stone-sceptre-website/
├── index.html                  # Book 1 main page
├── styles.css                  # Book 1 styling
├── script.js                   # Book 1 functionality
├── qr-code.html               # Book 1 QR sharing
├── images/                     # Book 1 assets
├── book2/                      # Book 2 complete application
│   ├── index.html             # Book 2 main page
│   ├── qr-code.html           # Book 2 QR sharing
│   ├── styles.css             # Book 2 Celtic styling
│   ├── script.js              # Book 2 functionality
│   ├── images/                # Book 2 assets
│   │   ├── book-cover.jpg     # Book 2 cover image
│   │   └── README.txt         # Image specifications
│   ├── .gitignore             # Git ignore rules
│   ├── README.md              # Book 2 documentation
│   ├── deploy-instructions.md  # Deployment guide
│   ├── github-setup.md        # GitHub setup guide
│   ├── deployment-to-kermangild.md # Kerman Gild domain guide
│   ├── INTEGRATION-GUIDE.md   # Quick integration guide
│   ├── GITHUB-INTEGRATION.md  # GitHub integration guide
│   └── deploy-book2.ps1       # PowerShell deployment script
├── README.md                   # Main repository documentation
├── deploy-instructions.md      # Main deployment guide
├── github-setup.md            # GitHub setup instructions
├── deploy.bat                 # Windows deployment script
├── deploy.sh                  # Unix deployment script
├── .gitignore                 # Git ignore rules
├── CNAME                      # Custom domain configuration
└── stone-sceptre-website.zip  # Archive file
```

---

## 🌐 **Domain Configuration**

### GitHub Pages Settings
- **Repository**: reversesingularity/stone-sceptre-website
- **Branch**: main
- **Directory**: / (root)
- **Custom Domain**: Configured via CNAME file
- **HTTPS**: Enforced

### DNS Configuration
- **CNAME File Content**: [Check CNAME file for domain]
- **GitHub Pages URL**: https://reversesingularity.github.io/stone-sceptre-website/

---

## 🎨 **Design System Configuration**

### Book 1: The Stone and the Sceptre
**Color Palette**:
- Primary: Ancient manuscript theme
- Typography: Cinzel, Cormorant Garamond
- Effects: Divine lightning, Celtic knotwork

### Book 2: The Red Hand & The Eternal Throne
**Color Palette**:
```css
:root {
    --primary-gold: #d4af37;
    --dark-blue: #1a1a2e;
    --deep-blue: #16213e;
    --accent-red: #8b0000;
    --royal-purple: #4b0082;
    --light-gold: #f4e5a1;
    --medium-gold: #e6c969;
    --dark-gold: #b8941f;
    --cream: #f5f5dc;
    --text-light: #f5f5dc;
    --text-dark: #2c2c2c;
}
```

**Typography**:
- Headers: 'Cinzel', serif
- Body: 'Cormorant Garamond', serif
- Google Fonts URL: https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Cormorant+Garamond:wght@400;600;700&display=swap

---

## 📱 **Technical Configuration**

### HTML5 Meta Tags (Book 2)
```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Red Hand & The Eternal Throne: A Bard's Chronicle</title>
<meta name="description" content="Book 2 of The Stone and the Sceptre Chronicles - The epic tale of Gathelus and Princess Scota establishing the Hebrew-Celtic kingdom in ancient Iberia, featuring divine providence, supernatural warfare, and the fulfillment of ancient prophecies.">
```

### CSS Framework
- **Framework**: Pure CSS3 (no external frameworks)
- **Features**: CSS Grid, Flexbox, CSS Variables, Animations
- **Responsive**: Mobile-first design with breakpoints
- **Browser Support**: Modern browsers with fallbacks

### JavaScript Configuration
- **Framework**: Vanilla JavaScript (ES6+)
- **Features**: Intersection Observer, Modern APIs
- **Compatibility**: Polyfills included for older browsers

---

## 🔗 **Navigation Structure**

### Book 1 Navigation
```html
<nav class="main-nav">
    <ul>
        <li><a href="#synopsis">Synopsis</a></li>
        <li><a href="#characters">Characters</a></li>
        <li><a href="#chapters">Chapters</a></li>
        <li><a href="#world">World</a></li>
        <li><a href="#book-series">Book Series</a></li>
        <li><a href="#author">Author</a></li>
        <li><a href="book2/" class="book2-link">📖 Book 2</a></li>
    </ul>
</nav>
```

### Book 2 Navigation
```html
<ul class="nav-menu">
    <li><a href="#home">Home</a></li>
    <li><a href="#synopsis">Synopsis</a></li>
    <li><a href="#characters">Characters</a></li>
    <li><a href="#chapters">Chapters</a></li>
    <li><a href="#author">Author</a></li>
    <li><a href="./qr-code.html">Share</a></li>
</ul>
```

### Series Cross-Navigation
- **Book 1 → Book 2**: Via navigation menu and Book Series section
- **Book 2 → Book 1**: Via series banner at top of page

---

## 🖼️ **Asset Configuration**

### Image Specifications (Book 2)
- **Book Cover**: 600x900 pixels, JPEG, max 200KB
- **Character Images**: 300x400 pixels, JPEG, max 80KB each
- **Format**: JPEG for photos, PNG for graphics with transparency
- **Optimization**: Compressed for web delivery

### Image Locations
- **Book 1 Images**: `/images/`
- **Book 2 Images**: `/book2/images/`
- **Book Cover**: `/book2/images/book-cover.jpg`

---

## 📊 **Analytics & SEO Configuration**

### SEO Meta Tags (Book 2)
```html
<meta property="og:title" content="The Red Hand & The Eternal Throne: A Bard's Chronicle">
<meta property="og:description" content="Book 2 of The Stone and the Sceptre Chronicles">
<meta property="og:type" content="website">
<meta property="og:url" content="https://reversesingularity.github.io/stone-sceptre-website/book2/">
```

### Structured Data
- **Schema.org**: Book schema markup
- **JSON-LD**: Structured data for search engines

---

## 🔧 **Development Configuration**

### Git Configuration
```bash
git remote -v
# origin  https://github.com/reversesingularity/stone-sceptre-website.git (fetch)
# origin  https://github.com/reversesingularity/stone-sceptre-website.git (push)
```

### Branch Strategy
- **Main Branch**: `main` (production)
- **Deployment**: Direct push to main triggers GitHub Pages build

### Local Development
```bash
# Local server for testing
python -m http.server 8000
# Access: http://localhost:8000
```

---

## 🚀 **Deployment Configuration**

### GitHub Pages Settings
- **Source**: Deploy from branch `main` / (root)
- **Custom Domain**: [Check CNAME file]
- **Enforce HTTPS**: Enabled
- **Build Type**: Static site

### Deployment Scripts
- **PowerShell**: `deploy-book2.ps1`
- **Batch**: `deploy.bat`
- **Shell**: `deploy.sh`

### Manual Deployment Steps
1. Clone repository: `git clone https://github.com/reversesingularity/stone-sceptre-website.git`
2. Make changes
3. Add files: `git add .`
4. Commit: `git commit -m "Description"`
5. Push: `git push origin main`

---

## 🔒 **Security Configuration**

### HTTPS Configuration
- **SSL Certificate**: Auto-managed by GitHub Pages
- **Redirect**: HTTP automatically redirects to HTTPS
- **Security Headers**: Standard GitHub Pages headers

### Content Security
- **No External Dependencies**: All resources self-hosted except Google Fonts
- **CORS**: Same-origin policy enforced
- **XSS Protection**: Content sanitized

---

## 📦 **Dependencies**

### External Dependencies
- **Google Fonts**: Cinzel, Cormorant Garamond
- **QR Code APIs**: Multiple fallback services
  - Google Charts API
  - QR Server API
  - QuickChart API

### Internal Dependencies
- **CSS**: No external frameworks
- **JavaScript**: No external libraries
- **Images**: Self-hosted assets

---

## 🔄 **Backup & Recovery**

### Current Backup Locations
1. **GitHub Repository**: https://github.com/reversesingularity/stone-sceptre-website
2. **Local Copy**: `C:\temp\stone-sceptre-website\`
3. **Source Files**: `C:\Users\cmodi.000\book_writer_ai_toolkit\output\book_2_red_hand_chronicle\web-app\`

### Recovery Process
1. Clone from GitHub: `git clone https://github.com/reversesingularity/stone-sceptre-website.git`
2. Or restore from local backup
3. Or rebuild from source files in book_writer_ai_toolkit

---

## 📋 **Content Configuration**

### Book 1 Content
- **Title**: The Stone and the Sceptre: A Scribe's Tale
- **Characters**: Jeremiah, Tea Tephi, Scota, Gathelus, Baruch ben Neriah
- **Setting**: 587 BCE, Jerusalem to Ireland

### Book 2 Content
- **Title**: The Red Hand & The Eternal Throne: A Bard's Chronicle
- **Characters**: Gathelus, Princess Scota, Taliesin, Azariah ben Hilkiah, Viriatus
- **Setting**: 6th Century BCE, Celtiberian Iberia
- **Chapters**: 16 chapters plus prologue and epilogue

---

## 🎯 **Performance Configuration**

### Optimization Settings
- **Image Compression**: 80-85% JPEG quality
- **CSS Minification**: Not applied (for readability)
- **JavaScript Minification**: Not applied (for maintainability)
- **Lazy Loading**: Implemented for images
- **CDN**: GitHub Pages global CDN

### Performance Targets
- **First Contentful Paint**: < 2 seconds
- **Largest Contentful Paint**: < 4 seconds
- **Cumulative Layout Shift**: < 0.1

---

## 📧 **Contact & Support**

### Repository Management
- **Owner**: reversesingularity
- **Repository**: stone-sceptre-website
- **Access**: Public repository

### Documentation Locations
- **Main README**: `/README.md`
- **Book 2 README**: `/book2/README.md`
- **Deployment Guides**: Multiple .md files in both directories

---

## 🔄 **Last Updated**

- **Backup Created**: October 1, 2025
- **Last Commit**: "Complete series integration: Add Book 2 navigation, update README, and add cross-linking"
- **Current Version**: Production ready with full Book 2 integration

---

**Note**: This backup contains all critical configuration information needed to restore, modify, or recreate the web applications. Keep this document updated when making significant changes to the websites.