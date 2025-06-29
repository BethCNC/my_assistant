# Beth Assistant - Simplified Deployment Guide

## Quick Start Commands

### Development
```bash
# Web app only
npm run dev

# Health journey app
npm run dev:health  

# Desktop app (opens Electron window)
npm run dev:desktop
```

### Building & Packaging

```bash
# Build everything
npm run build

# Build just web frontend
npm run build:frontend

# Build just health app
npm run build:health

# Build web + package Mac desktop app
npm run build:desktop
```

### Deployment

```bash
# Deploy web app to Firebase
npm run deploy:web

# Deploy backend to Google Cloud
npm run deploy:backend  

# Deploy everything (build + web + backend)
npm run deploy:all
```

### Desktop App Packaging

```bash
# Package for Mac (ARM64 - M1/M2 Macs)
npm run package:mac

# Package for Mac (Universal - Intel + ARM)
npm run package:mac-universal
```

### Utilities

```bash
# Clean build artifacts
npm run clean

# Start backend server
npm run backend
```

## File Structure After Build

```
my_assistant/
├── dist/                     # Desktop app packages
│   └── BethAssistant-darwin-arm64/
├── frontend/.next/           # Web build files
└── beth_health_journey_app/.next/  # Health app build files
```

## Deployment Targets

- **Web App**: Firebase Hosting (frontend)
- **Backend**: Google Cloud Run (backend) 
- **Desktop**: Mac .app bundle (local distribution)

## Development Workflow

1. **Daily development**: `npm run dev`
2. **Desktop testing**: `npm run dev:desktop` 
3. **Health data work**: `npm run dev:health`
4. **Deploy changes**: `npm run deploy:all`
5. **Package desktop**: `npm run build:desktop`

## Notes

- Desktop app loads web app at `localhost:3000` in dev mode
- Production desktop app uses built static files
- Storybook removed (no longer used)
- All builds are cleaned with `npm run clean` 