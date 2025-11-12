# Alpine Analytics - Next.js Landing Page

A world-class, conversion-optimized landing page for Alpine Analytics, built with Next.js 14, TypeScript, Tailwind CSS, and Framer Motion.

## 🚀 Features

- **Next.js 14** with App Router
- **TypeScript** strict mode
- **Tailwind CSS** with custom brand colors
- **Framer Motion** for smooth animations
- **shadcn/ui** components
- **Lucide React** icons
- **Performance optimized** (<2s load time target)
- **Mobile-first** responsive design
- **SEO optimized** with proper meta tags
- **Accessibility** compliant (ARIA labels, keyboard navigation)

## 📋 Prerequisites

- Node.js 18+ 
- npm, yarn, or pnpm

## 🛠️ Installation

1. Navigate to the project directory:
```bash
cd alpine-frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

## 🏃 Development

Run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the result.

## 🏗️ Build

Create a production build:

```bash
npm run build
# or
yarn build
# or
pnpm build
```

Start the production server:

```bash
npm start
# or
yarn start
# or
pnpm start
```

## 📁 Project Structure

```
alpine-frontend/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Main landing page
│   └── globals.css         # Global styles
├── components/
│   ├── ui/                 # Reusable UI components
│   │   ├── button.tsx
│   │   └── accordion.tsx
│   ├── Header.tsx          # Sticky navigation header
│   ├── Hero.tsx            # Hero section with dashboard
│   ├── Problem.tsx         # Problem section
│   ├── Solution.tsx        # Solution with regime cards
│   ├── Proof.tsx           # Performance proof section
│   ├── Comparison.tsx      # Comparison table
│   ├── Features.tsx        # Features grid
│   ├── Pricing.tsx         # Pricing section
│   ├── SocialProof.tsx     # Testimonials
│   ├── FAQ.tsx             # FAQ accordion
│   ├── FinalCTA.tsx        # Final call-to-action
│   └── Footer.tsx          # Footer
├── hooks/
│   └── useIntersectionObserver.ts  # Lazy loading hook
├── lib/
│   └── utils.ts            # Utility functions
└── public/                 # Static assets
```

## 🎨 Brand Colors

- **Navy**: `#0A1628` - Primary background, trust
- **Blue**: `#0066FF` - Primary action, innovation
- **Green**: `#10B981` - Success, profit
- **Red**: `#EF4444` - Alerts, stop-loss
- **Gray**: `#F3F4F6` - Text, backgrounds

## 🎯 Key Sections

1. **Header** - Sticky navigation with transparent-to-solid scroll effect
2. **Hero** - Full viewport section with animated dashboard mockup
3. **Problem** - Why 95% of trading signal services fail
4. **Solution** - Four regime-specific strategies
5. **Proof** - 20-year battle-tested performance
6. **Comparison** - Alpine vs competitors table
7. **Features** - 9 key features grid
8. **Pricing** - Three pricing tiers with annual savings
9. **Social Proof** - Customer testimonials
10. **FAQ** - 8 frequently asked questions
11. **Final CTA** - Conversion-optimized call-to-action
12. **Footer** - Links and legal information

## ⚡ Performance Optimizations

- Lazy loading with Intersection Observer
- Image optimization with next/image
- Font preloading (Inter from Google Fonts)
- Code splitting and tree shaking
- Optimized animations (60fps target)
- Minimal bundle size (<200KB gzipped target)

## 📱 Mobile Optimization

- Responsive design (mobile-first)
- Hamburger menu for navigation
- Touch-friendly buttons and interactions
- Optimized images for mobile
- Full-width CTAs on mobile

## 🔍 SEO Features

- Semantic HTML structure
- Proper meta tags
- Open Graph tags
- Twitter Card support
- Structured data ready

## 🚀 Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import the repository in Vercel
3. Vercel will automatically detect Next.js and deploy

### Other Platforms

The app can be deployed to any platform that supports Next.js:
- Netlify
- AWS Amplify
- Railway
- DigitalOcean App Platform

## 📝 Environment Variables

Currently, no environment variables are required. Add them as needed for:
- API endpoints
- Analytics IDs
- Feature flags

## 🧪 Testing

Run the linter:

```bash
npm run lint
```

## 📄 License

Copyright © 2025 Alpine Analytics. All rights reserved.

## 🆘 Support

For issues or questions, please contact the development team.

---

**Built with ❤️ for Alpine Analytics**

