# Visual Indicators Reference Guide
## Quick Reference for Circle Highlights & Animations

---

## 🎯 Circle Indicator Numbering System

```
STEP #1  - Contest Name Input         [Red Circle]
STEP #2  - Description Field          [Green Circle]
STEP #3  - Start/End Dates            [Blue Circles]
STEP #4  - PDPA URL Field             [Purple Circle]
STEP #5  - PDPA Message               [Orange Circle]
STEP #6a - Agreement Message          [Green Circle]
STEP #6b - Rejection Message          [Red Circle]
STEP #7  - Introduction Message       [Teal Circle]
STEP #8  - Instructions Textarea      [Blue Circle]
STEP #9  - NRIC Checkbox              [Yellow Circle]
STEP #10 - Receipt Checkbox           [Orange Circle]
STEP #11 - Min Purchase Amount        [Green Circle]
STEP #12 - Verification Instructions  [Magenta Circle]
STEP #13 - GIF/Image URL              [Cyan Circle]
STEP #14 - Success Message            [Bright Green Circle]
STEP #15 - Failure Message            [Red Circle]
STEP #16 - Create Contest Button      [Glowing Green Circle]
```

---

## 🎨 Color Palette (HEX Codes)

| Color Name | HEX Code | Usage |
|------------|----------|-------|
| Primary Red | `#e74c3c` | Critical inputs, rejection messages |
| Success Green | `#42b883` | Positive actions, success messages |
| Info Blue | `#1877f2` | Date/time, informational fields |
| Warning Orange | `#f7b731` | Settings, optional fields |
| Purple | `#9b59b6` | Links, URLs |
| Teal | `#17a2b8` | Welcome/introduction |
| Magenta | `#e91e63` | Instructions, guidance |
| Cyan | `#00bcd4` | Media, visual elements |
| Bright Green | `#10b981` | Final actions, confirmations |

---

## 📐 Circle Indicator Specifications

### Standard Circle
```
Diameter: 80px (relative to element size)
Border: 4px solid [COLOR]
Opacity: 80%
Blur: 0px (sharp edge)
Glow: 8px blur, 20% opacity, same color
Padding: 12px from element edge
```

### Animation Keyframes
```css
@keyframes pulse-circle {
  0%, 100% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.95;
  }
}

Duration: 1.5s
Iteration: infinite
Easing: ease-in-out
```

---

## 🏷️ Label Box Specifications

### Label Style
```
Background: rgba(255, 255, 255, 0.95)
Border: 2px solid [MATCHING_COLOR]
Border-radius: 6px
Padding: 8px 12px
Font: 'Inter', Bold, 14px
Text Color: #1c1e21 (dark gray)
Shadow: 0 2px 8px rgba(0,0,0,0.15)
```

### Label Positioning
- **Left-side inputs:** Label appears on the right
- **Right-side preview:** Label appears on the left
- **Centered elements:** Label appears above
- **Distance from circle:** 20px minimum

### Label Animation
```css
@keyframes slide-in-label {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

Duration: 0.4s
Delay: 0.2s (after circle appears)
Easing: ease-out
```

---

## ➡️ Arrow Specifications

### Curved Arrow Style
```
Line Width: 3px
Color: Matching circle color
Opacity: 90%
Arrow Head: 12px triangle
Curve: Quadratic bezier
```

### Arrow Animation
```css
@keyframes draw-arrow {
  from {
    stroke-dashoffset: 1000;
  }
  to {
    stroke-dashoffset: 0;
  }
}

Duration: 0.8s
Easing: ease-in-out
```

### When to Use Arrows
1. Form field → WhatsApp preview connection
2. Section completion → Next section
3. Input → Badge summary
4. Toggle button → Preview change

---

## ✓ Checkmark Animation Specs

### Checkmark Design
```
Circle Size: 32px diameter
Circle Color: #42b883 (success green)
Circle Border: 3px
Check Mark: White, 3px stroke
Position: Top-right of section header
```

### Animation Sequence
```
1. Circle outline draws (0.4s) - rotate 0° to 360°
2. Check mark draws (0.3s) - path animation
3. Slight bounce (0.2s) - scale 1.0 → 1.2 → 1.0
Total: 0.9s
```

---

## 🎬 Transition Effects Between Sections

### Section Collapse/Expand
```
Duration: 0.3s
Easing: ease-in-out
Effect: Max-height animation (0 → 1000px)
Concurrent: Fade in content (opacity 0 → 1)
```

### Circle Fade Out (Moving to Next Step)
```
Duration: 0.5s
Effect: 
  - Opacity: 80% → 0%
  - Scale: 1.0 → 0.8
  - Position: Stays in place
Delay before next: 0.2s
```

---

## 📱 WhatsApp Preview Indicators

### Message Highlight in Preview
```
Effect: Pulsing border around message bubble
Border: 3px solid #25d366 (WhatsApp green)
Animation: Opacity 50% ↔ 100% (1s loop)
Duration: 3 seconds, then fade out
```

### Preview Update Indicator
```
Icon: Small animated spinner or pulse dot
Position: Top-right of preview panel
Color: #25d366
Message: "Updating preview..."
Duration: 0.5s
```

---

## 🎯 Dual-Panel Connection Effect

### Data Flow Animation (Form → Preview)
```
Visual: Animated particles or line
Start Point: Form input field (center)
End Point: WhatsApp preview message (center)
Animation:
  - Particle: Small dot (4px)
  - Color: Gradient (input color → #25d366)
  - Speed: 0.8s travel time
  - Easing: ease-in-out
  - Trail: 3 particles with 0.2s stagger
```

---

## 📊 Progress Indicator (Optional)

### Top Progress Bar
```
Position: Fixed top, full width
Height: 4px
Colors: Gradient following section colors
Animation: Fill from 0% to 100% as video progresses
Segments: 6 equal parts (one per main step)
```

### Section Counter
```
Format: "Step X of 6"
Position: Bottom-right corner
Font: 16px, semi-bold
Color: #65676b (gray)
Background: White with 90% opacity
Padding: 6px 12px
Border-radius: 20px
```

---

## 🎆 Special Effect Moments

### 1. Form Field Fill Animation
```
Effect: Text typing simulation
Speed: 50 characters per second
Cursor: Blinking vertical line
Sound: Optional keyboard typing sound (subtle)
```

### 2. Checkbox Toggle Animation
```
Effect: Smooth slide + checkmark draw
Duration: 0.3s
Sound: Optional "click" sound effect
Visual: Brief glow around checkbox (0.5s)
```

### 3. Date Picker Interaction
```
Effect: Calendar overlay appears
Animation: Fade in + scale (0.3s)
Interaction: Show cursor selecting date
Auto-close: Fade out after selection
```

### 4. Success Confetti (End of Video)
```
Trigger: After "Create Contest" button click
Particles: 50-100 confetti pieces
Colors: Multi-colored (contest theme colors)
Duration: 2 seconds
Physics: Fall with slight rotation
Origin: Top-center of screen
```

---

## 🔄 Loop Indicators (For Key Concepts)

### Repeat Emphasis Circle
```
Use Case: When re-explaining important concepts
Effect: Circle pulses 3 times rapidly
Color: Yellow/orange (attention-grabbing)
Message Overlay: "Important!" or "Remember!"
```

---

## 📋 Badge Overlay Examples

### Requirement Summary Badges
```
Badge Container:
  - Background: Semi-transparent white
  - Border: 1px solid #dadde1
  - Border-radius: 12px
  - Padding: 8px
  - Shadow: 0 2px 6px rgba(0,0,0,0.1)

Individual Badge:
  - Height: 24px
  - Padding: 4px 10px
  - Border-radius: 12px
  - Font: 11px, semi-bold
  - Icon + Text format

Badge Colors:
  ✓ NRIC Required - Yellow (#f7b731)
  ✓ Receipt Required - Orange (#f39c12)
  ✓ Min RM98 - Green (#42b883)
```

### Animation Entry
```
Sequence: Stack from bottom to top
Stagger: 0.2s between each badge
Entry: Slide up + fade in (0.3s each)
```

---

## 🎭 Split-Screen Examples Layout

### Good vs Bad Receipt Example
```
Layout:
┌─────────────────┬─────────────────┐
│                 │                 │
│   Good Photo ✓  │  Bad Photo ✗    │
│                 │                 │
│   [Receipt]     │  [Blurry]       │
│                 │                 │
│   • Well-lit    │  • Too dark     │
│   • Complete    │  • Cropped      │
│   • Clear text  │  • Blurry       │
│                 │                 │
└─────────────────┴─────────────────┘

Border: Good side = green, Bad side = red
Thickness: 4px
Indicators: Large ✓ and ✗ icons overlaid
```

---

## ⏱️ Timing Chart

```
Time     | Visual Element                    | Audio Element
---------|----------------------------------|---------------------------
0:00     | Fade in from black               | "Welcome! In this..."
0:02     | Circle on "Create" button        | 
0:10     | Arrow to form                    | 
0:15     | Section 1 expands                | "Step 1: Contest..."
0:17     | Circle #1: Name field            | "First, give your..."
0:24     | Circle #2: Description           | "Next, add a..."
0:32     | Circles #3: Dates                | "Then, set your..."
0:40     | Checkmark animation              |
0:45     | Section 2 expands                | "Step 2: PDPA..."
0:47     | Circle #4: PDPA URL              | "First, paste your..."
...      | [Continue pattern]               | [Continue pattern]
3:22     | Final circle on submit button    | "Click Create Contest"
3:26     | Confetti animation               | 
3:30     | Fade to dashboard                | "And that's it!"
3:45     | Logo + CTA                       | "Start creating today!"
```

---

## 🎥 Camera Movement Guide

### Zoom Levels
```
Wide Shot (100%): Show entire interface - use at start/end
Medium Shot (110%): Focus on specific section - main content
Close-Up (125%): Highlight individual form fields - key moments
Extreme Close-Up (150%): Show specific text/values - detail shots
```

### Pan Movements
```
Horizontal Pan: Left (form) → Right (preview) - 1.5s duration
Vertical Pan: Scroll through form sections - 2s duration
Easing: Ease-in-out for smooth professional feel
```

### Zoom Transitions
```
Zoom In: Use when focusing on a specific field (0.8s)
Zoom Out: Use when showing context (0.8s)
Avoid: Rapid zooms (causes motion sickness)
```

---

## 🎵 Sound Effects Recommendations

```
- Circle appears: Soft "pop" (subtle)
- Label appears: Light "whoosh"
- Checkmark completes: Success "ding"
- Section expands: Smooth "swoosh"
- Form typing: Soft keyboard clicks (very subtle)
- Button hover: Tiny "click"
- Final submit: Triumphant "completion" sound
- Confetti: Celebratory "sparkle" sound
```

**Volume Guide:** All SFX should be 10-15% of voiceover volume

---

## 📐 Responsive Layouts (If Showing Mobile View)

### Mobile Screen Recording
```
Device Frame: iPhone/Android mockup
Orientation: Portrait
Resolution: 1080x1920
Circle Sizes: Scaled down to 60px diameter
Label Font: 12px (smaller)
Touch Indicators: Finger tap animation instead of cursor
```

---

## ✨ Pro Tips for Google Vids

1. **Layer Organization**
   - Layer 1: Screen recording
   - Layer 2: Circle indicators
   - Layer 3: Labels and text
   - Layer 4: Arrows
   - Layer 5: Checkmarks
   - Layer 6: Voiceover audio
   - Layer 7: Background music

2. **Keyframe Strategy**
   - Set keyframes at 0.5s intervals for smooth animations
   - Use easing curves for professional feel
   - Preview at half-speed to check timing

3. **Export Settings**
   - Format: MP4 (H.264)
   - Resolution: 1920x1080 (1080p)
   - Frame Rate: 30fps or 60fps
   - Bitrate: 8-12 Mbps for high quality
   - Audio: AAC, 192 kbps

4. **Accessibility**
   - Add captions/subtitles (burnt-in or separate)
   - Ensure high contrast for visibility
   - Avoid flashing effects (epilepsy risk)
   - Test on multiple devices before publishing

---

## 🎯 Quick Start Template

For Google Vids, import these assets:
- ✅ Screen recording of full contest creation flow
- ✅ Circle PNG overlays (16 different colors)
- ✅ Arrow SVG templates
- ✅ Checkmark animation GIF/Lottie
- ✅ Label box templates (PSD/Figma)
- ✅ Background music track (120-130 BPM)
- ✅ SFX pack (pops, whooshes, dings)
- ✅ Voiceover audio (recorded separately)

---

## 📞 Final Production Checklist

- [ ] All 16 circles appear at correct timestamps
- [ ] Labels are readable and properly aligned
- [ ] Arrows connect correct elements
- [ ] 6 checkmarks appear after each section
- [ ] WhatsApp preview updates are visible
- [ ] Voiceover is synced with visuals
- [ ] Background music doesn't overpower voice
- [ ] Color scheme is consistent throughout
- [ ] No rapid movements (avoid motion sickness)
- [ ] Transitions are smooth (0.3-0.5s)
- [ ] Text is large enough to read on mobile
- [ ] Video tested on multiple screen sizes
- [ ] Captions/subtitles added
- [ ] Final export is high quality (1080p+)
- [ ] Video length is 3:30-3:45 (optimal)

---

**Need Help?** Reference the main script document for detailed voiceover timing and content.

**Happy Editing! 🎬**


