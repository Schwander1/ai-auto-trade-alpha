import { render, screen } from "@testing-library/react";
import SignalCard from "@/components/dashboard/SignalCard";
import type { Signal } from "@/types/signal";

describe("SignalCard Edge Cases", () => {
  it("handles missing optional fields", () => {
    const minimalSignal: Signal = {
      id: "1",
      symbol: "AAPL",
      action: "BUY",
      entry_price: 150.25,
      stop_loss: null,
      take_profit: null,
      confidence: 95.5,
      timestamp: new Date().toISOString(),
      hash: "",
      type: "PREMIUM",
    };

    render(<SignalCard signal={minimalSignal} />);

    expect(screen.getByText("AAPL")).toBeInTheDocument();
  });

  it("handles null exit price", () => {
    const signal: Signal = {
      id: "1",
      symbol: "AAPL",
      action: "BUY",
      entry_price: 150.25,
      stop_loss: null,
      take_profit: null,
      confidence: 95.5,
      timestamp: new Date().toISOString(),
      exit_price: null,
      outcome: null,
      pnl_pct: null,
      hash: "abc123",
      type: "PREMIUM",
    };

    render(<SignalCard signal={signal} />);

    expect(screen.getByText("AAPL")).toBeInTheDocument();
  });

  it("handles loss outcome", () => {
    const signal: Signal = {
      id: "1",
      symbol: "AAPL",
      action: "BUY",
      entry_price: 150.25,
      stop_loss: null,
      take_profit: null,
      confidence: 95.5,
      timestamp: new Date().toISOString(),
      exit_price: 145.0,
      outcome: "loss" as const,
      pnl_pct: -3.5,
      hash: "abc123",
      type: "PREMIUM",
    };

    render(<SignalCard signal={signal} />);

    expect(screen.getByText(/loss/i)).toBeInTheDocument();
    // P&L might be formatted as "-3.50%" or "-3.5%"
    const pnlText = screen.queryByText(/-3\.5/i) || screen.queryByText(/-3\.50/i);
    expect(pnlText).toBeInTheDocument();
  });

  it("handles expired outcome", () => {
    const signal: Signal = {
      id: "1",
      symbol: "AAPL",
      action: "BUY",
      entry_price: 150.25,
      stop_loss: null,
      take_profit: null,
      confidence: 95.5,
      timestamp: new Date().toISOString(),
      exit_price: 150.25,
      outcome: "expired" as const,
      pnl_pct: 0,
      hash: "abc123",
      type: "PREMIUM",
    };

    render(<SignalCard signal={signal} />);

    expect(screen.getByText(/expired/i)).toBeInTheDocument();
  });

  it("handles very high confidence scores", () => {
    const signal: Signal = {
      id: "1",
      symbol: "AAPL",
      action: "BUY",
      entry_price: 150.25,
      stop_loss: null,
      take_profit: null,
      confidence: 99.9,
      timestamp: new Date().toISOString(),
      hash: "abc123",
      type: "PREMIUM",
    };

    render(<SignalCard signal={signal} />);

    expect(screen.getByText(/99\.9%/)).toBeInTheDocument();
  });

  it("handles very low confidence scores", () => {
    const signal: Signal = {
      id: "1",
      symbol: "AAPL",
      action: "BUY",
      entry_price: 150.25,
      stop_loss: null,
      take_profit: null,
      confidence: 50.0,
      timestamp: new Date().toISOString(),
      hash: "abc123",
      type: "PREMIUM",
    };

    render(<SignalCard signal={signal} />);

    expect(screen.getByText(/50\.0%/)).toBeInTheDocument();
  });
});
