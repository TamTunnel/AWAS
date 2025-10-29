/**
 * AWAS Parser - Client-side JavaScript Library
 * Version 1.0.0
 * 
 * Enables AI browsers to discover and execute actions defined by AWAS
 */

class AWASParser {
    constructor(options = {}) {
        this.manifest = null;
        this.actions = new Map();
        this.options = {
            autoInit: options.autoInit !== false,
            debug: options.debug || false,
            ...options
        };

        if (this.options.autoInit) {
            this.init();
        }
    }

    /**
     * Initialize the parser by loading the AI action manifest
     */
    async init() {
        try {
            await this.loadManifest();
            this.parseManifest();
            this.parseInlineActions();
            this.log('AWAS Parser initialized successfully');
            return true;
        } catch (error) {
            console.error('Failed to initialize AWAS Parser:', error);
            return false;
        }
    }

    /**
     * Load the AI action manifest from discovery link
     */
    async loadManifest() {
        const manifestLink = document.querySelector('link[rel="ai-actions"]');
        if (!manifestLink) {
            this.log('No AI actions manifest link found');
            return;
        }

        const response = await fetch(manifestLink.href);
        if (!response.ok) {
            throw new Error(`Failed to load manifest: ${response.statusText}`);
        }

        this.manifest = await response.json();
        this.log('Manifest loaded:', this.manifest);
    }

    /**
     * Parse the manifest and register all actions
     */
    parseManifest() {
        if (!this.manifest || !this.manifest.actions) return;

        this.manifest.actions.forEach(action => {
            this.actions.set(action.id, {
                ...action,
                source: 'manifest'
            });
        });

        this.log(`Registered ${this.actions.size} actions from manifest`);
    }

    /**
     * Parse inline AI action attributes from HTML
     */
    parseInlineActions() {
        const actionElements = document.querySelectorAll('[data-ai-action]');

        actionElements.forEach(element => {
            const actionId = element.getAttribute('data-ai-action');

            // Don't override manifest actions
            if (this.actions.has(actionId)) {
                return;
            }

            const action = {
                id: actionId,
                type: element.getAttribute('data-ai-action-type') || 'unknown',
                method: element.getAttribute('data-ai-method') || 'GET',
                endpoint: element.getAttribute('data-ai-endpoint'),
                element: element,
                inputs: this.parseInputs(element),
                source: 'inline'
            };

            this.actions.set(actionId, action);
        });

        this.log(`Registered ${actionElements.length} inline actions`);
    }

    /**
     * Parse input fields for an action
     */
    parseInputs(element) {
        const inputs = [];
        const inputElements = element.querySelectorAll('[data-ai-param]');

        inputElements.forEach(input => {
            const paramConfig = {
                name: input.getAttribute('data-ai-param'),
                type: input.getAttribute('data-ai-param-type') || 'string',
                required: input.getAttribute('data-ai-param-required') === 'true',
                default: input.getAttribute('data-ai-param-default'),
                element: input
            };

            inputs.push(paramConfig);
        });

        return inputs;
    }

    /**
     * Get all available actions
     */
    getActions() {
        return Array.from(this.actions.values());
    }

    /**
     * Get a specific action by ID
     */
    getAction(actionId) {
        return this.actions.get(actionId);
    }

    /**
     * Get actions by type
     */
    getActionsByType(type) {
        return this.getActions().filter(action => action.type === type);
    }

    /**
     * Execute an action with given parameters
     */
    async executeAction(actionId, params = {}) {
        const action = this.actions.get(actionId);
        if (!action) {
            throw new Error(`Action '${actionId}' not found`);
        }

        this.log(`Executing action: ${actionId}`, params);

        // Validate required parameters
        if (action.inputs) {
            for (const input of action.inputs) {
                if (input.required && !(input.name in params)) {
                    throw new Error(`Required parameter '${input.name}' is missing`);
                }
            }
        }

        // Build request
        const endpoint = action.endpoint;
        const method = action.method.toUpperCase();

        let url = endpoint;
        let options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-AI-Agent': 'true',
                'X-AI-Agent-Name': 'AWAS-Parser/1.0'
            }
        };

        // Handle GET requests with query parameters
        if (method === 'GET') {
            const queryParams = new URLSearchParams();
            Object.entries(params).forEach(([key, value]) => {
                if (value !== null && value !== undefined) {
                    queryParams.append(key, value);
                }
            });
            url += '?' + queryParams.toString();
        } else {
            // Handle POST, PUT, PATCH, DELETE with body
            options.body = JSON.stringify(params);
        }

        // Execute request
        try {
            const response = await fetch(url, options);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(`Action failed: ${response.statusText}`);
            }

            this.log(`Action '${actionId}' completed successfully`, data);
            return data;
        } catch (error) {
            this.log(`Action '${actionId}' failed:`, error);
            throw error;
        }
    }

    /**
     * Validate action parameters
     */
    validateParams(actionId, params) {
        const action = this.getAction(actionId);
        if (!action) {
            return { valid: false, errors: [`Action '${actionId}' not found`] };
        }

        const errors = [];

        if (action.inputs) {
            action.inputs.forEach(input => {
                const value = params[input.name];

                // Check required
                if (input.required && (value === null || value === undefined)) {
                    errors.push(`Parameter '${input.name}' is required`);
                }

                // Type validation
                if (value !== null && value !== undefined) {
                    const actualType = Array.isArray(value) ? 'array' : typeof value;
                    if (input.type !== actualType && input.type !== 'any') {
                        errors.push(`Parameter '${input.name}' should be ${input.type}, got ${actualType}`);
                    }
                }

                // Validation rules
                if (input.validation && value !== null && value !== undefined) {
                    // Pattern validation
                    if (input.validation.pattern) {
                        const regex = new RegExp(input.validation.pattern);
                        if (!regex.test(value)) {
                            errors.push(`Parameter '${input.name}' does not match pattern`);
                        }
                    }

                    // Range validation
                    if (typeof value === 'number') {
                        if (input.validation.min !== undefined && value < input.validation.min) {
                            errors.push(`Parameter '${input.name}' must be >= ${input.validation.min}`);
                        }
                        if (input.validation.max !== undefined && value > input.validation.max) {
                            errors.push(`Parameter '${input.name}' must be <= ${input.validation.max}`);
                        }
                    }

                    // Enum validation
                    if (input.validation.enum && !input.validation.enum.includes(value)) {
                        errors.push(`Parameter '${input.name}' must be one of: ${input.validation.enum.join(', ')}`);
                    }
                }
            });
        }

        return {
            valid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Get capabilities of the website
     */
    async getCapabilities() {
        try {
            const capabilitiesLink = document.querySelector('link[rel="ai-capabilities"]');
            if (!capabilitiesLink) {
                return null;
            }

            const response = await fetch(capabilitiesLink.href);
            return await response.json();
        } catch (error) {
            this.log('Failed to load capabilities:', error);
            return null;
        }
    }

    /**
     * Export all actions as structured data for AI consumption
     */
    exportForAI() {
        return {
            version: this.manifest?.version || '1.0',
            name: this.manifest?.name || 'Unknown',
            description: this.manifest?.description || '',
            actions: this.getActions().map(action => ({
                id: action.id,
                type: action.type,
                name: action.name || action.id,
                description: action.description,
                method: action.method,
                endpoint: action.endpoint,
                authentication_required: action.authentication_required || false,
                inputs: action.inputs?.map(input => ({
                    name: input.name,
                    type: input.type,
                    required: input.required,
                    default: input.default,
                    validation: input.validation
                }))
            })),
            rate_limits: this.manifest?.rate_limits,
            authentication: this.manifest?.authentication
        };
    }

    /**
     * Log debug messages
     */
    log(...args) {
        if (this.options.debug) {
            console.log('[AWAS Parser]', ...args);
        }
    }
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AWASParser;
}
if (typeof window !== 'undefined') {
    window.AWASParser = AWASParser;
}

// Auto-initialize if in browser
if (typeof window !== 'undefined' && document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.awasParser = new AWASParser({ debug: true });
    });
} else if (typeof window !== 'undefined') {
    window.awasParser = new AWASParser({ debug: true });
}
