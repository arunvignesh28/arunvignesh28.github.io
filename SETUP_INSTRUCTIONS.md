# Complete Setup Instructions for Your Research Website

## 🎯 Quick Setup (5 minutes)

### Step 1: Repository Setup
1. **Fork/Download** this repository
2. **Rename** it to `arunvignesh28.github.io` (replace with your GitHub username)
3. **Clone** to your local machine:
   ```bash
   git clone https://github.com/arunvignesh28/arunvignesh28.github.io.git
   cd arunvignesh28.github.io
   ```

### Step 2: Basic Configuration
1. **Edit `_config.yml`** with your information:
   ```yaml
   title: "Your Name - PhD Researcher"
   author:
     name: "Your Name"
     email: "your.email@university.edu"
     university: "Your University"
   social:
     github: "yourusername"
     linkedin: "yourprofile"
     google_scholar: "YOUR_SCHOLAR_ID"
   ```

2. **Update `index.html`** - Replace placeholder text:
   - Your name and title in the hero section
   - Your research description
   - Your biography in the About section
   - Your research areas
   - Contact information

### Step 3: Add Your Content
1. **Profile Image**: Add `images/profile.jpg` (250x250px recommended)
2. **CV**: Add `files/cv.pdf`
3. **Publications**: Edit the publications section in `index.html`
4. **Favicon**: Add `images/favicon.ico`

### Step 4: Deploy
1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial setup of research website"
   git push origin main
   ```

2. **Enable GitHub Pages**:
   - Go to Settings → Pages
   - Select "Deploy from branch" → "main"
   - Wait 5-10 minutes

3. **Visit your site**: `https://arunvignesh28.github.io`

## 🔧 Advanced Setup

### Google Scholar Integration

#### Option 1: Manual Update
1. Find your Google Scholar ID:
   - Visit your Google Scholar profile
   - Copy ID from URL: `citations?user=YOUR_ID_HERE`

2. Update `_config.yml`:
   ```yaml
   social:
     google_scholar: "YOUR_ACTUAL_ID"
   ```

#### Option 2: Automatic Updates (Recommended)
1. **Add GitHub Secret**:
   - Go to Settings → Secrets and variables → Actions
   - Add new secret: `GOOGLE_SCHOLAR_ID` = `your_scholar_id`

2. **Enable GitHub Actions**:
   - Go to Actions tab
   - Click "I understand my workflows, go ahead and enable them"

3. **Test the workflow**:
   - Go to Actions → "Update Google Scholar Citations"
   - Click "Run workflow"

### Publication Management

#### Method 1: Direct HTML Editing
Edit the publications section in `index.html`:

```html
<div class="publication-item">
    <div class="pub-title">Your Paper Title</div>
    <div class="pub-authors"><strong>Your Name</strong>, Co-authors</div>
    <div class="pub-venue">Conference/Journal Name 2024</div>
    <div class="pub-links">
        <a href="files/papers/paper.pdf" class="pub-link">PDF</a>
        <a href="https://github.com/you/project" class="pub-link">Code</a>
    </div>
</div>
```

#### Method 2: YAML Data File (Recommended)
1. **Edit `_data/publications.yml`**:
   ```yaml
   - title: "Your Paper Title"
     authors: "Your Name, Co-authors"
     venue: "Conference Name 2024"
     year: 2024
     pdf: "files/papers/paper1.pdf"
     code: "https://github.com/you/project"
     citations: 16
   ```

2. **Create dynamic publication list** (requires Jekyll processing):
   ```html
   {% for pub in site.data.publications %}
   <div class="publication-item">
       <div class="pub-title">{{ pub.title }}</div>
       <div class="pub-authors">{{ pub.authors }}</div>
       <div class="pub-venue">{{ pub.venue }}</div>
   </div>
   {% endfor %}
   ```

### File Organization

```
your-repository/
├── index.html              # Main website
├── _config.yml             # Configuration
├── README.md               # Documentation
├── images/
│   ├── profile.jpg         # Your photo (250x250px)
│   ├── favicon.ico         # Website icon
│   └── research/           # Research images
├── files/
│   ├── cv.pdf              # Your CV
│   ├── papers/             # PDF papers
│   └── slides/             # Presentation slides
├── _data/
│   ├── publications.yml    # Publication data
│   ├── scholar.json        # Auto-generated citations
│   └── stats.json          # Auto-generated stats
├── _includes/
│   └── google-scholar.js   # Scholar integration
└── .github/
    ├── workflows/
    │   └── update-scholar.yml  # Auto-update workflow
    └── scripts/
        └── update_scholar.py   # Update script
```

## 🎨 Customization

### Colors and Styling
Edit the CSS variables in `index.html`:

```css
:root {
    --primary-color: #3498db;      /* Main blue */
    --secondary-color: #2c3e50;    /* Dark blue */
    --gradient-start: #667eea;     /* Purple gradient start */
    --gradient-end: #764ba2;       /* Purple gradient end */
    --text-color: #333;           /* Main text */
    --light-bg: #f8f9fa;          /* Light background */
}
```

### Adding New Sections
1. **HTML Structure**:
   ```html
   <section id="new-section" class="section">
       <div class="container">
           <div class="section-header">
               <h2 class="section-title">Section Title</h2>
               <p class="section-subtitle">Description</p>
           </div>
           <!-- Your content here -->
       </div>
   </section>
   ```

2. **Navigation Link**:
   ```html
   <li><a href="#new-section">New Section</a></li>
   ```

### Mobile Responsiveness
The website is already mobile-responsive, but you can customize breakpoints:

```css
@media (max-width: 768px) {
    /* Mobile styles */
}

@media (max-width: 480px) {
    /* Small mobile styles */
}
```

## 🔍 SEO Optimization

### Meta Tags
Update these in the `<head>` section:

```html
<title>Your Name - PhD Researcher</title>
<meta name="description" content="Your research description">
<meta name="keywords" content="your, research, keywords">
<meta property="og:title" content="Your Name - PhD Researcher">
<meta property="og:description" content="Your research description">
```

### Google Analytics
1. **Create Google Analytics account**
2. **Get tracking ID** (GA4 format: G-XXXXXXXXXX)
3. **Update `_config.yml`**:
   ```yaml
   google_analytics: "G-XXXXXXXXXX"
   ```

### Structured Data
Add JSON-LD structured data for better search engine understanding:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Your Name",
  "jobTitle": "PhD Candidate",
  "affiliation": "Your University",
  "url": "https://yourusername.github.io",
  "sameAs": [
    "https://github.com/yourusername",
    "https://linkedin.com/in/yourprofile"
  ]
}
</script>
```

## 🚀 Performance Optimization

### Image Optimization
1. **Profile image**: 250x250px, optimized JPEG/WebP
2. **Research images**: Max 800px width
3. **Use WebP format** when possible for better compression

### Loading Speed
- All external dependencies are loaded from CDN
- CSS and JavaScript are minified
- Images should be optimized
- Uses modern web standards

## 🔧 Troubleshooting

### Common Issues

**Site not loading:**
- Check repository name is `username.github.io`
- Verify GitHub Pages is enabled
- Wait 10-15 minutes for deployment

**Images not showing:**
- Check file paths are correct
- Ensure files are committed to repository
- Verify file formats (JPG, PNG, WebP)

**Google Scholar not updating:**
- Check Scholar ID is correct
- Verify GitHub Secret is set
- Check Actions tab for error logs

**Mobile layout issues:**
- Test on multiple devices
- Check CSS media queries
- Validate HTML structure

### Getting Help

1. **GitHub Issues**: Create an issue in your repository
2. **GitHub Pages Docs**: https://docs.github.com/pages
3. **Jekyll Documentation**: https://jekyllrb.com/docs/
4. **Google Scholar API**: Consider using SerpAPI for production

## 📋 Pre-Launch Checklist

- [ ] Personal information updated
- [ ] Profile photo added
- [ ] CV uploaded and linked
- [ ] Publications list updated
- [ ] Research areas described
- [ ] Contact information correct
- [ ] Social media links working
- [ ] Google Scholar ID configured
- [ ] Mobile responsiveness tested
- [ ] All links working
- [ ] Favicon added
- [ ] SEO meta tags updated
- [ ] Google Analytics configured (optional)
- [ ] Repository name correct
- [ ] GitHub Pages enabled
- [ ] Custom domain configured (if applicable)

## 🔄 Maintenance

### Regular Updates
- **Publications**: Add new papers as published
- **CV**: Update regularly with new achievements
- **Research areas**: Update as focus evolves
- **Citations**: Automatic via GitHub Actions

### Annual Review
- Update profile photo if needed
- Review and update bio
- Check all external links
- Update research interests
- Review publications list for accuracy

---

**Your professional research website is ready! 🎓**

For additional help or questions, please refer to the README.md or create an issue in your repository.