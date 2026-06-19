const cityInput = document.getElementById('city');
const cropInput = document.getElementById('crop');
const seasonInput = document.getElementById('season');
const voiceAllBtn = document.getElementById('voice-all-btn');
const voiceStatus = document.getElementById('voice-status');
const speechOutput = document.getElementById('speech-output');
const form = document.querySelector('form');

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const speechSynthesisSupported = 'speechSynthesis' in window;

function speak(text) {
    // TTS disabled: update visible text and status only
    if (!text) return;
    updateStatus(text);
    const speechTextEl = document.getElementById('speech-text');
    if (speechTextEl) {
        speechTextEl.textContent = text;
        speechTextEl.style.display = '';
    }
}

function updateStatus(message) {
    if (voiceStatus) voiceStatus.textContent = message;
}

function parseCombinedTranscript(transcript) {
    if (!transcript) return {};
    const original = transcript.trim();
    const normalized = original.replace(/\bseason\b/gi, 'season').replace(/\blocation\b/gi, 'city');
    const fields = { city: null, crop: null, season: null };
    const regex = /\b(city|crop|season)\b\s*[:\-]?\s*/gi;
    let match;
    let lastKey = null;
    let lastIndex = 0;

    while ((match = regex.exec(normalized)) !== null) {
        if (lastKey) {
            fields[lastKey] = normalized.substring(lastIndex, match.index).trim().replace(/^[,:\-\s]+|[,:\-\s]+$/g, '');
        }
        lastKey = match[1].toLowerCase();
        lastIndex = regex.lastIndex;
    }

    if (lastKey) {
        fields[lastKey] = normalized.substring(lastIndex).trim().replace(/^[,:\-\s]+|[,:\-\s]+$/g, '');
    }

    // If city keyword is missing but there is text before the first keyword, use that as city.
    const firstKeywordMatch = /\b(city|crop|season)\b/i.exec(normalized);
    if (!fields.city && firstKeywordMatch && firstKeywordMatch.index > 0) {
        fields.city = normalized.substring(0, firstKeywordMatch.index).trim().replace(/^[,:\-\s]+|[,:\-\s]+$/g, '');
    }

    return {
        city: fields.city || null,
        crop: fields.crop || null,
        season: fields.season || null
    };
}

function startSingleRecognition(prompt) {
    if (!SpeechRecognition) {
        updateStatus('Voice input not supported in this browser.');
        return;
    }

    const recognition = new SpeechRecognition();
    // set recognition language based on page lang attribute if present
    const pageLang = document.documentElement.lang || (document.body.dataset && document.body.dataset.lang) || 'en';
    const recogMap = { 'en': 'en-US', 'hi': 'hi-IN', 'te': 'te-IN' };
    recognition.lang = recogMap[pageLang] || 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    updateStatus(prompt || 'Listening for location, crop, and season in one sentence.');
    recognition.start();

    recognition.addEventListener('result', (event) => {
        const transcript = event.results[0][0].transcript;
        updateStatus(`Recognized: ${transcript}`);

        const parsed = parseCombinedTranscript(transcript);
        if (parsed.city) cityInput.value = parsed.city;
        if (parsed.crop) cropInput.value = parsed.crop;
        if (parsed.season) seasonInput.value = parsed.season;
        // update visible summary immediately so user can read inputs
        try { readAllInputs(); } catch (e) {}

        // Use localized confirm text from the button if available
        let confirmTemplate = prompt || null;
        try {
            const btn = document.getElementById('voice-all-btn');
            if (btn && btn.dataset && btn.dataset.confirmText) {
                confirmTemplate = btn.dataset.confirmText;
            }
        } catch (e) {}

        const confirmText = (confirmTemplate || `Captured. Location: {city}, Crop: {crop}. Submitting now.`)
            .replace('{city}', parsed.city || 'unknown')
            .replace('{crop}', parsed.crop || 'unknown');

        // show confirmation text only (no TTS)
        updateStatus(confirmText);
        const speechTextEl = document.getElementById('speech-text');
        if (speechTextEl) { speechTextEl.textContent = confirmText; speechTextEl.style.display = ''; }

        // submit automatically after voice input if form is valid.
        if (form && form.checkValidity()) {
            setTimeout(() => {
                if (form && form.checkValidity()) {
                    form.submit();
                }
            }, 700);
        }
    });

    recognition.addEventListener('speechend', () => {
        recognition.stop();
    });

    recognition.addEventListener('end', () => {
        updateStatus('Voice input complete.');
    });

    recognition.addEventListener('error', (event) => {
        updateStatus(`Voice error: ${event.error}`);
    });
}

// Attach the single-utterance handler to the single mic button
if (voiceAllBtn) {
    voiceAllBtn.addEventListener('click', () => {
        const prompt = (voiceAllBtn.dataset && voiceAllBtn.dataset.listenPrompt) || 'Listening for location, crop, and season in one sentence.';
        startSingleRecognition(prompt);
    });
}

// Read-all button: speak a localized summary of the inputs
const readAllBtn = document.getElementById('read-all-btn');
function readAllInputs() {
    if (!readAllBtn) return;
    const template = readAllBtn.dataset.summaryTemplate || 'Summary — City: {city}. Crop: {crop}. Season: {season}.';
    const city = cityInput ? (cityInput.value || 'unknown') : 'unknown';
    const crop = cropInput ? (cropInput.value || 'unknown') : 'unknown';
    const seasonVal = seasonInput ? (seasonInput.value || 'unknown') : 'unknown';
    const summary = template.replace('{city}', city).replace('{crop}', crop).replace('{season}', seasonVal);
    // display summary text
    const summaryEl = document.getElementById('summary-text');
    if (summaryEl) { summaryEl.textContent = summary; summaryEl.style.display = ''; }
    updateStatus(summary);

    // speak the summary using TTS (best-effort for page language)
    try { speakTTS(`city ${city}, crop ${crop}, season ${seasonVal}`); } catch (e) { console.warn('TTS failed', e); }
}

if (readAllBtn) {
    readAllBtn.addEventListener('click', readAllInputs);
}

// --- TTS helper (best-effort, used only for Read All) ---
function getAvailableVoices() {
    if (!speechSynthesisSupported) return [];
    return window.speechSynthesis.getVoices() || [];
}

function getBestVoiceForLang(pageLang) {
    const voices = getAvailableVoices();
    if (!voices.length) return null;
    // prefer Indian voices (te-IN, hi-IN) strongly; then page lang, then Telugu, then fallback
    const lowers = pageLang.toLowerCase();
    // Prefer exact Indian variants first
    let v = voices.find(x => x.lang && (x.lang.toLowerCase() === 'te-in' || x.lang.toLowerCase() === 'hi-in'));
    if (v) return v;
    // Then prefer page lang
    v = voices.find(x => x.lang && x.lang.toLowerCase().startsWith(lowers));
    if (v) return v;
    // For Telugu, also check by name
    if (pageLang === 'te') {
        v = voices.find(x => x.name && x.name.toLowerCase().includes('telugu'));
        if (v) return v;
    }
    // Fallback to Hindi
    v = voices.find(x => x.lang && x.lang.toLowerCase().startsWith('hi'));
    if (v) return v;
    // Generic English
    v = voices.find(x => x.lang && x.lang.toLowerCase().startsWith('en'));
    return v || voices[0];
}

function speakTTS(text) {
    if (!speechSynthesisSupported || !text) return;
    const utterance = new SpeechSynthesisUtterance(text);
    const pageLang = document.documentElement.lang || (document.body.dataset && document.body.dataset.lang) || 'en';
    const langMap = { 'en': 'en-US', 'hi': 'hi-IN', 'te': 'te-IN' };
    utterance.lang = langMap[pageLang] || 'en-US';
    // select best available voice
    const best = getBestVoiceForLang(pageLang);
    if (best) utterance.voice = best;
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
}

// ensure voices list is populated in some browsers
if (speechSynthesisSupported && typeof window.speechSynthesis.onvoiceschanged !== 'undefined') {
    window.speechSynthesis.onvoiceschanged = function() { getAvailableVoices(); };
}

// Play spoken advice returned from server
const speechText = document.getElementById('speech-text');
if (speechOutput && speechOutput.dataset.text) {
    const text = speechOutput.dataset.text;
    if (text && text.trim()) {
        // show visible text
        if (speechText) {
            speechText.textContent = text;
            speechText.style.display = '';
        }
        // also show combined summary (inputs + advice) so everything is visible
        const summaryEl = document.getElementById('summary-text');
        if (summaryEl) {
            const template = (readAllBtn && readAllBtn.dataset && readAllBtn.dataset.summaryTemplate) || 'Summary — City: {city}. Crop: {crop}. Season: {season}.';
            const city = cityInput ? (cityInput.value || 'unknown') : 'unknown';
            const crop = cropInput ? (cropInput.value || 'unknown') : 'unknown';
            const seasonVal = seasonInput ? (seasonInput.value || 'unknown') : 'unknown';
            const summary = template.replace('{city}', city).replace('{crop}', crop).replace('{season}', seasonVal);
            summaryEl.textContent = summary + ' ' + text;
            summaryEl.style.display = '';
        }
    }
}

// replay button removed per user preference (no TTS)
