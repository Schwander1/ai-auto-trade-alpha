// ARGO Capital Dashboard WebSocket Client
// Real-Time Trading Data Integration with Streamlit
const WebSocket = require('ws');

class ArgoDashboardClient {
    constructor() {
        this.ws = null;
        this.reconnectInterval = 5000;
        this.connect();
    }
    
    connect() {
        console.log('🔗 ARGO: Connecting to trading data stream...');
        this.ws = new WebSocket('ws://localhost:8580');
        
        this.ws.on('open', () => {
            console.log('✅ ARGO: Dashboard WebSocket connected');
            this.requestPortfolioUpdate();
        });
        
        this.ws.on('message', (data) => {
            try {
                const message = JSON.parse(data);
                this.handleTradingData(message);
            } catch (error) {
                console.error('❌ Data parsing error:', error);
            }
        });
        
        this.ws.on('close', () => {
            console.log('📤 ARGO: Connection lost, reconnecting...');
            setTimeout(() => this.connect(), this.reconnectInterval);
        });
        
        this.ws.on('error', (error) => {
            console.error('❌ WebSocket error:', error);
        });
    }
    
    handleTradingData(message) {
        switch (message.type) {
            case 'portfolio_update':
                console.log('💰 Portfolio Update:', message.data);
                // Integration point for Streamlit dashboard updates
                break;
            case 'new_signal':
                console.log('📊 New Signal:', message.data);
                break;
            case 'order_executed':
                console.log('🚀 Order Update:', message.data);
                break;
            default:
                console.log('📨 Message:', message);
        }
    }
    
    requestPortfolioUpdate() {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'request_portfolio_update',
                timestamp: new Date().toISOString()
            }));
        }
    }
}

// Start ARGO Dashboard Client
console.log('🚀 ARGO Capital Dashboard Client Starting...');
const client = new ArgoDashboardClient();

// Keep the process running
process.on('SIGINT', () => {
    console.log('\n📤 ARGO Dashboard Client shutting down...');
    process.exit(0);
});
