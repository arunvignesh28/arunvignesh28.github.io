# Arun Vignesh - Personal Research Website

A modern, professional website for academic researchers built with HTML, CSS, JavaScript, and Jekyll for GitHub Pages.

## 🚀 Quick Start

1. **Fork and rename this repository** to `yourusername.github.io`
2. **Edit the configuration** in `_config.yml` with your information
3. **Replace placeholder content** with your actual information
4. **Add your profile image** to `images/profile.jpg`
5. **Upload your CV** to `files/cv.pdf`
6. **Enable GitHub Pages** in repository settings

Your site will be live at `https://yourusername.github.io`

## 📁 File Structure

```
├── index.html              # Main website file
├── _config.yml             # Jekyll configuration
├── README.md               # This file
├── images/
│   ├── profile.jpg         # Your profile photo
│   ├── favicon.ico         # Website favicon
│   └── research/           # Research-related images
├── files/
│   ├── cv.pdf              # Your CV/Resume
│   └── papers/             # PDF files of your papers
├── _data/
│   └── publications.yml    # Publication data
└── _includes/
    └── google-scholar.js   # Google Scholar integration
```

## ✏️ Customization Guide

### 1. Basic Information

Edit these sections in `index.html`:

**Hero Section:**
- Update name, title, and description
- Replace `./images/profile.jpg` with your photo
- Update CV link path

**About Section:**
- Write your biography
- Update statistics (publications, citations)
- Add your research interests

**Research Areas:**
- Replace the three research cards with your areas
- Update icons and descriptions

### 2. Publications

**Option A: Manual Updates**
Edit the publications section in `index.html` directly.

**Option B: Data-Driven (Recommended)**
1. Create `_data/publications.yml`:

```yaml
- title: "Your Paper Title"
  authors: "Your Name, Co-Author"
  venue: "Conference/Journal Name 2024"
  year: 2024
  pdf: "files/papers/paper1.pdf"
  code: "https://github.com/yourusername/project"
  arxiv: "https://arxiv.org/abs/xxxx.xxxxx"
  
- title: "Another Paper"
  authors: "Co-Author, Your Name"
  venue: "Workshop Name 2023"
  year: 2023
  pdf: "files/papers/paper2.pdf"
```

### 3. Google Scholar Integration

1. Find your Google Scholar ID:
   - Go to your Google Scholar profile
   - Copy the ID from the URL: `citations?user=YOUR_ID_HERE`

2. Update `_config.yml`:
   ```yaml
   google_scholar: "YOUR_ACTUAL_ID"
   ```

3. Set up automatic updates (optional):
   - Add your Scholar ID to GitHub Secrets
   - Enable GitHub Actions for automatic citation updates

### 4. Social Media Links

Update the social media section in both `index.html` and `_config.yml`:

```yaml
social:
  github: "yourusername"
  linkedin: "yourlinkedin"
  twitter: "yourtwitter"
  google_scholar: "YOUR_SCHOLAR_ID"
  orcid: "YOUR_ORCID_ID"
```

### 5. Contact Information

Update the contact section with:
- Your university email
- Institution and department
- Office location
- LinkedIn profile

## 🎨 Styling and Colors

The website uses a modern color scheme. To customize:

1. **Primary colors** are defined in CSS variables at the top of the `<style>` section
2. **Gradient backgrounds** can be modified in the `.hero` class
3. **Fonts** can be changed by updating the Google Fonts import

Main colors:
- Primary blue: `#3498db`
- Dark blue: `#2c3e50`
- Purple gradient: `#667eea` to `#764ba2`

## 📱 Mobile Responsiveness

The website is fully responsive and includes:
- Mobile-friendly navigation menu
- Responsive grid layouts
- Touch-friendly buttons
- Optimized images and fonts

## 🔧 Advanced Features

### Google Analytics

1. Create a Google Analytics account
2. Get your tracking ID (GA4 format: G-XXXXXXXXXX)
3. Update `_config.yml`:
   ```yaml
   google_analytics: "G-XXXXXXXXXX"
   ```

### SEO Optimization

The website includes:
- Meta tags for search engines
- Open Graph tags for social media
- Structured data for academic profiles
- XML sitemap generation

### Performance Features

- Optimized images and fonts
- Minimal external dependencies
- Fast loading animations
- Efficient CSS and JavaScript

## 🚀 Deployment

### GitHub Pages (Recommended)

1. Push your code to `yourusername.github.io` repository
2. Go to Settings → Pages
3. Select "Deploy from branch"
4. Choose "main" branch
5. Your site will be live at `https://yourusername.github.io`

### Custom Domain (Optional)

1. Add a `CNAME` file with your domain name
2. Configure DNS settings with your domain provider
3. Enable HTTPS in GitHub Pages settings

## 🔄 Maintenance

### Regular Updates

1. **Publications**: Add new papers as they're published
2. **CV**: Keep your CV file updated
3. **News/Updates**: Add recent achievements or news
4. **Profile photo**: Update periodically

### Google Scholar Sync

For automatic citation updates:
1. Enable GitHub Actions
2. Set up the Google Scholar workflow
3. Citations will update daily automatically

## 🆘 Troubleshooting

### Common Issues

**Site not loading:**
- Check repository name is `yourusername.github.io`
- Verify GitHub Pages is enabled
- Wait 5-10 minutes for deployment

**Images not showing:**
- Ensure file paths are correct
- Check image file formats (JPG, PNG, WebP)
- Verify file sizes aren't too large

**Mobile layout issues:**
- Clear browser cache
- Test on multiple devices
- Check responsive CSS media queries

### Getting Help

1. Check the [GitHub Pages documentation](https://docs.github.com/en/pages)
2. Review Jekyll documentation for advanced features
3. Open an issue in this repository for specific problems

## 📄 License

This template is free to use for academic purposes. Please maintain attribution in the footer.

## 🤝 Contributing

Feel free to suggest improvements or report issues. Pull requests are welcome!

---

**Good luck with your research website! 🎓**