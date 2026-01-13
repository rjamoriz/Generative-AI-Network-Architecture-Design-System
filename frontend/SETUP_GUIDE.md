# Frontend Setup Guide

Complete guide for setting up and running the frontend application.

---

## 📋 Prerequisites

### Required Software
- **Node.js**: 18.0.0 or higher
- **npm**: 9.0.0 or higher (comes with Node.js)
- **Git**: For version control

### Check Versions
```bash
node --version  # Should be v18.0.0 or higher
npm --version   # Should be 9.0.0 or higher
```

### Install Node.js
If you don't have Node.js installed:

**macOS/Linux:**
```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

**Windows:**
- Download from [nodejs.org](https://nodejs.org/)
- Run the installer
- Restart your terminal

---

## 🚀 Installation Steps

### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 2: Install Dependencies
```bash
npm install
```

This will install all dependencies listed in `package.json`:
- Next.js 14
- React 18
- TypeScript
- TailwindCSS
- And all other required packages

**Expected output:**
```
added 500+ packages in 30s
```

### Step 3: Configure Environment
```bash
# Copy the example environment file
cp .env.example .env.local

# Edit the file with your settings
nano .env.local  # or use your preferred editor
```

**Required environment variables:**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1
```

### Step 4: Verify Backend is Running
Before starting the frontend, ensure the backend API is running:

```bash
# In a separate terminal, check backend health
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", ...}
```

If the backend isn't running, start it first:
```bash
cd ../backend
docker-compose up -d
# or
python -m uvicorn app.main:app --reload
```

### Step 5: Start Development Server
```bash
npm run dev
```

**Expected output:**
```
▲ Next.js 14.1.0
- Local:        http://localhost:3000
- Network:      http://192.168.1.x:3000

✓ Ready in 2.5s
```

### Step 6: Open in Browser
```bash
# macOS
open http://localhost:3000

# Linux
xdg-open http://localhost:3000

# Windows
start http://localhost:3000
```

---

## 🏗️ Project Structure Setup

After installation, you'll need to create the source files. Here's the recommended structure:

```bash
# Create directory structure
mkdir -p src/app
mkdir -p src/components/ui
mkdir -p src/components/design
mkdir -p src/components/network
mkdir -p src/lib
mkdir -p src/hooks
mkdir -p src/types
mkdir -p src/store
mkdir -p public/images
```

---

## 📝 Creating Core Files

### 1. Root Layout (`src/app/layout.tsx`)

```typescript
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Network Architecture Design System',
  description: 'AI-Powered Network Design Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
```

### 2. Home Page (`src/app/page.tsx`)

```typescript
export default function Home() {
  return (
    <main className="min-h-screen p-24">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold mb-4">
          Network Architecture Design System
        </h1>
        <p className="text-xl text-gray-600">
          AI-Powered Network Design Platform
        </p>
      </div>
    </main>
  )
}
```

### 3. Global Styles (`src/app/globals.css`)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 47.4% 11.2%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 47.4% 11.2%;
    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

### 4. API Client (`src/lib/api-client.ts`)

```typescript
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_VERSION = process.env.NEXT_PUBLIC_API_VERSION || 'v1'

export const apiClient = axios.create({
  baseURL: `${API_URL}/api/${API_VERSION}`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

### 5. TypeScript Types (`src/types/design.ts`)

```typescript
export interface NetworkDesign {
  design_id: string
  name: string
  description: string
  network_type: string
  topology: Topology
  components: Component[]
  connections: Connection[]
  created_at: string
  updated_at: string
}

export interface Topology {
  topology_type: string
  layers: Layer[]
}

export interface Component {
  component_id: string
  name: string
  type: string
  specifications: Record<string, any>
}

export interface Connection {
  connection_id: string
  source_id: string
  target_id: string
  type: string
}

export interface Layer {
  name: string
  components: string[]
}
```

---

## 🧪 Testing the Setup

### 1. Check Development Server
```bash
# Server should be running at http://localhost:3000
curl http://localhost:3000
```

### 2. Test API Connection
```bash
# From browser console
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
```

### 3. Verify TypeScript
```bash
npm run type-check
```

### 4. Run Linter
```bash
npm run lint
```

---

## 🔧 Development Workflow

### Daily Development
```bash
# 1. Pull latest changes
git pull

# 2. Install any new dependencies
npm install

# 3. Start dev server
npm run dev

# 4. Make changes and test

# 5. Run linter before committing
npm run lint

# 6. Commit changes
git add .
git commit -m "feat: add new feature"
git push
```

### Building for Production
```bash
# Create production build
npm run build

# Test production build locally
npm start

# Build should complete without errors
```

---

## 🐛 Troubleshooting

### Port 3000 Already in Use
```bash
# Find and kill process using port 3000
# macOS/Linux:
lsof -ti:3000 | xargs kill -9

# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use a different port
PORT=3001 npm run dev
```

### Module Not Found Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### TypeScript Errors
```bash
# Regenerate TypeScript config
npx tsc --init

# Check for type errors
npm run type-check
```

### API Connection Issues
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS settings in backend
# Ensure frontend URL is in CORS_ORIGINS

# Check environment variables
cat .env.local
```

### Build Failures
```bash
# Clear Next.js cache
rm -rf .next

# Rebuild
npm run build
```

---

## 📚 Next Steps

After setup is complete:

1. **Explore the codebase** - Familiarize yourself with the structure
2. **Read the README** - Understand the architecture
3. **Check API docs** - http://localhost:8000/docs
4. **Start building** - Create your first component
5. **Test thoroughly** - Ensure everything works

---

## 🆘 Getting Help

### Resources
- **Next.js Docs**: https://nextjs.org/docs
- **React Docs**: https://react.dev
- **TailwindCSS**: https://tailwindcss.com/docs
- **Backend API**: http://localhost:8000/docs

### Common Commands Reference
```bash
# Development
npm run dev          # Start dev server
npm run build        # Production build
npm start            # Start production server
npm run lint         # Run ESLint
npm run type-check   # Check TypeScript

# Dependencies
npm install          # Install all dependencies
npm install <pkg>    # Install specific package
npm update           # Update dependencies
npm audit fix        # Fix security issues

# Cleanup
rm -rf node_modules  # Remove dependencies
rm -rf .next         # Clear build cache
npm cache clean --force  # Clear npm cache
```

---

**Setup Complete!** 🎉

You're now ready to start developing the frontend application.
