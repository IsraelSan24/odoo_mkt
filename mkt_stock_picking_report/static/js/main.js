document.addEventListener('DOMContentLoaded', function() {
    const checks = {
        'check-store-transfer': o.mt_store_transfer,
        'check-return': o.mt_return,
        'check-incoming': o.mt_incoming,
        'check-storage-output': o.mt_storage_output,
        'check-other': o.mt_other
    };
    
    Object.keys(checks).forEach(function(id) {
        const element = document.getElementById(id);
        if (element && checks[id]) {
            element.innerHTML = '&#10003;';
        }
    });
});