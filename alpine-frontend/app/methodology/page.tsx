export default function MethodologyPage() {
  return (
    <div className="min-h-screen bg-alpine-black-primary text-alpine-text-primary ">
      <div className="container mx-auto px-6 py-20 max-w-4xl">
        <h1 className="text-4xl font-display font-bold mb-8 text-alpine-semantic-success">Methodology</h1>
        <p className="text-xl text-alpine-text-secondary mb-12">
          Understanding the math and strategy behind Alpine Analytics
        </p>

        <div className="space-y-12 text-alpine-text-secondary">
          <section>
            <h2 className="text-3xl font-display font-bold text-alpine-text-primary mb-6">Multi-Regime Adaptive Framework</h2>
            <p className="mb-4">
              Unlike traditional trading systems that use a single strategy, Alpine Analytics adapts to changing market conditions in real-time.
            </p>
            <p>
              Our proprietary regime detection system analyzes market conditions every 15 minutes and automatically switches between four distinct trading strategies.
            </p>
          </section>

          <section>
            <h2 className="text-3xl font-display font-bold text-alpine-text-primary mb-6">The Four Regimes</h2>

            <div className="space-y-6">
              <div className="p-6 bg-alpine-black-secondary border border-alpine-black-border rounded-lg">
                <h3 className="text-xl font-display font-bold text-alpine-semantic-success mb-3">📈 Bull Regime</h3>
                <p className="mb-2"><strong>Strategy:</strong> Trend-following with momentum</p>
                <p className="mb-2"><strong>Detection:</strong> Price &gt; 200 SMA, Low volatility (ATR &lt; 3%)</p>
                <p><strong>Historical Win Rate:</strong> 66%</p>
              </div>

              <div className="p-6 bg-alpine-black-secondary border border-alpine-black-border rounded-lg">
                <h3 className="text-xl font-display font-bold text-alpine-semantic-error mb-3">📉 Bear Regime</h3>
                <p className="mb-2"><strong>Strategy:</strong> Counter-trend mean reversion</p>
                <p className="mb-2"><strong>Detection:</strong> Price &lt; 200 SMA, Declining momentum</p>
                <p><strong>Historical Win Rate:</strong> 55%</p>
              </div>

              <div className="p-6 bg-alpine-black-secondary border border-alpine-black-border rounded-lg">
                <h3 className="text-xl font-display font-bold text-alpine-orange mb-3">🔀 Chop Regime</h3>
                <p className="mb-2"><strong>Strategy:</strong> Range-bound mean reversion</p>
                <p className="mb-2"><strong>Detection:</strong> Price oscillating around 200 SMA, Normal volatility</p>
                <p><strong>Historical Win Rate:</strong> 56%</p>
              </div>

              <div className="p-6 bg-alpine-black-secondary border border-alpine-black-border rounded-lg">
                <h3 className="text-xl font-display font-bold text-alpine-neon-purple mb-3">⚡ Crisis Regime</h3>
                <p className="mb-2"><strong>Strategy:</strong> Volatility-based opportunities</p>
                <p className="mb-2"><strong>Detection:</strong> ATR &gt; 5%, VIX &gt; 30, Extreme volatility</p>
                <p><strong>Historical Win Rate:</strong> 57%</p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-3xl font-display font-bold text-alpine-text-primary mb-6">SHA-256 Cryptographic Verification</h2>
            <p className="mb-4">
              Every signal is cryptographically signed using SHA-256 hashing at the moment of generation. This creates an immutable record that cannot be altered retroactively.
            </p>
            <p className="mb-4">
              <strong className="text-alpine-semantic-success">Patent Pending:</strong> Our SHA-256 cryptographic verification system for trading signals is protected under pending U.S. patent application.
            </p>
            <p className="text-alpine-text-secondary text-sm">
              Note: Institutional clients receive full methodology disclosure under NDA.
            </p>
          </section>

          <section>
            <h2 className="text-3xl font-display font-bold text-alpine-text-primary mb-6">Position Sizing: Kelly Criterion</h2>
            <p className="mb-4">
              We use the Kelly Criterion for optimal position sizing, maximizing long-term capital growth while managing risk.
            </p>
            <p>
              Position sizes are dynamically adjusted based on win probability, reward-to-risk ratio, and current market regime.
            </p>
          </section>

          <section className="mt-12">
            <h2 className="text-3xl font-display font-bold text-alpine-text-primary mb-6">Continuous Evolution</h2>

            <p className="text-alpine-text-secondary mb-4">
              Unlike traditional trading systems that remain static for months or years, Alpine Analytics
              operates under a philosophy of <strong className="text-alpine-semantic-success">continuous improvement</strong>.
            </p>

            <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-6 mb-6">
              <h3 className="text-xl font-display font-bold text-alpine-text-primary mb-3">Our Iteration Cycle</h3>
              <ul className="space-y-3 text-alpine-text-secondary">
                <li className="flex items-start gap-2">
                  <span className="text-alpine-semantic-success font-bold">•</span>
                  <span><strong>Weekly Analysis:</strong> Review all signals from past 7 days. Identify patterns, edge cases, improvement opportunities.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-alpine-semantic-success font-bold">•</span>
                  <span><strong>Hypothesis Formation:</strong> Propose specific changes (new indicator, adjusted threshold, regime refinement).</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-alpine-semantic-success font-bold">•</span>
                  <span><strong>Backtest Validation:</strong> Test proposed changes on recent historical data to verify improvement.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-alpine-semantic-success font-bold">•</span>
                  <span><strong>Live Deployment:</strong> Ship as new strategy version (e.g., v1.5 → v1.6). All signals tagged with version number.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-alpine-semantic-success font-bold">•</span>
                  <span><strong>Comparative Analysis:</strong> Track new version vs previous. If improvement confirmed, keep it. If not, revert.</span>
                </li>
              </ul>
            </div>

            <p className="text-alpine-text-secondary mb-4">
              Every strategy version is <strong className="text-alpine-semantic-success">cryptographically verified</strong>.
              You can download complete trade history and filter by version to see evolution over time.
            </p>

            <div className="bg-alpine-black-primary border border-alpine-black-border rounded-lg p-6">
              <p className="text-alpine-text-primary font-semibold mb-2">Example Evolution:</p>
              <ul className="space-y-2 text-sm text-alpine-text-secondary font-mono">
                <li>v1.0 (Nov 2025): Launch | 54.2% win rate</li>
                <li>v1.1 (Nov 2025): Improved crisis regime detection | 56.1% win rate</li>
                <li>v1.2 (Dec 2025): Added volume confirmation | 57.8% win rate</li>
                <li>v2.0 (Jan 2026): Machine learning regime classifier | 61.3% win rate</li>
              </ul>
              <p className="text-alpine-text-secondary text-smmt-4">
                All versions verified. All performance provable. No retroactive changes possible.
              </p>
            </div>
          </section>

          <section className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-8">
            <h2 className="text-2xl font-display font-bold text-alpine-text-primary mb-4">Want More Details?</h2>
            <p className="mb-6 text-alpine-text-secondary">
              Institutional clients receive complete methodology documentation under NDA, including exact indicator specifications, threshold values, and signal generation algorithms.
            </p>
            <a
              href="mailto:alpine.signals@proton.me"
              className="inline-flex items-center gap-2 px-6 py-3 bg-alpine-semantic-success hover:bg-alpine-green-dark text-alpine-black-primary font-bold rounded-lg transition-colors"
            >
              Contact for Institutional Access
            </a>
          </section>
        </div>

        <div className="mt-12">
          <a href="/" className="text-alpine-semantic-success hover:underline">← Back to Home</a>
        </div>
      </div>
    </div>
  )
}

