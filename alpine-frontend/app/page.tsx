import Navigation from '@/components/Navigation'
import Hero from '@/components/Hero'
import TrustIndicator from '@/components/TrustIndicator'
import dynamic from 'next/dynamic'

// Lazy load heavy components that are below the fold
const HonestDisclosure = dynamic(() => import('@/components/HonestDisclosure'), {
  loading: () => <div className="h-64 animate-pulse bg-alpine-blackseconda-ry" />,
  ssr: true  // Still render on server for SEO
})

const TheProof = dynamic(() => import('@/components/TheProof'), {
  loading: () => <div className="h-96 animate-pulse bg-alpine-blackseconda-ry" />,
  ssr: true
})

const CompetitorComparison = dynamic(() => import('@/components/CompetitorComparison'), {
  loading: () => <div className="h-64 animate-pulse bg-alpine-blackseconda-ry" />,
  ssr: true
})

const CSVPreview = dynamic(() => import('@/components/CSVPreview'), {
  loading: () => <div className="h-96 animate-pulse bg-alpine-blackseconda-ry" />,
  ssr: true
})

const VerificationSection = dynamic(() => import('@/components/VerificationSection'), {
  loading: () => <div className="h-64 animate-pulse bg-alpine-blackseconda-ry" />,
  ssr: true
})

// Heavy chart component - lazy load with no SSR (charts need browser APIs)
const EquityCurveChart = dynamic(() => import('@/components/EquityCurveChart'), {
  loading: () => <div className="h-96 animate-pulse bg-alpine-blackseconda-ry" />,
  ssr: false  // Charts require browser APIs
})

const RegimeCards = dynamic(() => import('@/components/RegimeCards'), {
  loading: () => <div className="h-64 animate-pulse bg-alpine-blackseconda-ry" />,
  ssr: true
})

const ContinuousImprovement = dynamic(() => import('@/components/ContinuousImprovement'), {
  loading: () => <div className="h-64 animate-pulse bg-alpine-blackseconda-ry" />,
  ssr: true
})

// Large table component - lazy load
const SymbolTable = dynamic(() => import('@/components/SymbolTable'), {
  loading: () => <div className="h-96 animate-pulse bg-alpine-blackseconda-ry" />,
  ssr: true
})

const RiskDisclosure = dynamic(() => import('@/components/RiskDisclosure'), {
  loading: () => <div className="h-48 animate-pulse bg-alpine-blackseconda-ry" />,
  ssr: true
})

const Pricing = dynamic(() => import('@/components/Pricing'), {
  loading: () => <div className="h-96 animate-pulse bg-alpine-blackseconda-ry" />,
  ssr: true
})

const FAQ = dynamic(() => import('@/components/FAQ'), {
  loading: () => <div className="h-64 animate-pulse bg-alpine-blackseconda-ry" />,
  ssr: true
})

import Footer from '@/components/Footer'  // Keep Footer static (small, always needed)

export default function Home() {
  return (
    <main id="main-content" className="min-h-screen bg-alpine-blackprima-ry">
      <Navigation />
      <Hero />
      <TrustIndicator />
      <HonestDisclosure />
      <TheProof />
      <CompetitorComparison />
      <CSVPreview />
      <VerificationSection />
      <EquityCurveChart />
      <RegimeCards />
      <ContinuousImprovement />
      <SymbolTable />
      <RiskDisclosure />
      <Pricing />
      <FAQ />
      <Footer />
    </main>
  )
}
