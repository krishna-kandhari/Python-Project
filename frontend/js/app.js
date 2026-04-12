document.addEventListener('DOMContentLoaded', () => {
    console.log("DefendHer App Initialized.");

    // Night Mode Logic (Auto-switch based on time)
    const checkNightMode = () => {
        const hour = new Date().getHours();
        // Enable night mode between 18:00 (6 PM) and 06:00 (6 AM)
        if (hour >= 18 || hour < 6) {
            document.body.classList.add('night-mode');
        } else {
            document.body.classList.remove('night-mode');
        }
    };

    checkNightMode();
    // Check every minute just in case
    setInterval(checkNightMode, 60000);

    // SOS Logic
    const mainSosBtn = document.getElementById('main-sos-btn');
    
    if (mainSosBtn) {
        mainSosBtn.addEventListener('click', () => {
            triggerSOS();
        });
    }

    async function triggerSOS() {
        console.log("SOS Triggered!");
        
        // Visual feedback
        const originalText = mainSosBtn.querySelector('.sos-text').innerText;
        mainSosBtn.querySelector('.sos-text').innerText = "SENDING";
        mainSosBtn.style.background = "linear-gradient(135deg, #10b981 0%, #059669 100%)";
        mainSosBtn.classList.remove('pulse-animation');

        // Fetch user location
        try {
            const position = await getCurrentPosition();
            console.log(`Location gathered: ${position.coords.latitude}, ${position.coords.longitude}`);
            
            // TODO: API Call to Backend to dispatch WhatsApp messages
            const response = await fetch('/api/sos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                    timestamp: new Date().toISOString()
                })
            });

            if (response.ok) {
                mainSosBtn.querySelector('.sos-text').innerText = "SENT";
            } else {
                throw new Error("API failed");
            }

        } catch (error) {
            console.error("SOS Failed:", error);
            mainSosBtn.querySelector('.sos-text').innerText = "FAILED";
            mainSosBtn.style.background = "linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)";
        }

        // Reset button after 5 seconds
        setTimeout(() => {
            mainSosBtn.querySelector('.sos-text').innerText = originalText;
            mainSosBtn.style.background = "linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%)";
            mainSosBtn.classList.add('pulse-animation');
        }, 5000);
    }

    function getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation is not supported by your browser'));
            } else {
                navigator.geolocation.getCurrentPosition(resolve, reject);
            }
        });
    }

    // Feature Card Listeners
    const features = {
        'feat-walk': { api: '/api/tracking/start_walk', action: "Start Walk" },
        'feat-ride': { api: '/api/tracking/start_ride', action: "Start Ride" },
        'feat-checkin': { api: '/api/checkin/set_checkin', action: "Set Check-in" },
        'feat-emergency': { localAction: () => alert("Finding Nearby Services... (Maps integration coming soon)") }
    };

    Object.keys(features).forEach(id => {
        const el = document.getElementById(id);
        if(el) {
            el.addEventListener('click', async () => {
                const feat = features[id];
                if(feat.localAction) {
                    feat.localAction();
                    return;
                }
                
                try {
                    const res = await fetch(feat.api, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ timestamp: new Date().toISOString() })
                    });
                    const data = await res.json();
                    alert(`${feat.action} Success! Session: ` + (data.session_id || data.message));
                } catch(e) {
                    alert(`Failed to trigger ${feat.action}`);
                }
            });
        }
    });

    // Health check endpoint verification
    fetch('/api/health')
        .then(res => res.json())
        .then(data => console.log('Backend connected:', data.status))
        .catch(err => console.error('Backend offline or not running on same origin', err));
});
