// Main application JavaScript
class CryptoApp {
    constructor() {
        this.currentPrices = [];
        this.init();
    }
    
    init() {
        this.loadPrices();
        // Refresh every 30 seconds
        setInterval(() => this.loadPrices(), 30000);
    }
    
    async loadPrices() {
        try {
            const response = await fetch('/api/prices');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            if (!data || !Array.isArray(data.prices)) {
                throw new Error('Unexpected /api/prices response');
            }

            this.updateLastUpdateTime();
            this.renderPrices(data.prices);
            
            // Load charts for each coin
            this.loadAllCharts(data.prices);
            
        } catch (error) {
            console.error('Error loading prices:', error);
            this.showError('Failed to load prices. Please refresh the page.');
        }
    }
    
    updateLastUpdateTime() {
        document.getElementById('lastUpdate').textContent = 
            `Last update: ${new Date().toLocaleTimeString()}`;
    }
    
    renderPrices(prices) {
        let html = '';
        
        prices.forEach(coin => {
            // defensive access for change value (support either key)
            const rawChange = coin['24h_change'] ?? coin.price_change_24h ?? 0;
            const change = Number(rawChange) || 0;
            const changeClass = change >= 0 ? 'positive' : 'negative';
            const changeSymbol = change >= 0 ? '↗' : '↘';
            const changeText = (change >= 0 ? `+${change.toFixed(2)}%` : `${change.toFixed(2)}%`);
            
            const lastUpdated = coin.last_updated ? new Date(coin.last_updated).toLocaleTimeString() : '—';
            const priceVal = (typeof coin.price_usd === 'number') ? coin.price_usd : Number(coin.price_usd) || 0;
            
            html += `
                <div class="coin-card">
                    <div class="coin-header">
                        <div class="coin-symbol">${coin.symbol}</div>
                        <div class="${changeClass}">
                            ${changeSymbol} ${changeText}
                        </div>
                    </div>
                    <div class="coin-price">
                        $${this.formatPrice(priceVal)}
                    </div>
                    <div class="chart-container">
                        <canvas id="chart-${coin.symbol}"></canvas>
                    </div>
                    <div class="last-updated">
                        Updated: ${lastUpdated}
                    </div>
                </div>
            `;
        });
        
        document.getElementById('coinsGrid').innerHTML = html;
    }
    
    formatPrice(price) {
        if (price >= 1) {
            return price.toLocaleString('en-US', { 
                minimumFractionDigits: 2, 
                maximumFractionDigits: 2 
            });
        } else {
            return price.toLocaleString('en-US', { 
                minimumFractionDigits: 2, 
                maximumFractionDigits: 6 
            });
        }
    }
    
    async loadAllCharts(prices) {
        for (const coin of prices) {
            await this.loadChart(coin.symbol);
        }
    }
    
    async loadChart(symbol) {
        try {
            const response = await fetch(`/api/history/${symbol}`);
            const data = await response.json();
            
            if (data.history.length > 0) {
                this.createChart(symbol, data.history);
            }
        } catch (error) {
            console.error(`Error loading chart for ${symbol}:`, error);
        }
    }
    
    createChart(symbol, history) {
        const ctx = document.getElementById(`chart-${symbol}`)?.getContext('2d');
        if (!ctx) return;
        
        const prices = history.map(h => h.price);
        const timestamps = history.map(h => 
            new Date(h.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
        );
        
        // Calculate min and max for proper scaling
        const minPrice = Math.min(...prices);
        const maxPrice = Math.max(...prices);
        const padding = (maxPrice - minPrice) * 0.1;
        
        // Destroy existing chart if it exists
        if (ctx.chart) {
            ctx.chart.destroy();
        }
        
        ctx.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: symbol,
                    data: prices,
                    borderColor: prices[prices.length - 1] >= prices[0] ? '#27ae60' : '#e74c3c',
                    backgroundColor: prices[prices.length - 1] >= prices[0] ? 
                        'rgba(39, 174, 96, 0.1)' : 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return `$${context.parsed.y.toFixed(4)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: { 
                        display: false 
                    },
                    y: { 
                        display: false,
                        min: minPrice - padding,
                        max: maxPrice + padding
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'nearest'
                }
            }
        });
    }
    
    showError(message) {
        const coinsGrid = document.getElementById('coinsGrid');
        coinsGrid.innerHTML = `<div class="error">${message}</div>`;
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new CryptoApp();
});