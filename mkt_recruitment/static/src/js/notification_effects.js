/** @odoo-module **/
import { registry } from '@web/core/registry';

// 1) Register the function
registry.category('effects').add('custom_notification_animation', function(env, params = {}) {
    // Create container
    const container = document.createElement('div');
    container.classList.add('my-notif');     // animation SCSS

    // Define level parameter
    const level = params.level || 'info';
    container.classList.add(level)
    container.textContent = params.message || '';
    document.body.appendChild(container);

    // Remove the element after the fade
    const delays = { fast: 1000, medium: 2000, slow: 3000 };
    const timeout = delays[params.fadeout] || 1500;
    setTimeout(() => container.remove(), timeout);
});