# Beth Assistant Design System - Complete Documentation

**File:** beth assistant design system file  
**Last Modified:** June 25, 2025  
**Figma URL:** https://www.figma.com/design/8dak7GzHKjjMohUxhu9M9A/beth-assistant-design-system-file  
**Token Reference:** `frontend/styles/tokens.json`

---

## 🎯 System Overview

The Beth Assistant Design System is a comprehensive conversational AI interface featuring **two distinct window states**:

1. **Initial State**: Suggestion prompts interface with greeting and prompt cards
2. **Conversation State**: Active chat interface with message bubbles and history

The system transitions seamlessly between these states, maintaining visual consistency while optimizing for different interaction modes.

---

## 🏗️ Layout Architecture

### Main Application Structure
- **Container Width**: 1440px (desktop)
- **Mobile Width**: 375px
- **Content Padding**: 48px (desktop), 23px (mobile)
- **Background**: Image overlay (`semantic.colors.background.primary`)

### Two-Window System

#### Window 1: Suggestion Interface
**Purpose**: Initial user engagement with suggested prompts
**Components**:
- Greeting section
- Suggestion cards grid
- Suggestion shapes (decorative)
- Chat input (prominent, ready for interaction)

#### Window 2: Chat Conversation
**Purpose**: Active conversation with message history
**Components**:
- Chat conversation bubbles
- Chat history sidebar
- Chat input (contextual, part of flow)
- Navigation controls

---

## 🧩 Component Library

### 1. Chat Input Component Set

**Component ID**: `4002:13423`  
**Variants**: 14 total (7 states × 2 sizes)

#### Size Variants
- **Full Height**: `180px` - Used in suggestion interface for prominence
- **Short Height**: `100px` - Used in conversation interface for efficiency

#### Interactive States

##### Default State
**Full Variant** (`4002:13424`):
- **Dimensions**: 740px × 180px
- **Background**: `semantic.colors.background.secondary` (`#F7F7F7`)
- **Border**: 2px solid `semantic.colors.border.primary` (`#000000`)
- **Shadow**: `semantic.shadows.button.default`
- **Placeholder**: "Ask me a question..." (`semantic.typography.body.large`)

**Short Variant** (`4169:5410`):
- **Dimensions**: 740px × 100px
- **All other properties identical to full variant**

##### Hover State
**Full Variant** (`4027:19771`):
- **Visual Enhancement**: Subtle background lightening
- **Border**: Maintains 2px solid black
- **Shadow**: Enhanced depth

**Short Variant** (`4169:5427`):
- **Identical hover behavior to full variant**

##### Focused State
**Full Variant** (`4002:13444`):
- **Border**: Accent color highlight
- **Shadow**: `semantic.shadows.button.focus`
- **Text Cursor**: Active input state

**Short Variant** (`4169:5444`):
- **Identical focus behavior to full variant**

##### File Attachment States

**Attaching Images** - Full (`4002:13464`) / Short (`4169:5461`):
- **Visual Indicator**: Image icon highlighted in `semantic.colors.accent.primary`
- **State Feedback**: Visual confirmation of attachment mode

**Attaching Files** - Full (`4002:13515`) / Short (`4169:5506`):
- **Visual Indicator**: File icon highlighted in `semantic.colors.accent.primary`
- **State Feedback**: Visual confirmation of attachment mode

**Images Attached** - Full (`4002:13569`) / Short (`4169:5557`):
- **Confirmation State**: Attached images displayed as thumbnails
- **Icon State**: Image icon remains highlighted

**Files Attached** - Full (`4002:13589`) / Short (`4169:5574`):
- **Confirmation State**: Attached files listed with names
- **Icon State**: File icon remains highlighted

#### Internal Structure
```
chat input/
├── TextArea/
│   └── Controls/
│       └── Input with label/
│           └── Input/
│               ├── Text (placeholder)
│               └── Frame 8 (cursor indicator)
└── controls/
    ├── Controls-Left/
    │   ├── Files button
    │   └── Image button
    └── Controls-Right/
        ├── Character count (0/1000)
        └── Send button
```

#### CSS Token Mapping
```css
.chat-input {
  width: 740px;
  height: var(--chat-input-height-full, 180px); /* or --chat-input-height-short: 100px */
  background: var(--semantic-colors-background-secondary);
  border: 2px solid var(--semantic-colors-border-primary);
  border-radius: var(--primitives-border-radius-sm);
  box-shadow: var(--semantic-shadows-button-default);
  padding: var(--primitives-spacing-4) var(--primitives-spacing-3);
  gap: var(--primitives-spacing-3);
}

.chat-input__text {
  font-family: var(--primitives-typography-font-family-primary);
  font-weight: var(--primitives-typography-font-weight-medium);
  font-size: var(--primitives-typography-font-size-lg);
  line-height: var(--primitives-typography-line-height-tight);
  color: var(--semantic-colors-text-placeholder);
}
```

---

### 2. Icon Buttons Component Set

**Component ID**: `4002:13733`  
**Variants**: 18 total (3 buttons × 6 states)

#### Button Types
1. **Files Button** (`icon button=files`)
2. **Image Button** (`icon button=image`)  
3. **Send Button** (`icon button=send`)

#### Interactive States

##### Default State
- **Dimensions**: 44px × 44px (including 10px padding)
- **Background**: `semantic.colors.background.secondary` (`#F7F7F7`)
- **Icon Size**: 24px × 24px
- **Border Radius**: `primitives.border-radius.sm` (4px)

##### Hover State
- **Background**: `semantic.colors.accent.primary` (`#2180EC`)
- **Icon Color**: White
- **Transition**: 200ms ease

##### Focus State
- **Background**: `semantic.colors.accent.primary` (`#2180EC`)
- **Outline**: 2px solid `semantic.colors.accent.primary`
- **Outline Offset**: 2px

##### Active State
- **Background**: `semantic.colors.accent.gradient`
- **Icon Color**: White
- **Scale**: 0.95 (pressed effect)

##### Attached State (Files/Images only)
- **Background**: `semantic.colors.accent.gradient`
- **Border**: 1px solid `semantic.colors.accent.primary`
- **Icon Color**: White
- **Persistent State**: Remains highlighted when files/images attached

#### CSS Token Mapping
```css
.icon-button {
  width: 44px;
  height: 44px;
  padding: var(--primitives-spacing-2-5);
  background: var(--semantic-colors-background-secondary);
  border-radius: var(--primitives-border-radius-sm);
  transition: all 200ms ease;
}

.icon-button:hover {
  background: var(--semantic-colors-accent-primary);
}

.icon-button:focus {
  background: var(--semantic-colors-accent-primary);
  outline: 2px solid var(--semantic-colors-accent-primary);
  outline-offset: 2px;
}

.icon-button:active {
  background: var(--semantic-colors-accent-gradient);
  transform: scale(0.95);
}

.icon-button--attached {
  background: var(--semantic-colors-accent-gradient);
  border: 1px solid var(--semantic-colors-accent-primary);
}
```

---

### 3. Suggestion Cards Component Set

**Component ID**: `4002:13609`  
**Variants**: 3 states

#### Card Structure
- **Dimensions**: Variable width × fixed height
- **Background**: `semantic.colors.background.secondary` (`#F7F7F7`)
- **Border**: 2px solid `semantic.colors.border.primary` (`#171717`)
- **Border Radius**: `primitives.border-radius.sm` (4px)
- **Padding**: 12px (right only, left 0px)

#### Interactive States

##### Default State (`4002:13610`)
- **Background**: `semantic.colors.background.secondary`
- **Border**: 2px solid `semantic.colors.border.primary`
- **Text Color**: `semantic.colors.text.primary`

##### Hover State (`4002:13616`)
- **Background**: Maintains `semantic.colors.background.secondary`
- **Border**: 2px solid `semantic.colors.border.primary`
- **Shadow**: `semantic.shadows.suggestion-card.hover`
  - Outer glow: `0px 0px 100px 0px rgba(254, 235, 229, 1)`
  - White highlight: `0px 0px 1px 4px rgba(255, 255, 255, 0.1)`
  - Inner highlight: `inset 0px 2px 1px 0px rgba(255, 255, 255, 0.25)`
  - Inner shadow: `inset 0px -2px 2px 0px rgba(0, 0, 0, 0.25)`

##### Focus State (`4002:13622`)
- **Border Radius**: Increased to 6px (from 4px)
- **Background**: `semantic.colors.background.secondary`
- **Border**: 2px solid `semantic.colors.border.primary`
- **Keyboard Navigation**: Accessible focus indicator

#### CSS Token Mapping
```css
.suggestion-card {
  background: var(--semantic-colors-background-secondary);
  border: 2px solid var(--semantic-colors-border-primary);
  border-radius: var(--primitives-border-radius-sm);
  padding: 0 var(--primitives-spacing-3) 0 0;
  transition: all 200ms ease;
}

.suggestion-card:hover {
  box-shadow: var(--semantic-shadows-suggestion-card-hover);
}

.suggestion-card:focus {
  border-radius: var(--primitives-border-radius-md);
  outline: 2px solid var(--semantic-colors-accent-primary);
  outline-offset: 2px;
}
```

---

### 4. New Chat Button Component Set

**Component ID**: `4002:13773`  
**Variants**: 8 total (2 sizes × 4 states)

#### Size Variants
- **Full Size**: 244px width - Shows full "New Chat" text
- **Collapsed Size**: 96px width - Shows icon only

#### Interactive States

##### Default State
**Full** (`4002:13800`):
- **Dimensions**: 244px × 68px (including padding)
- **Background**: `semantic.colors.background.primary` (`#000000`)
- **Border**: 1px solid `semantic.colors.border.primary` (`#000000`)
- **Text**: "New Chat" in white
- **Border Radius**: 6px

**Collapsed** (`4025:744`):
- **Dimensions**: 96px × 68px
- **Icon Only**: Plus icon centered
- **Same styling as full variant**

##### Hover State
**Full** (`4002:13774`) / **Collapsed** (`4025:748`):
- **Background**: `semantic.colors.accent.primary` (`#2180EC`)
- **Border**: 1px solid `semantic.colors.accent.primary`
- **Text/Icon Color**: White

##### Focus State
**Full** (`4002:13790`) / **Collapsed** (`4025:752`):
- **Background**: `semantic.colors.accent.primary` (`#2180EC`)
- **Border**: 1px solid `semantic.colors.accent.primary`
- **Outline**: 2px solid `semantic.colors.accent.primary`
- **Outline Offset**: 2px

##### Active State
**Full** (`4002:13782`) / **Collapsed** (`4025:757`):
- **Background**: `semantic.colors.accent.gradient`
- **Border**: 1px solid `semantic.colors.accent.primary`
- **Scale**: 0.98 (pressed effect)

#### CSS Token Mapping
```css
.new-chat-button {
  height: 68px;
  padding: var(--primitives-spacing-4) var(--primitives-spacing-8);
  background: var(--semantic-colors-background-primary);
  border: 1px solid var(--semantic-colors-border-primary);
  border-radius: var(--primitives-border-radius-md);
  color: var(--semantic-colors-text-inverse);
  transition: all 200ms ease;
}

.new-chat-button--full {
  width: 244px;
}

.new-chat-button--collapsed {
  width: 96px;
}

.new-chat-button:hover {
  background: var(--semantic-colors-accent-primary);
  border-color: var(--semantic-colors-accent-primary);
}

.new-chat-button:active {
  background: var(--semantic-colors-accent-gradient);
  transform: scale(0.98);
}
```

---

### 5. Sidebar Component Set

**Component ID**: `4002:13380`  
**Variants**: 2 states

#### Default Sidebar (`4002:13381`)
- **Background**: `semantic.colors.background.overlay` (`rgba(247, 247, 247, 0.2)`)
- **Border Radius**: 4px
- **Layout**: Full width with chat history, navigation, and controls
- **Justification**: Space-between (top and bottom elements)

#### Collapsed Sidebar (`4025:17381`)
- **Background**: `semantic.colors.background.overlay` (`rgba(247, 247, 247, 0.2)`)
- **Border Radius**: 4px  
- **Layout**: Collapsed width, icons only
- **Responsive**: Maintains functionality in minimal space

#### CSS Token Mapping
```css
.sidebar {
  background: var(--semantic-colors-background-overlay);
  border-radius: var(--primitives-border-radius-sm);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: var(--primitives-spacing-3);
}

.sidebar--default {
  width: 270px;
}

.sidebar--collapsed {
  width: 80px;
}
```

---

### 6. Navigation Text Component Set

**Component ID**: `4002:13712`  
**Variants**: 10 total (5 words × 2 states)

#### Word Variants
- **Day** - Contextual date reference
- **Date** - Specific date display  
- **Time** - Time stamp
- **Name** - User identifier
- **Smiley** - Emoji/mood indicator (36px × 36px icon)

#### Interactive States

##### Default State
- **Typography**: System default for navigation
- **Color**: `semantic.colors.text.secondary`
- **Hover**: None (static display)

##### Hover State  
- **Typography**: Enhanced visibility
- **Color**: `semantic.colors.text.primary`
- **Interactive**: Clickable navigation elements

#### CSS Token Mapping
```css
.navigation-text {
  font-family: var(--primitives-typography-font-family-primary);
  font-size: var(--primitives-typography-font-size-sm);
  color: var(--semantic-colors-text-secondary);
  transition: color 200ms ease;
}

.navigation-text:hover {
  color: var(--semantic-colors-text-primary);
}

.navigation-text--smiley {
  width: 36px;
  height: 36px;
}
```

---

### 7. Chat Conversation Component

**Component ID**: `4027:18954`  
**Layout**: Conversation flow with alternating message bubbles

#### Structure
```
chat conversation/
├── assistant chat bubble 01/
├── user chat bubble 01/
├── assistant chat bubble 02/
└── user chat bubble 02/
```

#### Message Bubble Types

##### Assistant Bubbles
- **Width**: 468px (fixed)
- **Alignment**: Right-aligned in container
- **Background**: `semantic.colors.background.assistant`
- **Text Color**: `semantic.colors.text.primary`
- **Border Radius**: Asymmetric (rounded away from conversation flow)

##### User Bubbles  
- **Width**: Flexible (fill available space)
- **Alignment**: Left-aligned in container
- **Background**: `semantic.colors.background.user`
- **Text Color**: `semantic.colors.text.primary`
- **Border Radius**: Asymmetric (rounded away from conversation flow)

#### Spacing
- **Gap Between Messages**: 24px
- **Internal Bubble Padding**: 12px
- **Container Width**: 950px

#### CSS Token Mapping
```css
.chat-conversation {
  width: 950px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--primitives-spacing-6);
}

.message-bubble {
  padding: var(--primitives-spacing-3);
  border-radius: var(--primitives-border-radius-lg);
  max-width: 80%;
}

.message-bubble--assistant {
  width: 468px;
  background: var(--semantic-colors-background-assistant);
  align-self: flex-end;
}

.message-bubble--user {
  background: var(--semantic-colors-background-user);
  align-self: flex-start;
}
```

---

### 8. Suggestion Shapes Component Set

**Component ID**: `4002:13350`  
**Variants**: 7 decorative shapes

#### Shape Variants
- **Shape 1-7**: Decorative background elements
- **Dimensions**: 32px × 32px each
- **Background**: `semantic.colors.background.secondary` (`#FFFFFF`)
- **Purpose**: Visual enhancement for suggestion interface

#### Layout
- **Arrangement**: Horizontal row
- **Gap**: 16px between shapes
- **Padding**: 20px container padding

#### CSS Token Mapping
```css
.suggestion-shapes {
  display: flex;
  align-items: center;
  gap: var(--primitives-spacing-4);
  padding: var(--primitives-spacing-5);
}

.suggestion-shape {
  width: 32px;
  height: 32px;
  background: var(--semantic-colors-background-secondary);
}
```

---

### 9. Chat History Component

**Component ID**: `4004:15738`  
**Layout**: Sidebar navigation element

#### Structure
- **Container Width**: 270px
- **Background**: Transparent
- **Border Radius**: 4px
- **Internal Padding**: 4px
- **Row Layout**: Horizontal alignment with 8px gap
- **Item Padding**: 8px × 12px

#### CSS Token Mapping
```css
.chat-history {
  width: 270px;
  padding: var(--primitives-spacing-1);
  display: flex;
  flex-direction: column;
  gap: var(--primitives-spacing-1);
}

.chat-history__item {
  display: flex;
  align-items: center;
  gap: var(--primitives-spacing-2);
  padding: var(--primitives-spacing-2) var(--primitives-spacing-3);
  border-radius: var(--primitives-border-radius-sm);
}
```

---

### 10. Icons Component Set

**Component ID**: `4004:15940`  
**Variants**: 7 icons

#### Icon Types
- **Paperclip** (`4004:15936`) - File attachment
- **Camera** (`4004:15938`) - Image capture/upload
- **Send** (`4004:15935`) - Message submission
- **Plus** (`4004:15937`) - Add/create actions
- **Arrow** (`4004:15939`) - Navigation/direction
- **Minus** (`4004:15934`) - Remove/subtract actions
- **Trash** (`4004:15933`) - Delete actions

#### Specifications
- **Size**: 24px × 24px
- **Format**: SVG
- **Color**: Inherits from parent component
- **Style**: Consistent line weight and corner radius

#### CSS Token Mapping
```css
.icon {
  width: 24px;
  height: 24px;
  color: currentColor;
}
```

---

### 11. Thumbnail Images Component Set

**Component ID**: `4002:13825`  
**Variants**: 4 thumbnail options

#### Thumbnail Types
- **Thumbnail 01-04**: Different image previews
- **Dimensions**: 21px × 21px
- **Background**: `semantic.colors.background.secondary` (`#FFFFFF`)
- **Purpose**: File/image attachment previews

#### Layout
- **Arrangement**: Horizontal row
- **Gap**: 4px between thumbnails
- **Container Padding**: 20px

#### CSS Token Mapping
```css
.thumbnail-images {
  display: flex;
  gap: var(--primitives-spacing-1);
  padding: var(--primitives-spacing-5);
}

.thumbnail {
  width: 21px;
  height: 21px;
  background: var(--semantic-colors-background-secondary);
  border-radius: var(--primitives-border-radius-xs);
}
```

#### Word Variants
- **Day** - Contextual date reference
- **Date** - Specific date display  
- **Time** - Time stamp
- **Name** - User identifier
- **Smiley** - Emoji/mood indicator (36px × 36px icon)

#### Interactive States

##### Default State
- **Typography**: System default for navigation
- **Color**: `semantic.colors.text.secondary`
- **Hover**: None (static display)

##### Hover State  
- **Typography**: Enhanced visibility
- **Color**: `semantic.colors.text.primary`
- **Interactive**: Clickable navigation elements

#### CSS Token Mapping
```css
.navigation-text {
  font-family: var(--primitives-typography-font-family-primary);
  font-size: var(--primitives-typography-font-size-sm);
  color: var(--semantic-colors-text-secondary);
  transition: color 200ms ease;
}

.navigation-text:hover {
  color: var(--semantic-colors-text-primary);
}

.navigation-text--smiley {
  width: 36px;
  height: 36px;
}
```

---

### 7. Chat Conversation Component

**Component ID**: `4027:18954`  
**Layout**: Conversation flow with alternating message bubbles

#### Structure
```
chat conversation/
├── assistant chat bubble 01/
├── user chat bubble 01/
├── assistant chat bubble 02/
└── user chat bubble 02/
```

#### Message Bubble Types

##### Assistant Bubbles
- **Width**: 468px (fixed)
- **Alignment**: Right-aligned in container
- **Background**: `semantic.colors.background.assistant`
- **Text Color**: `semantic.colors.text.primary`
- **Border Radius**: Asymmetric (rounded away from conversation flow)

##### User Bubbles  
- **Width**: Flexible (fill available space)
- **Alignment**: Left-aligned in container
- **Background**: `semantic.colors.background.user`
- **Text Color**: `semantic.colors.text.primary`
- **Border Radius**: Asymmetric (rounded away from conversation flow)

#### Spacing
- **Gap Between Messages**: 24px
- **Internal Bubble Padding**: 12px
- **Container Width**: 950px

#### CSS Token Mapping
```css
.chat-conversation {
  width: 950px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--primitives-spacing-6);
}

.message-bubble {
  padding: var(--primitives-spacing-3);
  border-radius: var(--primitives-border-radius-lg);
  max-width: 80%;
}

.message-bubble--assistant {
  width: 468px;
  background: var(--semantic-colors-background-assistant);
  align-self: flex-end;
}

.message-bubble--user {
  background: var(--semantic-colors-background-user);
  align-self: flex-start;
}
```

---

### 8. Suggestion Shapes Component Set

**Component ID**: `4002:13350`  
**Variants**: 7 decorative shapes

#### Shape Variants
- **Shape 1-7**: Decorative background elements
- **Dimensions**: 32px × 32px each
- **Background**: `semantic.colors.background.secondary` (`#FFFFFF`)
- **Purpose**: Visual enhancement for suggestion interface

#### Layout
- **Arrangement**: Horizontal row
- **Gap**: 16px between shapes
- **Padding**: 20px container padding

#### CSS Token Mapping
```css
.suggestion-shapes {
  display: flex;
  align-items: center;
  gap: var(--primitives-spacing-4);
  padding: var(--primitives-spacing-5);
}

.suggestion-shape {
  width: 32px;
  height: 32px;
  background: var(--semantic-colors-background-secondary);
}
```

---

### 9. Chat History Component

**Component ID**: `4004:15738`  
**Layout**: Sidebar navigation element

#### Structure
- **Container Width**: 270px
- **Background**: Transparent
- **Border Radius**: 4px
- **Internal Padding**: 4px
- **Row Layout**: Horizontal alignment with 8px gap
- **Item Padding**: 8px × 12px

#### CSS Token Mapping
```css
.chat-history {
  width: 270px;
  padding: var(--primitives-spacing-1);
  display: flex;
  flex-direction: column;
  gap: var(--primitives-spacing-1);
}

.chat-history__item {
  display: flex;
  align-items: center;
  gap: var(--primitives-spacing-2);
  padding: var(--primitives-spacing-2) var(--primitives-spacing-3);
  border-radius: var(--primitives-border-radius-sm);
}
```

---

### 10. Icons Component Set

**Component ID**: `4004:15940`  
**Variants**: 7 icons

#### Icon Types
- **Paperclip** (`4004:15936`) - File attachment
- **Camera** (`4004:15938`) - Image capture/upload
- **Send** (`4004:15935`) - Message submission
- **Plus** (`4004:15937`) - Add/create actions
- **Arrow** (`4004:15939`) - Navigation/direction
- **Minus** (`4004:15934`) - Remove/subtract actions
- **Trash** (`4004:15933`) - Delete actions

#### Specifications
- **Size**: 24px × 24px
- **Format**: SVG
- **Color**: Inherits from parent component
- **Style**: Consistent line weight and corner radius

#### CSS Token Mapping
```css
.icon {
  width: 24px;
  height: 24px;
  color: currentColor;
}
```

---

### 11. Thumbnail Images Component Set

**Component ID**: `4002:13825`  
**Variants**: 4 thumbnail options

#### Thumbnail Types
- **Thumbnail 01-04**: Different image previews
- **Dimensions**: 21px × 21px
- **Background**: `semantic.colors.background.secondary` (`#FFFFFF`)
- **Purpose**: File/image attachment previews

#### Layout
- **Arrangement**: Horizontal row
- **Gap**: 4px between thumbnails
- **Container Padding**: 20px

#### CSS Token Mapping
```css
.thumbnail-images {
  display: flex;
  gap: var(--primitives-spacing-1);
  padding: var(--primitives-spacing-5);
}

.thumbnail {
  width: 21px;
  height: 21px;
  background: var(--semantic-colors-background-secondary);
  border-radius: var(--primitives-border-radius-xs);
}
```

---

## 🎨 Color System

### Brand Colors

#### Orange Palette
- **Base**: `#FF7D59` - Primary brand color
- **60%**: `#D4684A` - Darker variant
- **50%**: `#FF9375` - Mid-tone
- **70%**: `#AA533B` - Deep variant  
- **40%**: `#FFA890` - Light variant
- **80%**: `#803F2D` - Very dark
- **30%**: `#FFBEAC` - Very light
- **90%**: `#552A1E` - Darkest
- **20%**: `#FFD4C8` - Lightest
- **100%**: `#331912` - Maximum dark
- **10%**: `#FFE5DE` - Minimum tint

#### Blue Palette  
- **Base**: `#2180EC` - Secondary brand color
- **60%**: `#1C6BC5` - Darker variant
- **50%**: `#4695EF` - Mid-tone
- **70%**: `#16559D` - Deep variant
- **40%**: `#6BAAF2` - Light variant
- **80%**: `#114076` - Very dark
- **30%**: `#90BFF5` - Very light
- **90%**: `#0B2B4F` - Darkest
- **20%**: `#B5D5F9` - Lightest
- **100%**: `#071A2F` - Maximum dark
- **10%**: `#D3E6FB` - Minimum tint

### Semantic Color Tokens

#### Background Colors
```css
--semantic-colors-background-primary: #000000;
--semantic-colors-background-secondary: #F7F7F7;
--semantic-colors-background-overlay: rgba(247, 247, 247, 0.2);
--semantic-colors-background-assistant: #F7F7F7;
--semantic-colors-background-user: #FFFFFF;
```

#### Text Colors
```css
--semantic-colors-text-primary: #000000;
--semantic-colors-text-secondary: #404040;
--semantic-colors-text-placeholder: #808080;
--semantic-colors-text-inverse: #FFFFFF;
```

#### Border Colors
```css
--semantic-colors-border-primary: #000000;
--semantic-colors-border-secondary: #171717;
```

#### Accent Colors
```css
--semantic-colors-accent-primary: #2180EC;
--semantic-colors-accent-gradient: linear-gradient(135deg, #69DEF2 0%, #126FD8 100%);
```

---

## 📐 Spacing System

### Primitive Spacing Scale
```css
--primitives-spacing-0: 0px;
--primitives-spacing-1: 4px;
--primitives-spacing-2: 8px;
--primitives-spacing-2-5: 10px;
--primitives-spacing-3: 12px;
--primitives-spacing-4: 16px;
--primitives-spacing-5: 20px;
--primitives-spacing-6: 24px;
--primitives-spacing-8: 32px;
```

### Semantic Spacing
```css
--semantic-spacing-component-gap: var(--primitives-spacing-6);
--semantic-spacing-section-gap: var(--primitives-spacing-8);
--semantic-spacing-page-padding: var(--primitives-spacing-12);
```

---

## 🔤 Typography System

### Font Families
```css
--primitives-typography-font-family-primary: "Mabry Pro", sans-serif;
--primitives-typography-font-family-display: "Behind The Nineties", display;
```

### Font Weights
```css
--primitives-typography-font-weight-regular: 400;
--primitives-typography-font-weight-medium: 500;
--primitives-typography-font-weight-bold: 700;
```

### Font Sizes
```css
--primitives-typography-font-size-sm: 14px;
--primitives-typography-font-size-base: 16px;
--primitives-typography-font-size-lg: 18px;
--primitives-typography-font-size-xl: 20px;
--primitives-typography-font-size-2xl: 32px;
--primitives-typography-font-size-display: 42px;
```

### Line Heights
```css
--primitives-typography-line-height-tight: 1.111;
--primitives-typography-line-height-base: 1.3;
--primitives-typography-line-height-relaxed: 1.238;
```

### Semantic Typography
```css
--semantic-typography-body-large: {
  font-family: var(--primitives-typography-font-family-primary);
  font-weight: var(--primitives-typography-font-weight-medium);
  font-size: var(--primitives-typography-font-size-lg);
  line-height: var(--primitives-typography-line-height-tight);
}

--semantic-typography-body-base: {
  font-family: var(--primitives-typography-font-family-primary);
  font-weight: var(--primitives-typography-font-weight-regular);
  font-size: var(--primitives-typography-font-size-base);
  line-height: var(--primitives-typography-line-height-base);
}

--semantic-typography-display: {
  font-family: var(--primitives-typography-font-family-display);
  font-weight: var(--primitives-typography-font-weight-medium);
  font-size: var(--primitives-typography-font-size-display);
  line-height: var(--primitives-typography-line-height-relaxed);
}
```

---

## 🌟 Shadow System

### Button Shadows
```css
--semantic-shadows-button-default: 
  0px 1px 2px 0px rgba(10, 13, 18, 0.06),
  0px 1px 1px 0px rgba(10, 13, 18, 0.14);

### Brand Colors

#### Orange Palette
- **Base**: `#FF7D59` - Primary brand color
- **60%**: `#D4684A` - Darker variant
- **50%**: `#FF9375` - Mid-tone
- **70%**: `#AA533B` - Deep variant  
- **40%**: `#FFA890` - Light variant
- **80%**: `#803F2D` - Very dark
- **30%**: `#FFBEAC` - Very light
- **90%**: `#552A1E` - Darkest
- **20%**: `#FFD4C8` - Lightest
- **100%**: `#331912` - Maximum dark
- **10%**: `#FFE5DE` - Minimum tint

#### Blue Palette  
- **Base**: `#2180EC` - Secondary brand color
- **60%**: `#1C6BC5` - Darker variant
- **50%**: `#4695EF` - Mid-tone
- **70%**: `#16559D` - Deep variant
- **40%**: `#6BAAF2` - Light variant
- **80%**: `#114076` - Very dark
- **30%**: `#90BFF5` - Very light
- **90%**: `#0B2B4F` - Darkest
- **20%**: `#B5D5F9` - Lightest
- **100%**: `#071A2F` - Maximum dark
- **10%**: `#D3E6FB` - Minimum tint

### Semantic Color Tokens

#### Background Colors
```css
--semantic-colors-background-primary: #000000;
--semantic-colors-background-secondary: #F7F7F7;
--semantic-colors-background-overlay: rgba(247, 247, 247, 0.2);
--semantic-colors-background-assistant: #F7F7F7;
--semantic-colors-background-user: #FFFFFF;
```

#### Text Colors
```css
--semantic-colors-text-primary: #000000;
--semantic-colors-text-secondary: #404040;
--semantic-colors-text-placeholder: #808080;
--semantic-colors-text-inverse: #FFFFFF;
```

#### Border Colors
```css
--semantic-colors-border-primary: #000000;
--semantic-colors-border-secondary: #171717;
```

#### Accent Colors
```css
--semantic-colors-accent-primary: #2180EC;
--semantic-colors-accent-gradient: linear-gradient(135deg, #69DEF2 0%, #126FD8 100%);
```

---

## 📐 Spacing System

### Primitive Spacing Scale
```css
--primitives-spacing-0: 0px;
--primitives-spacing-1: 4px;
--primitives-spacing-2: 8px;
--primitives-spacing-2-5: 10px;
--primitives-spacing-3: 12px;
--primitives-spacing-4: 16px;
--primitives-spacing-5: 20px;
--primitives-spacing-6: 24px;
--primitives-spacing-8: 32px;
```

### Semantic Spacing
```css
--semantic-spacing-component-gap: var(--primitives-spacing-6);
--semantic-spacing-section-gap: var(--primitives-spacing-8);
--semantic-spacing-page-padding: var(--primitives-spacing-12);
```

---

## 🔤 Typography System

### Font Families
```css
--primitives-typography-font-family-primary: "Mabry Pro", sans-serif;
--primitives-typography-font-family-display: "Behind The Nineties", display;
```

### Font Weights
```css
--primitives-typography-font-weight-regular: 400;
--primitives-typography-font-weight-medium: 500;
--primitives-typography-font-weight-bold: 700;
```

### Font Sizes
```css
--primitives-typography-font-size-sm: 14px;
--primitives-typography-font-size-base: 16px;
--primitives-typography-font-size-lg: 18px;
--primitives-typography-font-size-xl: 20px;
--primitives-typography-font-size-2xl: 32px;
--primitives-typography-font-size-display: 42px;
```

### Line Heights
```css
--primitives-typography-line-height-tight: 1.111;
--primitives-typography-line-height-base: 1.3;
--primitives-typography-line-height-relaxed: 1.238;
```

### Semantic Typography
```css
--semantic-typography-body-large: {
  font-family: var(--primitives-typography-font-family-primary);
  font-weight: var(--primitives-typography-font-weight-medium);
  font-size: var(--primitives-typography-font-size-lg);
  line-height: var(--primitives-typography-line-height-tight);
}

--semantic-typography-body-base: {
  font-family: var(--primitives-typography-font-family-primary);
  font-weight: var(--primitives-typography-font-weight-regular);
  font-size: var(--primitives-typography-font-size-base);
  line-height: var(--primitives-typography-line-height-base);
}

--semantic-typography-display: {
  font-family: var(--primitives-typography-font-family-display);
  font-weight: var(--primitives-typography-font-weight-medium);
  font-size: var(--primitives-typography-font-size-display);
  line-height: var(--primitives-typography-line-height-relaxed);
}
```

---

## 🌟 Shadow System

### Button Shadows
```css
--semantic-shadows-button-default: 
  0px 1px 2px 0px rgba(10, 13, 18, 0.06),
  0px 1px 1px 0px rgba(10, 13, 18, 0.14);

--semantic-shadows-button-focus:
  0px 1px 2px 0px rgba(10, 13, 18, 0.05);

--semantic-shadows-suggestion-card-hover:
  0px 0px 1px 4px rgba(255, 255, 255, 0.1),
  0px 0px 100px 0px rgba(254, 235, 229, 1),
  inset 0px 2px 1px 0px rgba(255, 255, 255, 0.25),
  inset 0px -2px 2px 0px rgba(0, 0, 0, 0.25);
```

---

## 🔄 State Management & Interactions

### Window State Transitions

#### From Suggestion Interface to Chat Conversation
**Trigger**: User submits first message
**Changes**:
1. Suggestion cards fade out
2. Suggestion shapes disappear  
3. Greeting section slides up and out
4. Chat input transitions from full (180px) to short (100px)
5. Chat conversation component slides in from bottom
6. Sidebar becomes visible (if not already)

#### Component State Persistence
- **Chat Input**: Maintains content during height transition
- **Icon Buttons**: Preserve attachment states
- **Sidebar**: Retains expanded/collapsed preference
- **Navigation**: Updates context from "new chat" to "conversation"

### Responsive Behavior

#### Desktop (1440px)
- **Chat Input**: 740px width
- **Sidebar**: Full width (270px default, 80px collapsed)
- **Container**: 1344px content width with 48px padding

#### Mobile (375px)  
- **Chat Input**: Responsive width (calc(100vw - 46px))
- **Sidebar**: Overlay mode or hidden
- **Container**: 328px content width with 23px padding

### Accessibility Considerations

#### Keyboard Navigation
- **Tab Order**: Logical flow through interactive elements
- **Focus Indicators**: 2px solid accent color outline with 2px offset
- **Skip Links**: Available for main content areas

#### Screen Reader Support
- **ARIA Labels**: All interactive elements properly labeled
- **Live Regions**: Chat messages announced when added
- **State Changes**: Component state changes communicated

#### Color Contrast
- **Text on Background**: Minimum 4.5:1 ratio maintained
- **Interactive Elements**: Enhanced contrast on focus/hover
- **Error States**: Additional visual indicators beyond color

---

## 🚀 Implementation Guidelines

### Component Usage Patterns

#### Chat Input Integration
```jsx
<ChatInput 
  variant={conversationActive ? "short" : "full"}
  state={inputState}
  onSubmit={handleMessageSubmit}
  onAttachFiles={handleFileAttachment}
  onAttachImages={handleImageAttachment}
  placeholder="Ask me a question..."
  maxLength={1000}
/>
```

#### Window State Management
```jsx
const [windowState, setWindowState] = useState('suggestion'); // 'suggestion' | 'conversation'

const handleFirstMessage = (message) => {
  setWindowState('conversation');
  // Trigger transition animations
};
```

#### Responsive Layout
```css
.app-container {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  padding: var(--semantic-spacing-page-padding);
}

@media (max-width: 768px) {
  .app-container {
    padding: var(--primitives-spacing-6);
  }
}
```

### Animation Specifications

#### Window Transitions
```css
.window-transition {
  transition: all 400ms cubic-bezier(0.4, 0, 0.2, 1);
}

.chat-input-resize {
  transition: height 300ms ease-in-out;
}

.fade-in {
  animation: fadeIn 300ms ease-in;
}

.slide-up {
  animation: slideUp 400ms ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}
```

---

## 📋 Component Checklist

### Pre-Implementation
- [ ] Design tokens imported from `tokens.json`
- [ ] Component variants mapped to design system
- [ ] Interactive states defined
- [ ] Accessibility requirements reviewed
- [ ] Responsive breakpoints planned

### Development
- [ ] Component structure matches Figma hierarchy
- [ ] CSS custom properties used for all design tokens
- [ ] Interactive states implemented with proper transitions
- [ ] Keyboard navigation functional
- [ ] Focus management implemented
- [ ] ARIA attributes added

### Testing
- [ ] All component variants render correctly
- [ ] Interactive states function as expected
- [ ] Window transitions smooth and performant
- [ ] Responsive behavior verified across devices
- [ ] Accessibility tested with screen readers
- [ ] Color contrast validated

### Documentation
- [ ] Component API documented
- [ ] Usage examples provided
- [ ] Design decisions explained
- [ ] Token mapping verified
- [ ] Implementation notes updated

---

## 🔧 Development Notes

### Critical Implementation Details

1. **Chat Input Height Transition**: Must be smooth and maintain content during resize from 180px to 100px
2. **Icon Button States**: Attachment states must persist across window transitions
3. **Focus Management**: When transitioning between windows, focus should move logically
4. **Animation Performance**: Use `transform` and `opacity` for smooth 60fps animations
5. **Token Consistency**: All measurements and colors must reference design tokens

### Performance Considerations

- **Component Lazy Loading**: Non-critical components should load on demand
- **Animation Optimization**: Use `will-change` property sparingly and remove after animations
- **Image Optimization**: Thumbnail images should be optimized for web delivery
- **State Management**: Minimize re-renders during window transitions

### Browser Support

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **CSS Features**: CSS Grid, Flexbox, Custom Properties, CSS Transitions
- **JavaScript Features**: ES2020+, Async/Await, Optional Chaining

---

*This documentation serves as the complete reference for implementing the Beth Assistant Design System. All measurements, colors, and interactions are precisely defined to ensure consistent implementation across all platforms and devices.* 