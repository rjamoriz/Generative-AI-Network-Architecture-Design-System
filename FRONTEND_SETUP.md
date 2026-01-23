# Frontend Setup Guide

## 📋 Overview

The frontend is a **Next.js 14** application with:
- **React 18** with TypeScript
- **TailwindCSS** for styling
- **React Query** for data fetching
- **Zustand** for state management
- **React Flow** for network diagram visualization
- **Recharts** for analytics

---

## 🚀 Quick Start (Local Development)

### **Option 1: Automated Setup (Recommended)**

```powershell
cd frontend
.\START_FRONTEND.ps1
```

This script will:
1. Check Node.js installation
2. Install dependencies if needed
3. Set environment variables
4. Start the development server

### **Option 2: Manual Setup**

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set API URL
$env:NEXT_PUBLIC_API_URL="http://localhost:8000"

# Start development server
npm run dev
```

The frontend will be available at: **http://localhost:3000**

---

## 🐳 Docker Setup (When Network is Available)

### **Prerequisites**
- Docker and Docker Compose installed
- Backend already running

### **Build and Start**

```powershell
# From project root
docker-compose --env-file .env.docker up -d frontend
```

### **Check Status**

```powershell
docker ps
docker logs network-design-frontend
```

### **Access**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

---

## 📦 Requirements

### **Node.js Version**
- Node.js 18.0.0 or higher
- npm 9.0.0 or higher

### **Check Your Version**

```powershell
node --version
npm --version
```

### **Install Node.js**
Download from: https://nodejs.org/

---

## 🔧 Configuration

### **Environment Variables**

Create `.env.local` in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Network Architecture Design System
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### **API Connection**

The frontend connects to the backend API at:
- **Development**: http://localhost:8000
- **Docker**: http://backend:8000 (internal network)

---

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js 14 App Router
│   ├── (auth)/            # Authentication pages
│   ├── (dashboard)/       # Main application pages
│   └── api/               # API routes
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   ├── forms/            # Form components
│   └── diagrams/         # Network diagram components
├── lib/                   # Utilities and helpers
├── hooks/                 # Custom React hooks
├── stores/                # Zustand state stores
├── types/                 # TypeScript type definitions
└── public/                # Static assets
```

---

## 🛠️ Available Scripts

### **Development**

```powershell
npm run dev          # Start development server (port 3000)
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript type checking
```

---

## 🎨 Features

### **1. Network Design Canvas**
- Visual network topology builder
- Drag-and-drop components
- Real-time validation

### **2. AI-Powered Design**
- LLM-based design suggestions
- Automated optimization
- Best practice recommendations

### **3. Historical Data Integration**
- View past designs
- Compare configurations
- Track changes over time

### **4. Validation & Testing**
- Real-time design validation
- Configuration testing
- Compliance checking

### **5. Export & Documentation**
- Export to various formats
- Auto-generated documentation
- Configuration templates

---

## 🔗 Integration with Backend

### **API Endpoints Used**

```typescript
// Design Management
POST   /api/designs              // Create new design
GET    /api/designs              // List all designs
GET    /api/designs/{id}         // Get specific design
PUT    /api/designs/{id}         // Update design
DELETE /api/designs/{id}         // Delete design

// Validation
POST   /api/validate             // Validate design

// AI Generation
POST   /api/generate             // Generate design with AI

// Historical Data
GET    /api/historical           // Get historical designs
```

### **Authentication**

The frontend uses JWT tokens for authentication:
1. Login via `/api/auth/login`
2. Token stored in localStorage
3. Included in all API requests

---

## 🐛 Troubleshooting

### **Port 3000 Already in Use**

```powershell
# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use a different port
npm run dev -- -p 3001
```

### **Cannot Connect to Backend**

1. Verify backend is running:
   ```powershell
   curl http://localhost:8000/health
   ```

2. Check CORS settings in backend

3. Verify `NEXT_PUBLIC_API_URL` is set correctly

### **Dependencies Installation Failed**

```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json

# Reinstall
npm install
```

---

## 📊 Performance

### **Build Optimization**

The frontend is configured with:
- **SWC** for faster compilation
- **Image optimization** with Next.js Image
- **Code splitting** for smaller bundles
- **Standalone output** for Docker

### **Production Build**

```powershell
npm run build
npm run start
```

---

## 🔐 Security

### **Headers**

Security headers are configured in `next.config.js`:
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- Referrer-Policy: origin-when-cross-origin

### **Environment Variables**

- Never commit `.env.local`
- Use `NEXT_PUBLIC_` prefix for client-side variables
- Keep API keys server-side only

---

## 📝 Next Steps

1. **Start the frontend** using one of the methods above
2. **Open http://localhost:3000** in your browser
3. **Ensure backend is running** at http://localhost:8000
4. **Create your first network design**

---

## 🆘 Support

If you encounter issues:

1. Check that Node.js 18+ is installed
2. Verify backend is running and healthy
3. Check browser console for errors
4. Review `FRONTEND_SETUP.md` for troubleshooting

---

**Status**: Frontend is configured and ready to run locally. Docker build will work once network connectivity is restored.
