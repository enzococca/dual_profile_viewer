# QGIS Plugin Repository Submission Guide

## Pre-submission Checklist

### Required Files ✓
- [x] `__init__.py` - Plugin initialization
- [x] `metadata.txt` - Plugin metadata
- [x] `icon.png` - Plugin icon (24x24 or 64x64 px)
- [x] Main plugin files (`.py` files)
- [x] `README.md` - Documentation
- [x] `LICENSE` - GPL-3.0 license

### Metadata Requirements ✓
- [x] Unique plugin name
- [x] Valid version number (1.0.0)
- [x] Minimum QGIS version specified (3.0)
- [x] Author name and email
- [x] Description and about text
- [x] Repository and tracker URLs
- [x] Tags for discoverability
- [x] Changelog

### Code Quality ✓
- [x] No syntax errors
- [x] Compatible with QGIS 3.x Python API
- [x] Proper error handling
- [x] User-friendly interface

## Submission Steps

### 1. Create Plugin Package

```bash
# Navigate to plugins directory
cd ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/

# Create zip file (exclude git and development files)
zip -r dual_profile_viewer.zip "dual_profile_viewer 2"/* \
    -x "*.git*" \
    -x "*__pycache__*" \
    -x "*.pyc" \
    -x ".DS_Store" \
    -x "QGIS_REPOSITORY_SUBMISSION.md" \
    -x "CLAUDE.md" \
    -x "Strcture_Proj.md"
```

### 2. Test Plugin Package

1. Install from ZIP in QGIS:
   - Plugins → Manage and Install Plugins
   - Install from ZIP
   - Select `dual_profile_viewer.zip`
   - Verify installation and functionality

### 3. Register on QGIS Plugin Repository

1. Go to: https://plugins.qgis.org/
2. Create account or login
3. Click "Share a plugin"

### 4. Upload Plugin

Fill in the form:
- **Package**: Upload `dual_profile_viewer.zip`
- **Experimental**: No (stable release)
- **QGIS Versions**: 3.0 to 3.99
- **Homepage**: https://github.com/enzococca/dual-profile-viewer
- **Tracker**: https://github.com/enzococca/dual-profile-viewer/issues
- **Repository**: https://github.com/enzococca/dual-profile-viewer

### 5. Additional Information

**Plugin Description** (for repository):
```
The Dual Profile Viewer creates parallel elevation profiles from DEM/DTM data, 
specifically designed for archaeological and geological analysis. Perfect for 
analyzing walls, structures, excavations, and terrain features.

Key Features:
• Dual parallel profiles with adjustable offset
• Interactive Plotly visualizations
• Multi-DEM comparison
• Export as georeferenced vectors (polyline/polygon/3D)
• CSV and PNG export with georeferencing
• Automatic section labeling
```

**Tags**: archaeology, profile, dem, dtm, elevation, analysis, vector, export, terrain, cross-section

### 6. Post-Submission

After submission:
1. Plugin will be reviewed by QGIS team
2. You'll receive email notifications
3. Address any feedback or issues
4. Plugin will be available in QGIS Plugin Manager

## Maintenance

### Version Updates
1. Update version in `metadata.txt`
2. Update changelog
3. Create new ZIP package
4. Upload new version on plugin page

### Issue Management
- Monitor GitHub issues
- Respond to user feedback
- Release patches for critical bugs

## Marketing & Community

1. **Announce Release**:
   - QGIS mailing lists
   - GIS forums and communities
   - Archaeological software groups
   - Social media (#QGIS #GIS #Archaeology)

2. **Create Tutorial**:
   - Video demonstration
   - Blog post with examples
   - Sample datasets

3. **Gather Feedback**:
   - User surveys
   - Feature requests
   - Use case documentation

## Support Channels

- GitHub Issues: Bug reports and feature requests
- Email: enzo.ccc@gmail.com
- Wiki: Documentation and tutorials