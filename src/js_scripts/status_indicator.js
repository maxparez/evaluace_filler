/**
 * Visual Status Indicator System
 * Provides colored status bar at top of page during automation
 */

window.AutomationStatusIndicator = {
    // Status bar element reference
    statusBar: null,

    // Current status
    currentStatus: 'inactive',

    // Status configurations
    statusConfig: {
        'running': {
            color: '#4CAF50',
            backgroundColor: '#E8F5E8',
            borderColor: '#4CAF50',
            text: '🤖 Probíhá automatické vyplňování...',
            icon: '✅'
        },
        'processing': {
            color: '#2196F3',
            backgroundColor: '#E3F2FD',
            borderColor: '#2196F3',
            text: '⚡ Zpracovávám stránku...',
            icon: '⚡'
        },
        'waiting': {
            color: '#FF9800',
            backgroundColor: '#FFF3E0',
            borderColor: '#FF9800',
            text: '⏳ Čekám na načtení stránky...',
            icon: '⏳'
        },
        'manual_required': {
            color: '#F44336',
            backgroundColor: '#FFEBEE',
            borderColor: '#F44336',
            text: '⚠️ Požadován manuální zásah - zkontrolujte stránku',
            icon: '🔴'
        },
        'error': {
            color: '#F44336',
            backgroundColor: '#FFEBEE',
            borderColor: '#F44336',
            text: '❌ Chyba při automatickém vyplňování',
            icon: '❌'
        },
        'completed': {
            color: '#4CAF50',
            backgroundColor: '#E8F5E8',
            borderColor: '#4CAF50',
            text: '🎉 Automatické vyplňování dokončeno úspěšně!',
            icon: '🎉'
        },
        'inactive': {
            color: '#9E9E9E',
            backgroundColor: '#F5F5F5',
            borderColor: '#9E9E9E',
            text: '⏹️ Automatické vyplňování neaktivní',
            icon: '⏹️'
        }
    },

    /**
     * Initialize the status indicator system
     */
    init: function() {
        console.log('🎯 Initializing Automation Status Indicator...');

        // Remove existing status bar if present
        this.remove();

        // Create new status bar
        this.create();

        // Set initial status
        this.setStatus('inactive');

        console.log('✅ Status Indicator initialized successfully');
        return true;
    },

    /**
     * Create the status bar element
     */
    create: function() {
        // Create status bar container
        this.statusBar = document.createElement('div');
        this.statusBar.id = 'automation-status-bar';
        this.statusBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 999999;
            padding: 12px 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 14px;
            font-weight: 600;
            text-align: center;
            border-bottom: 3px solid;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: all 0.3s ease-in-out;
            transform: translateY(-100%);
            animation: slideDown 0.5s ease-out forwards;
        `;

        // Create text content
        const textSpan = document.createElement('span');
        textSpan.id = 'status-text';
        this.statusBar.appendChild(textSpan);

        // Create close button (hidden by default)
        const closeButton = document.createElement('button');
        closeButton.innerHTML = '✕';
        closeButton.id = 'status-close-btn';
        closeButton.style.cssText = `
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            font-size: 16px;
            cursor: pointer;
            opacity: 0.7;
            padding: 0;
            width: 20px;
            height: 20px;
            display: none;
        `;
        closeButton.onclick = () => this.hide();
        this.statusBar.appendChild(closeButton);

        // Add CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideDown {
                from { transform: translateY(-100%); }
                to { transform: translateY(0); }
            }
            @keyframes slideUp {
                from { transform: translateY(0); }
                to { transform: translateY(-100%); }
            }
            #automation-status-bar.slide-up {
                animation: slideUp 0.5s ease-in-out forwards;
            }
            #automation-status-bar:hover #status-close-btn {
                display: block !important;
            }
        `;

        if (!document.getElementById('status-bar-styles')) {
            style.id = 'status-bar-styles';
            document.head.appendChild(style);
        }

        // Insert at the very beginning of body
        if (document.body) {
            document.body.insertBefore(this.statusBar, document.body.firstChild);
        } else {
            // If body not ready, wait for it
            document.addEventListener('DOMContentLoaded', () => {
                document.body.insertBefore(this.statusBar, document.body.firstChild);
            });
        }
    },

    /**
     * Set the status of the indicator
     * @param {string} status - Status key from statusConfig
     * @param {string} customText - Optional custom text override
     */
    setStatus: function(status, customText) {
        if (!this.statusBar) {
            console.warn('Status bar not initialized, initializing now...');
            this.init();
        }

        const config = this.statusConfig[status];
        if (!config) {
            console.error(`Unknown status: ${status}`);
            return false;
        }

        this.currentStatus = status;

        // Update visual appearance
        this.statusBar.style.color = config.color;
        this.statusBar.style.backgroundColor = config.backgroundColor;
        this.statusBar.style.borderBottomColor = config.borderColor;

        // Update text content
        const textElement = this.statusBar.querySelector('#status-text');
        if (textElement) {
            textElement.textContent = customText || config.text;
        }

        // Show the status bar if hidden
        this.show();

        // Auto-hide completed status after delay
        if (status === 'completed') {
            setTimeout(() => {
                this.hide();
            }, 5000);
        }

        console.log(`🎯 Status updated to: ${status} - ${customText || config.text}`);
        return true;
    },

    /**
     * Show the status bar
     */
    show: function() {
        if (this.statusBar) {
            this.statusBar.style.display = 'block';
            this.statusBar.classList.remove('slide-up');
        }
    },

    /**
     * Hide the status bar with animation
     */
    hide: function() {
        if (this.statusBar) {
            this.statusBar.classList.add('slide-up');
            setTimeout(() => {
                if (this.statusBar) {
                    this.statusBar.style.display = 'none';
                }
            }, 500);
        }
    },

    /**
     * Remove the status bar completely
     */
    remove: function() {
        const existingBar = document.getElementById('automation-status-bar');
        if (existingBar) {
            existingBar.remove();
        }

        const existingStyles = document.getElementById('status-bar-styles');
        if (existingStyles) {
            existingStyles.remove();
        }

        this.statusBar = null;
    },

    /**
     * Update status with progress information
     * @param {string} status - Status key
     * @param {number} current - Current step/page
     * @param {number} total - Total steps/pages (optional)
     * @param {string} action - Current action description
     */
    setStatusWithProgress: function(status, current, total, action) {
        let progressText = `Stránka ${current}`;
        if (total && total > 0) {
            progressText += `/${total}`;
        }

        if (action) {
            progressText += ` - ${action}`;
        }

        const baseText = this.statusConfig[status]?.text || 'Probíhá automatizace...';
        const fullText = `${baseText} (${progressText})`;

        this.setStatus(status, fullText);
    },

    /**
     * Set manual intervention required status with specific reason
     * @param {string} reason - Reason for manual intervention
     * @param {string} suggestion - Suggested action
     */
    setManualRequired: function(reason, suggestion) {
        const text = `⚠️ Manuální zásah: ${reason}${suggestion ? ' - ' + suggestion : ''}`;
        this.setStatus('manual_required', text);

        // Show close button for manual interventions
        const closeBtn = this.statusBar?.querySelector('#status-close-btn');
        if (closeBtn) {
            closeBtn.style.display = 'block';
        }
    },

    /**
     * Get current status
     */
    getStatus: function() {
        return this.currentStatus;
    },

    /**
     * Check if status bar is visible
     */
    isVisible: function() {
        return this.statusBar && this.statusBar.style.display !== 'none';
    }
};

// Auto-initialize when script loads
console.log('📜 Status Indicator script loaded');

// Export for external access
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.AutomationStatusIndicator;
}