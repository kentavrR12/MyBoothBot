# Exhibition Booth 3D Configurator

## Overview

A professional 3D web-based exhibition booth configurator built with **Three.js**. Allows users to design custom exhibition stands by selecting dimensions, materials, colors, and equipment in real-time with interactive 3D visualization.

## Features

✅ **Real-time 3D Visualization** - See your booth design instantly  
✅ **Interactive Controls** - Rotate, zoom, and pan the 3D model  
✅ **Customization Options:**
- Booth dimensions (2-6m length, 2-5m width)
- Construction types (Standard/Exclusive)
- Wall colors (8 color options)
- Materials (Plastic, Wood, Metal)
- Equipment (Lighting, Furniture, Monitor)

✅ **Automatic Cost Calculation** - Real-time pricing updates  
✅ **Shareable Configurations** - Generate links to share designs  
✅ **Responsive Design** - Works on desktop and tablets  
✅ **No Installation Required** - Pure HTML/JavaScript/WebGL

## Technology Stack

- **Three.js** - 3D graphics library (WebGL)
- **HTML5** - Structure
- **CSS3** - Styling and animations
- **JavaScript (ES6+)** - Logic and interactivity

## File Structure

```
exhibition_booth_configurator/
├── index.html          # Main HTML file with UI
├── configurator.js     # Three.js logic and controls
└── README.md          # This file
```

## Installation & Usage

### Option 1: Local File
1. Extract the ZIP file
2. Open `index.html` in a modern web browser
3. Start configuring your booth!

### Option 2: Web Server
```bash
# Using Python 3
python -m http.server 8000

# Using Node.js (http-server)
npx http-server

# Using PHP
php -S localhost:8000
```

Then open `http://localhost:8000` in your browser.

### Option 3: Deploy to Web Hosting
Upload the files to any web hosting service (GitHub Pages, Netlify, Vercel, etc.)

## How to Use

1. **Set Dimensions:**
   - Adjust Length (2-6 meters)
   - Adjust Width (2-5 meters)

2. **Choose Construction Type:**
   - Standard (500€ base price)
   - Exclusive (800€ base price)

3. **Select Wall Color:**
   - Click any color button to change wall appearance

4. **Add Materials:**
   - Check boxes for Plastic, Wood, or Metal
   - Each adds cost per square meter

5. **Add Equipment:**
   - Check boxes for Lighting, Furniture, or Monitor
   - Each adds fixed cost

6. **View Cost Summary:**
   - See real-time cost breakdown
   - Total cost updates automatically

7. **Save Configuration:**
   - Click "Save Config" to generate shareable link
   - Configuration saved to browser localStorage
   - Link copied to clipboard

8. **Reset:**
   - Click "Reset" to return to default configuration

## 3D Controls

| Action | Control |
|--------|---------|
| Rotate | Click and drag with mouse |
| Zoom | Scroll wheel |
| Pan | Right-click and drag |

## Cost Calculation Formula

```
TOTAL = (Base Price × Area) + (Materials × Area) + Equipment

Where:
- Base Price = 500€ (Standard) or 800€ (Exclusive)
- Area = Length × Width (in m²)
- Materials = sum of selected materials × area
- Equipment = sum of selected equipment (fixed prices)
```

### Example:
```
Length: 3m
Width: 4m
Area: 12m²
Construction: Standard (500€)
Materials: Wood (150€/m²)
Equipment: Lighting (300€)

Calculation:
- Base: 500€ × 12m² = 6000€
- Materials: 150€ × 12m² = 1800€
- Equipment: 300€
- TOTAL: 6000€ + 1800€ + 300€ = 8100€
```

## Integration with Telegram Bot

### Sending Configuration to Bot

The configurator generates shareable links with URL parameters:

```
https://example.com/configurator/?length=3&width=4&construction=standard&color=%23FF6B6B&materials=wood&equipment=lighting
```

### From Telegram Bot (Python/aiogram):

```python
# Generate link to configurator
configurator_url = "https://your-domain.com/exhibition_booth_configurator/"
params = f"?length={length}&width={width}&construction={construction_type}&materials={','.join(materials)}&equipment={','.join(equipment)}"
full_url = configurator_url + params

# Send to user
await message.answer(
    f"Design your booth in 3D:\n{full_url}",
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Open Configurator", url=full_url)]
    ])
)
```

## Browser Compatibility

- ✅ Chrome/Chromium (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ⚠️ IE11 (not supported - requires WebGL)

## Performance

- Optimized for smooth 60 FPS rendering
- Efficient shadow mapping
- Responsive to window resizing
- Minimal memory footprint

## Customization

### Add New Colors

Edit `index.html` and add new color buttons:

```html
<div class="color-btn" data-color="#YOURCOLOR" style="background: #YOURCOLOR;" title="Color Name"></div>
```

### Add New Equipment

Edit `configurator.js` in the `CONFIG` object:

```javascript
CONFIG.equipment = {
    // ... existing equipment
    projector: { name: 'Projector', price: 1200 }
};
```

Then add checkbox in `index.html`:

```html
<div class="checkbox-item">
    <input type="checkbox" id="equipment-projector" data-equipment="projector" data-price="1200">
    <label for="equipment-projector">Projector</label>
    <span class="price">+1200€</span>
</div>
```

### Modify Prices

Edit the `CONFIG` object in `configurator.js`:

```javascript
CONFIG.construction = {
    standard: { name: 'Standard', price: 600 },  // Changed from 500
    exclusive: { name: 'Exclusive', price: 900 }  // Changed from 800
};
```

## Known Limitations

- 3D models are procedurally generated (not imported from files)
- No texture mapping (solid colors only)
- No physics simulation
- Limited to single-booth configuration

## Future Enhancements

- [ ] Import custom 3D models (.glb, .gltf)
- [ ] Texture mapping and advanced materials
- [ ] Multiple booth configurations
- [ ] Export to PDF/image
- [ ] AR preview
- [ ] Multiplayer collaboration
- [ ] Database integration for saving configurations

## Troubleshooting

### Booth doesn't appear
- Check browser console for errors (F12)
- Ensure WebGL is enabled
- Try a different browser

### Performance issues
- Close other browser tabs
- Reduce window size
- Use a modern GPU-enabled browser

### Configuration not saving
- Check if localStorage is enabled
- Try incognito/private mode
- Clear browser cache

## License

This project is created for educational purposes (Bachelor's thesis).

## Support

For issues or questions, refer to:
- Three.js Documentation: https://threejs.org/docs/
- WebGL Support: https://get.webgl.org/

---

**Created:** 2026-04-11  
**Version:** 1.0  
**Author:** Manus AI
