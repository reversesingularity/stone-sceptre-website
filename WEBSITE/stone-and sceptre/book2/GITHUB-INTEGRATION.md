# GitHub Integration Guide: Adding Book 2 to stone-sceptre-website

## 🎯 **Goal**: Add Book 2 to your existing GitHub Pages site

**Current Site**: `https://reversesingularity.github.io/stone-sceptre-website/`  
**Book 2 URL**: `https://reversesingularity.github.io/stone-sceptre-website/book2/`

## 📁 **Recommended Directory Structure**

```
stone-sceptre-website/
├── index.html              ← Book 1 (current site)
├── styles.css              ← Book 1 styles  
├── script.js               ← Book 1 functionality
├── qr-code.html           ← Book 1 QR code
├── images/                 ← Book 1 images
├── book2/                  ← NEW: Book 2 directory
│   ├── index.html         ← Book 2 main page
│   ├── qr-code.html       ← Book 2 QR sharing
│   ├── styles.css         ← Book 2 Celtic styling
│   ├── script.js          ← Book 2 functionality
│   └── images/            ← Book 2 images
│       └── book-cover.jpg
├── README.md
└── other existing files...
```

## 🚀 **Step-by-Step Integration**

### Step 1: Clone Your Repository
```bash
git clone https://github.com/reversesingularity/stone-sceptre-website.git
cd stone-sceptre-website
```

### Step 2: Create Book 2 Directory
```bash
mkdir book2
mkdir book2/images
```

### Step 3: Copy Book 2 Files
Copy these files from your Book 2 web app to the `book2/` directory:
- `index.html` → `book2/index.html`
- `qr-code.html` → `book2/qr-code.html`  
- `styles.css` → `book2/styles.css`
- `script.js` → `book2/script.js`
- `images/book-cover.jpg` → `book2/images/book-cover.jpg`

### Step 4: Update Your Main Site Navigation
Add Book 2 navigation to your main `index.html`:

```html
<!-- Add this to your main site navigation -->
<nav class="main-navigation">
    <ul>
        <li><a href="/">Book 1: The Stone and the Sceptre</a></li>
        <li><a href="/book2/">Book 2: The Red Hand & The Eternal Throne</a></li>
    </ul>
</nav>

<!-- Or add a book series section -->
<section class="book-series">
    <h2>The Stone and the Sceptre Chronicles</h2>
    <div class="books-grid">
        <div class="book-card current">
            <h3>Book 1: The Stone and the Sceptre</h3>
            <p>A Scribe's Tale</p>
            <a href="/" class="btn">Current Page</a>
        </div>
        <div class="book-card">
            <h3>Book 2: The Red Hand & The Eternal Throne</h3>
            <p>A Bard's Chronicle</p>
            <a href="/book2/" class="btn">Explore Book 2</a>
        </div>
    </div>
</section>
```

### Step 5: Commit and Push
```bash
git add .
git commit -m "Add Book 2: The Red Hand & The Eternal Throne web app"
git push origin main
```

## 🔗 **Final URLs After Integration**

- **Book 1**: `https://reversesingularity.github.io/stone-sceptre-website/`
- **Book 2**: `https://reversesingularity.github.io/stone-sceptre-website/book2/`
- **Book 2 QR**: `https://reversesingularity.github.io/stone-sceptre-website/book2/qr-code.html`

## 🎨 **Navigation Styling Suggestions**

Add this CSS to your main `styles.css` for book series navigation:

```css
.book-series {
    padding: 4rem 0;
    text-align: center;
}

.books-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.book-card {
    background: rgba(0, 0, 0, 0.4);
    padding: 2rem;
    border-radius: 15px;
    border: 2px solid #d4af37;
    transition: transform 0.3s ease;
}

.book-card:hover {
    transform: translateY(-5px);
}

.book-card.current {
    border-color: #fff;
    background: rgba(212, 175, 55, 0.1);
}

.book-card h3 {
    color: #d4af37;
    font-family: 'Cinzel', serif;
    margin-bottom: 0.5rem;
}

.book-card .btn {
    display: inline-block;
    padding: 0.8rem 1.5rem;
    background: #d4af37;
    color: #1a1a2e;
    text-decoration: none;
    border-radius: 25px;
    margin-top: 1rem;
    transition: all 0.3s ease;
}

.book-card .btn:hover {
    background: #f4e5a1;
    transform: translateY(-2px);
}
```

## ✅ **Quick Deploy Script**

Create this script to automate the process:

```bash
#!/bin/bash
# deploy-book2.sh

echo "🚀 Deploying Book 2 to GitHub Pages..."

# Create book2 directory if it doesn't exist
mkdir -p book2/images

# Copy Book 2 files (adjust source path as needed)
cp "C:/Users/cmodi.000/book_writer_ai_toolkit/output/book_2_red_hand_chronicle/web-app/index.html" book2/
cp "C:/Users/cmodi.000/book_writer_ai_toolkit/output/book_2_red_hand_chronicle/web-app/qr-code.html" book2/
cp "C:/Users/cmodi.000/book_writer_ai_toolkit/output/book_2_red_hand_chronicle/web-app/styles.css" book2/
cp "C:/Users/cmodi.000/book_writer_ai_toolkit/output/book_2_red_hand_chronicle/web-app/script.js" book2/
cp "C:/Users/cmodi.000/book_writer_ai_toolkit/output/book_2_red_hand_chronicle/web-app/images/book-cover.jpg" book2/images/

# Git operations
git add .
git commit -m "Add Book 2: The Red Hand & The Eternal Throne"
git push origin main

echo "✅ Book 2 deployed to GitHub Pages!"
echo "🌐 Available at: https://reversesingularity.github.io/stone-sceptre-website/book2/"
```

## 📋 **Deployment Checklist**

- [ ] Clone your stone-sceptre-website repository
- [ ] Create `book2/` directory structure
- [ ] Copy all Book 2 web app files to `book2/`
- [ ] Add navigation links to main site
- [ ] Test locally with `python -m http.server`
- [ ] Commit and push to GitHub
- [ ] Verify GitHub Pages deployment
- [ ] Test both URLs work correctly
- [ ] Update README.md to mention Book 2

## 🎉 **Benefits of This Setup**

✅ **Single Domain**: Both books under one GitHub Pages site  
✅ **Easy Navigation**: Readers can move between books seamlessly  
✅ **Consistent Branding**: Unified Stone and Sceptre Chronicles experience  
✅ **SEO Friendly**: Related content under same domain authority  
✅ **Cost Effective**: Free GitHub Pages hosting for entire series  

## 🔧 **Maintenance Notes**

- **Book Updates**: Edit files in respective directories (`/` for Book 1, `/book2/` for Book 2)
- **Shared Resources**: Consider moving common images/fonts to a shared `/assets/` directory
- **Series Navigation**: Add consistent navigation between books
- **Analytics**: Use same Google Analytics tracking for both books

Your readers will be able to explore both books in "The Stone and the Sceptre Chronicles" from a single, professional website!