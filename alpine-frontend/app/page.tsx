import Navigation from '@/components/Navigation'
import Hero from '@/components/Hero'
import TrustIndicator from '@/components/TrustIndicator'
import HonestDisclosure from '@/components/HonestDisclosure'
import TheProof from '@/components/TheProof'
import CompetitorComparison from '@/components/CompetitorComparison'
import CSVPreview from '@/components/CSVPreview'
import VerificationSection from '@/components/VerificationSection'
import EquityCurveChart from '@/components/EquityCurveChart'
import RegimeCards from '@/components/RegimeCards'
import ContinuousImprovement from '@/components/ContinuousImprovement'
import SymbolTable from '@/components/SymbolTable'
import RiskDisclosure from '@/components/RiskDisclosure'
import Pricing from '@/components/Pricing'
import FAQ from '@/components/FAQ'
import Footer from '@/components/Footer'

export default function Home() {
  return (
    <main className="min-h-screen bg-alpine-darker">
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
