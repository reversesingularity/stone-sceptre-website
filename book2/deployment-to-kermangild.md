# Deployment Guide: Adding Book 2 to kermangildpublishing.org

This guide explains how to add "The Red Hand & The Eternal Throne" web app to your existing `kermangildpublishing.org` domain.

## 🎯 **Recommended Setup: Subdirectory Structure**

### Option A: `/red-hand-chronicle/` (Recommended)
**Final URL**: `https://kermangildpublishing.org/red-hand-chronicle/`

### Option B: `/books/red-hand/`
**Final URL**: `https://kermangildpublishing.org/books/red-hand/`

### Option C: `/chronicles/book2/`
**Final URL**: `https://kermangildpublishing.org/chronicles/book2/`

---

## 📁 **Step 1: Prepare Your File Structure**

Your web app files are ready for deployment. Here's what you'll upload:

```
kermangildpublishing.org/
├── (your existing site files)
└── red-hand-chronicle/          ← New subdirectory
    ├── index.html              ← Book 2 main page
    ├── qr-code.html           ← QR sharing page
    ├── styles.css             ← All styling
    ├── script.js              ← Interactive features
    ├── images/
    │   ├── book-cover.jpg     ← Book cover image
    │   └── README.txt         ← Image specifications
    ├── assets/                ← Additional assets (if any)
    ├── README.md              ← Project documentation
    └── .gitignore             ← Git ignore rules
```

---

## 🌐 **Step 2: Upload Files to Your Domain**

### Method 1: FTP/SFTP Upload
1. Connect to your hosting account via FTP client (FileZilla, WinSCP, etc.)
2. Navigate to your domain's public folder (usually `public_html` or `www`)
3. Create a new folder: `red-hand-chronicle`
4. Upload all web app files to this new folder

### Method 2: Hosting Control Panel
1. Log into your hosting control panel (cPanel, Plesk, etc.)
2. Open File Manager
3. Navigate to your domain's public directory
4. Create new folder: `red-hand-chronicle`
5. Upload all web app files to this folder

### Method 3: Git Deployment (if supported)
1. Create a repository with your web app files
2. Use your hosting provider's Git integration
3. Deploy to the `red-hand-chronicle` subdirectory

---

## 🔗 **Step 3: Link from Your Main Site**

Add navigation links from your main `kermangildpublishing.org` site to the new book page:

### Example Navigation Link
```html
<a href="/red-hand-chronicle/">The Red Hand & The Eternal Throne</a>
```

### Example Book Gallery Entry
```html
<div class="book-card">
    <h3>The Red Hand & The Eternal Throne</h3>
    <p>Book 2 of The Stone and the Sceptre Chronicles</p>
    <a href="/red-hand-chronicle/" class="btn">Explore Book</a>
</div>
```

---

## 📱 **Step 4: Update QR Code Configuration**

The QR code page will automatically detect the correct URL, but you can verify it points to:
`https://kermangildpublishing.org/red-hand-chronicle/`

---

## 🔧 **Step 5: Test Your Deployment**

After uploading, test these URLs:

1. **Main Book Page**: `https://kermangildpublishing.org/red-hand-chronicle/`
2. **QR Code Page**: `https://kermangildpublishing.org/red-hand-chronicle/qr-code.html`
3. **All Navigation**: Verify all internal links work properly
4. **Mobile Responsive**: Test on different devices
5. **Images Loading**: Ensure book cover and assets load correctly

---

## 🌐 **Alternative: Subdomain Setup**

If you prefer a subdomain instead of a subdirectory:

### Step 1: Create Subdomain
1. In your hosting control panel, create a new subdomain
2. Choose name: `red-hand.kermangildpublishing.org` or `book2.kermangildpublishing.org`

### Step 2: Upload Files
1. Upload web app files to the subdomain's directory
2. No path changes needed for subdomain setup

### Step 3: DNS Configuration
- DNS will typically auto-configure
- May take 24-48 hours to propagate globally

---

## 📊 **SEO and Analytics Setup**

### Update Meta Tags
The web app already includes proper meta tags, but consider adding:

```html
<!-- In index.html <head> section -->
<meta property="og:url" content="https://kermangildpublishing.org/red-hand-chronicle/">
<meta property="og:site_name" content="Kerman Gild Publishing">
<link rel="canonical" href="https://kermangildpublishing.org/red-hand-chronicle/">
```

### Google Analytics
If you have Google Analytics on your main site, add the same tracking code to the book pages.

### Search Console
Submit the new URLs to Google Search Console:
- `https://kermangildpublishing.org/red-hand-chronicle/`
- `https://kermangildpublishing.org/red-hand-chronicle/qr-code.html`

---

## 🔒 **Security Considerations**

### HTTPS
- Your existing SSL certificate should cover subdirectories automatically
- Verify HTTPS works: `https://kermangildpublishing.org/red-hand-chronicle/`

### File Permissions
- Set appropriate file permissions (644 for files, 755 for directories)
- Ensure web server can read all files

---

## 📋 **Deployment Checklist**

- [ ] Choose subdirectory name (`red-hand-chronicle` recommended)
- [ ] Create directory on your web server
- [ ] Upload all web app files
- [ ] Test main page loads correctly
- [ ] Test QR code page functionality
- [ ] Verify all internal navigation works
- [ ] Test on mobile devices
- [ ] Add navigation links from main site
- [ ] Update any analytics tracking
- [ ] Submit to search engines
- [ ] Test HTTPS functionality

---

## 🚀 **Quick Deploy Commands**

If you have SSH access to your server:

```bash
# Navigate to your web directory
cd /path/to/public_html

# Create subdirectory
mkdir red-hand-chronicle

# Upload files (example with scp)
scp -r /local/path/to/web-app/* user@server:/path/to/public_html/red-hand-chronicle/

# Set permissions
chmod -R 644 red-hand-chronicle/*
find red-hand-chronicle -type d -exec chmod 755 {} \;
```

---

## 📞 **Need Help?**

If you encounter any issues during deployment:

1. **Check file paths**: Ensure all relative paths are correct
2. **Verify permissions**: Make sure web server can read files
3. **Test locally first**: Use the local server setup to verify everything works
4. **Contact hosting support**: They can assist with subdirectory setup

---

## 🎉 **After Successful Deployment**

Your book will be accessible at:
**`https://kermangildpublishing.org/red-hand-chronicle/`**

Readers can:
- ✅ View the complete book website
- ✅ Generate QR codes for sharing
- ✅ Navigate seamlessly between pages
- ✅ Experience the full Celtic/medieval theme
- ✅ Access on any device (mobile responsive)

The web app is now ready to showcase "The Red Hand & The Eternal Throne: A Bard's Chronicle" as part of your publishing website!