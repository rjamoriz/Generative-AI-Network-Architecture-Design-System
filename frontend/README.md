# Network Architecture Design System - Frontend

**Version**: 1.0.0  
**Framework**: Next.js 14 with TypeScript  
**Status**: Phase 4 - In Development

---

## 📋 Overview

Modern, responsive web interface for the Network Architecture Design System. Built with Next.js, TypeScript, and TailwindCSS for a fast, type-safe, and beautiful user experience.

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm 9+
- Backend API running at `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Run development server
npm run dev

# Open browser
open http://localhost:3000
```

---

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js 14 App Router
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   ├── designs/           # Design management pages
│   │   ├── validation/        # Validation pages
│   │   └── analytics/         # Analytics dashboard
│   ├── components/            # React components
│   │   ├── ui/               # Base UI components
│   │   ├── design/           # Design-specific components
│   │   ├── network/          # Network visualization
│   │   └── forms/            # Form components
│   ├── lib/                   # Utilities and helpers
│   │   ├── api-client.ts     # API client
│   │   ├── utils.ts          # Utility functions
│   │   └── constants.ts      # Constants
│   ├── hooks/                 # Custom React hooks
│   │   ├── useDesign.ts      # Design management
│   │   ├── useValidation.ts  # Validation hooks
│   │   └── useApi.ts         # API hooks
│   ├── types/                 # TypeScript types
│   │   ├── design.ts         # Design types
│   │   ├── validation.ts     # Validation types
│   │   └── api.ts            # API types
│   └── store/                 # State management (Zustand)
│       ├── designStore.ts    # Design state
│       └── uiStore.ts        # UI state
├── public/                    # Static assets
├── package.json
├── tsconfig.json
├── next.config.js
└── tailwind.config.ts
```

---

## 🎨 Tech Stack

### Core
- **Next.js 14** - React framework with App Router
- **TypeScript 5.3** - Type safety
- **React 18** - UI library

### Styling
- **TailwindCSS 3.4** - Utility-first CSS
- **Lucide React** - Icon library
- **clsx** - Conditional classes

### State Management
- **Zustand** - Lightweight state management
- **TanStack Query** - Server state management

### Forms & Validation
- **React Hook Form** - Form handling
- **Zod** - Schema validation

### Data Visualization
- **Recharts** - Charts and graphs
- **React Flow** - Network diagrams

### HTTP Client
- **Axios** - API requests

---

## 📡 API Integration

### API Client Setup

The frontend communicates with the backend API at `http://localhost:8000/api/v1`.

**Environment Variables:**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1
```

### API Endpoints Used

#### Design Management
- `POST /api/v1/design/analyze` - Analyze requirements
- `POST /api/v1/design/generate` - Generate design
- `GET /api/v1/design/{id}` - Get design
- `POST /api/v1/design/refine` - Refine design

#### Validation
- `POST /api/v1/validation/validate` - Validate design
- `GET /api/v1/admin/rules` - Get validation rules

#### Historical Data
- `POST /api/v1/historical/query/similar-designs` - Query similar designs
- `GET /api/v1/historical/patterns/{type}` - Get patterns

#### Metrics
- `GET /api/v1/metrics/system` - System metrics
- `GET /api/v1/metrics/application` - App metrics

---

## 🎯 Key Features

### 1. Design Wizard
Multi-step form for creating network designs:
1. Requirements input
2. AI-powered generation
3. Validation feedback
4. Refinement options

### 2. Network Visualization
Interactive network topology viewer:
- Drag-and-drop components
- Real-time connections
- Zoom and pan
- Component details

### 3. Validation Dashboard
Real-time validation feedback:
- Critical issues highlighted
- Error categorization
- Fix suggestions
- Compliance status

### 4. Historical Insights
Learn from past designs:
- Similar design search
- Pattern analysis
- Best practices
- Success metrics

### 5. Analytics
System-wide analytics:
- Design statistics
- Validation trends
- Performance metrics
- Usage analytics

---

## 🧩 Component Architecture

### Base UI Components
```typescript
// Button component
<Button variant="primary" size="lg">
  Generate Design
</Button>

// Card component
<Card>
  <CardHeader>
    <CardTitle>Network Design</CardTitle>
  </CardHeader>
  <CardContent>...</CardContent>
</Card>

// Input component
<Input
  type="text"
  placeholder="Project name"
  {...register("projectName")}
/>
```

### Design Components
```typescript
// Design card
<DesignCard
  design={design}
  onEdit={handleEdit}
  onValidate={handleValidate}
/>

// Network viewer
<NetworkViewer
  topology={design.topology}
  components={design.components}
  connections={design.connections}
/>

// Validation results
<ValidationResults
  results={validationResults}
  onFixIssue={handleFix}
/>
```

---

## 🎨 Styling Guide

### Color Scheme
```css
/* Primary colors */
--primary: 222.2 47.4% 11.2%;
--primary-foreground: 210 40% 98%;

/* Secondary colors */
--secondary: 210 40% 96.1%;
--secondary-foreground: 222.2 47.4% 11.2%;

/* Accent colors */
--accent: 210 40% 96.1%;
--accent-foreground: 222.2 47.4% 11.2%;

/* Status colors */
--success: 142 76% 36%;
--warning: 38 92% 50%;
--error: 0 84% 60%;
--info: 199 89% 48%;
```

### Typography
- **Headings**: Inter font family
- **Body**: Inter font family
- **Code**: JetBrains Mono

---

## 🔧 Development

### Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Linting
npm run lint

# Type checking
npm run type-check
```

### Code Quality

```bash
# ESLint configuration
- TypeScript support
- Next.js rules
- React hooks rules
- Accessibility rules

# TypeScript strict mode enabled
- No implicit any
- Strict null checks
- No unused variables
```

---

## 🧪 Testing (Future)

```bash
# Unit tests (Jest + React Testing Library)
npm run test

# E2E tests (Playwright)
npm run test:e2e

# Coverage report
npm run test:coverage
```

---

## 📦 Build & Deployment

### Production Build

```bash
# Build for production
npm run build

# Output: .next/ directory
# Static files: .next/static/
# Server files: .next/server/
```

### Docker Deployment

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --production
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables

**Development:**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_DEBUG=true
```

**Production:**
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_ENABLE_DEBUG=false
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

---

## 🎯 Roadmap

### Phase 4.1 - Core UI (Current)
- [x] Project setup
- [x] Configuration
- [ ] Base UI components
- [ ] Layout and navigation
- [ ] Home page

### Phase 4.2 - Design Management
- [ ] Design wizard
- [ ] Design list view
- [ ] Design detail view
- [ ] Edit functionality

### Phase 4.3 - Visualization
- [ ] Network topology viewer
- [ ] Component library
- [ ] Connection editor
- [ ] Export functionality

### Phase 4.4 - Validation
- [ ] Validation dashboard
- [ ] Real-time feedback
- [ ] Issue resolution
- [ ] Compliance reports

### Phase 4.5 - Advanced Features
- [ ] Historical insights
- [ ] Analytics dashboard
- [ ] User preferences
- [ ] Collaboration tools

---

## 🐛 Troubleshooting

### Common Issues

**API Connection Failed**
```bash
# Check backend is running
curl http://localhost:8000/health

# Verify NEXT_PUBLIC_API_URL in .env.local
```

**Build Errors**
```bash
# Clear cache and reinstall
rm -rf .next node_modules
npm install
npm run build
```

**Type Errors**
```bash
# Run type check
npm run type-check

# Update types
npm install --save-dev @types/node @types/react
```

---

## 📚 Resources

### Documentation
- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev)
- [TailwindCSS Docs](https://tailwindcss.com/docs)
- [TypeScript Docs](https://www.typescriptlang.org/docs)

### API Documentation
- Backend API: `http://localhost:8000/docs`
- API Reference: See `../backend/README.md`

---

## 🤝 Contributing

### Code Style
- Use TypeScript for all files
- Follow ESLint rules
- Use functional components
- Implement proper error handling
- Add JSDoc comments for complex functions

### Component Guidelines
- Keep components small and focused
- Use composition over inheritance
- Implement proper prop types
- Handle loading and error states
- Make components accessible (WCAG 2.1)

---

## 📄 License

Same as parent project

---

**Status**: 🚧 **In Development**  
**Next Steps**: Implement base UI components and layout  
**Backend Required**: Yes (must be running)
