# Deployment Instructions
## The Red Hand & The Eternal Throne: A Bard's Chronicle Website

This guide provides comprehensive instructions for deploying your book website to various hosting platforms.

## Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] Customized all book-specific content in `index.html`
- [ ] Added your book cover image to `images/book-cover.jpg`
- [ ] Updated meta tags and descriptions
- [ ] Tested the website locally
- [ ] Optimized images for web delivery
- [ ] Verified all links work correctly
- [ ] Tested responsive design on multiple devices

## Deployment Option 1: GitHub Pages (Recommended)

GitHub Pages is free and integrates seamlessly with version control.

### Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click "New Repository" or the "+" icon
3. Name your repository (e.g., `red-hand-chronicle-website`)
4. Make it public (required for free GitHub Pages)
5. Initialize with README (optional)
6. Click "Create repository"

### Step 2: Upload Your Files

**Option A: Web Interface**
1. Click "uploading an existing file" on your repository page
2. Drag all your website files into the upload area
3. Write a commit message: "Initial website upload"
4. Click "Commit changes"

**Option B: Git Command Line**
```bash
git clone https://github.com/yourusername/your-repository-name.git
cd your-repository-name
# Copy all your website files here
git add .
git commit -m "Initial website upload"
git push origin main
```

### Step 3: Enable GitHub Pages

1. Go to your repository settings
2. Scroll down to "Pages" section
3. Under "Source," select "Deploy from a branch"
4. Choose "main" branch and "/ (root)" folder
5. Click "Save"
6. Your site will be available at `https://yourusername.github.io/repository-name`

### Step 4: Custom Domain (Optional)

1. Purchase a domain from a domain registrar
2. In your repository, create a file named `CNAME`
3. Add your domain name (e.g., `redhandchronicle.com`)
4. Configure DNS settings with your domain provider:
   - Add CNAME record pointing to `yourusername.github.io`
5. Enable "Enforce HTTPS" in GitHub Pages settings

## Deployment Option 2: Netlify

Netlify offers excellent performance and easy deployment.

### Step 1: Prepare Your Repository

1. Upload your website files to GitHub (see GitHub Pages instructions above)
2. Ensure all files are in the repository root

### Step 2: Connect to Netlify

1. Go to [Netlify.com](https://www.netlify.com) and sign up
2. Click "New site from Git"
3. Choose GitHub and authorize Netlify
4. Select your repository
5. Configure build settings:
   - Build command: (leave empty)
   - Publish directory: (leave empty or use `/`)
6. Click "Deploy site"

### Step 3: Configure Custom Domain

1. Go to Site Settings → Domain management
2. Click "Add custom domain"
3. Enter your domain name
4. Follow DNS configuration instructions
5. Netlify will automatically handle SSL certificates

### Advanced Netlify Features

- **Form handling**: Add `netlify` attribute to contact forms
- **Redirects**: Create `_redirects` file for URL management
- **Functions**: Add serverless functions if needed

## Deployment Option 3: Traditional Web Hosting

For shared hosting, VPS, or dedicated servers.

### Step 1: Prepare Files

1. Ensure all files are optimized for production
2. Compress images if necessary
3. Minify CSS and JavaScript (optional)

### Step 2: Upload Files

**Via FTP/SFTP:**
1. Connect to your hosting account using FTP client
2. Navigate to your domain's public folder (usually `public_html` or `www`)
3. Upload all website files to this directory
4. Ensure `index.html` is in the root

**Via Hosting Control Panel:**
1. Access your hosting control panel
2. Use File Manager to upload files
3. Extract zip file if you uploaded an archive

### Step 3: Configure Domain

1. Point your domain to your hosting server
2. Update DNS A records if necessary
3. Enable SSL certificate through your hosting provider

## Deployment Option 4: Firebase Hosting

Google Firebase offers fast, secure hosting with CDN.

### Step 1: Install Firebase CLI

```bash
npm install -g firebase-tools
```

### Step 2: Initialize Project

```bash
firebase login
firebase init hosting
```

### Step 3: Configure

1. Select "Use an existing project" or create new
2. Set public directory to current directory (`.`)
3. Configure as single-page app: No
4. Set up automatic builds: Optional

### Step 4: Deploy

```bash
firebase deploy
```

## Performance Optimization

### Image Optimization

1. Compress images using tools like:
   - [TinyPNG](https://tinypng.com/)
   - [ImageOptim](https://imageoptim.com/)
   - [Squoosh](https://squoosh.app/)

2. Use appropriate formats:
   - JPEG for photos
   - PNG for graphics with transparency
   - WebP for modern browsers (with fallbacks)

### CSS and JavaScript Optimization

1. Minify files using tools like:
   - [CSS Minifier](https://cssminifier.com/)
   - [JavaScript Minifier](https://javascript-minifier.com/)

2. Combine files to reduce HTTP requests

### Content Delivery Network (CDN)

Consider using a CDN for faster global delivery:
- Cloudflare (free tier available)
- AWS CloudFront
- Google Cloud CDN

## Security Considerations

### HTTPS Setup

1. Always enable HTTPS/SSL
2. Use tools like [Let's Encrypt](https://letsencrypt.org/) for free certificates
3. Configure HTTP to HTTPS redirects

### Security Headers

Add security headers via hosting configuration:
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

## Monitoring and Analytics

### Google Analytics

1. Create Google Analytics account
2. Add tracking code to `index.html` before closing `</head>` tag:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_TRACKING_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_TRACKING_ID');
</script>
```

### Search Console

1. Verify your site with Google Search Console
2. Submit sitemap (create `sitemap.xml` if needed)
3. Monitor search performance

## Troubleshooting Common Issues

### Site Not Loading

1. Check DNS propagation (can take 24-48 hours)
2. Verify all files uploaded correctly
3. Check hosting account status
4. Review error logs if available

### HTTPS Certificate Issues

1. Wait for certificate provisioning (can take several hours)
2. Verify domain ownership
3. Check DNS configuration
4. Contact hosting support if issues persist

### Performance Issues

1. Test with tools like:
   - [Google PageSpeed Insights](https://pagespeed.web.dev/)
   - [GTmetrix](https://gtmetrix.com/)
   - [WebPageTest](https://www.webpagetest.org/)

2. Common fixes:
   - Optimize images
   - Enable gzip compression
   - Use browser caching
   - Minimize HTTP requests

## Maintenance

### Regular Updates

1. Keep content fresh and current
2. Update book information as needed
3. Monitor for broken links
4. Review analytics regularly

### Backup Strategy

1. Keep local copies of all files
2. Use version control (Git)
3. Regular backups of hosting account
4. Document any custom configurations

## Support Resources

- **GitHub Pages**: [GitHub Pages Documentation](https://docs.github.com/en/pages)
- **Netlify**: [Netlify Documentation](https://docs.netlify.com/)
- **Firebase**: [Firebase Hosting Documentation](https://firebase.google.com/docs/hosting)
- **General Web Development**: [MDN Web Docs](https://developer.mozilla.org/)

---

## Quick Deployment Summary

1. **Prepare**: Test locally, optimize files
2. **Choose Platform**: GitHub Pages (free) or Netlify (advanced features)
3. **Upload**: Push to repository or drag-and-drop
4. **Configure**: Set up custom domain and SSL
5. **Monitor**: Add analytics and monitor performance
6. **Maintain**: Regular updates and backups

Your book website should now be live and accessible to readers worldwide!