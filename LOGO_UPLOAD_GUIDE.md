# Logo Upload Guide

## Overview
A new **Site Settings** feature has been added to the Django Admin panel, allowing you to easily upload and manage the Roots Party logo without editing code or replacing static files.

## How to Upload/Change the Logo

### Step 1: Access Site Settings
1. Go to your Django Admin panel: `http://localhost:8080/admin/`
2. Look for **"Site Settings"** in the **Core** section
3. Click on **"Site Settings"** (there will only be one entry)

### Step 2: Upload Your Logo
1. In the **"Logo Settings"** section, click **"Choose File"** next to **"Logo"**
2. Select your logo image file (PNG, JPG, etc.)
3. After uploading, you'll see a cropping tool - adjust the crop area if needed
4. Optionally, upload a **"Logo Square"** version for favicons and social media
5. Click **"Save"** at the bottom

### Step 3: Verify
1. Go to your homepage: `http://localhost:8080/`
2. The new logo should appear immediately
3. If you see the old logo, do a hard refresh (Ctrl+F5) to clear browser cache

## Features

- **Image Cropping**: Built-in cropping tool to ensure optimal logo display
- **Automatic Fallback**: If no logo is uploaded, the system uses the default static logo
- **Square Logo Option**: Upload a separate square version for favicons and social media
- **Site-Wide Availability**: The logo is automatically available in all templates

## Logo Requirements

- **Format**: PNG (recommended for transparency) or JPG
- **Size**: Recommended 400x400px or larger (square format works best)
- **File Size**: Keep under 2MB for optimal performance
- **Transparency**: PNG with transparency works best for logos

## Additional Settings

The Site Settings page also allows you to manage:
- **Site Name**: Official site name
- **Site Tagline**: Slogan/tagline
- **Contact Information**: Email and phone
- **Social Media**: Twitter, Facebook, YouTube links

## Troubleshooting

### Logo Not Showing
- Clear browser cache (Ctrl+F5)
- Check that the image file uploaded successfully
- Verify the file isn't corrupted

### Logo Looks Distorted
- Use the cropping tool to adjust the crop area
- Ensure your source image is square or close to square
- Try uploading a higher resolution image

### Want to Revert to Default Logo
- Simply delete the uploaded logo in the admin panel
- The system will automatically fall back to the static logo

## Technical Details

- **Model**: `SiteSettings` (singleton - only one instance)
- **Storage**: Uploaded logos are stored in `media/site/logo/`
- **Template Usage**: `{{ site_settings.get_logo_url }}` in templates
- **Context Processor**: Site settings are available globally via `core.context_processors.site_settings`
