document.addEventListener('DOMContentLoaded', () => {
    // --- Element Selectors ---
    const chatLauncher = document.getElementById('chat-launcher');
    const chatWidget = document.getElementById('chat-widget');
    const chatBody = document.getElementById('chat-body');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const langSwitcherBtn = document.getElementById('lang-switcher-btn');
    const langMenu = document.getElementById('lang-menu');
    const voiceInputBtn = document.getElementById('voice-input-btn');
    const themeSwitcherBtn = document.getElementById('theme-switcher-btn');

    // --- State Variables ---
    const API_URL = ""; // same origin
    let currentUserLanguage = 'en';
    let isRecognizing = false;

    const placeholderTranslations = {
        'en': 'Type or say something...',
        'hi': 'अपना संदेश टाइप करें या बोलें...',
        'gu': 'તમારો સંદેશ લખો અથવા બોલો...',
        'mr': 'आपला संदेश टाइप करा किंवा बोला...',
        'bn': 'আপনার বার্তা টাইপ করুন বা বলুন...',
        'ta': 'உங்கள் செய்தியை உள்ளிடவும் அல்லது பேசவும்...',
        'te': 'మీ సందేశాన్ని టైప్ చేయండి లేదా చెప్పండి...',
        'kn': 'ನಿಮ್ಮ ಸಂದೇಶವನ್ನು ಟೈಪ್ ಮಾಡಿ ಅಥವಾ ಹೇಳಿ...',
        'ml': 'നിങ്ങളുടെ സന്ദേശം ടൈപ്പ് ചെയ്യുക അല്ലെങ്കിൽ പറയുക...',
        'pa': 'ਆਪਣਾ ਸੁਨੇਹਾ ਲਿਖੋ ਜਾਂ ਬੋਲੋ...',
        'raj': 'आपण संदेश टाइप करो या बोलो...'
    };

    // --- Speech Recognition ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;
    if (SpeechRecognition && voiceInputBtn) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = currentUserLanguage;

        recognition.onresult = (event) => {
            const transcript = event.results[event.results.length - 1][0].transcript.trim();
            chatInput.value = transcript;
            sendMessage();
        };
        recognition.onerror = () => addMessageToChat('bot', "Sorry, I couldn't hear that. Check microphone permissions.");
        recognition.onend = () => {
            isRecognizing = false;
            voiceInputBtn.classList.remove('listening');
        };
    } else if (voiceInputBtn) {
        voiceInputBtn.style.display = 'none';
    }

    // --- Event Listeners ---
    chatLauncher?.addEventListener('click', toggleChatWidget);
    sendBtn?.addEventListener('click', sendMessage);
    langSwitcherBtn?.addEventListener('click', (e) => { e.stopPropagation(); langMenu?.classList.toggle('hidden'); });
    voiceInputBtn?.addEventListener('click', toggleVoiceRecognition);

    chatInput?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
    chatInput?.addEventListener('input', autoResizeInput);

    langMenu?.addEventListener('click', (e) => {
        if (e.target.classList.contains('lang-option')) {
            currentUserLanguage = e.target.getAttribute('data-lang').split('-')[0];
            if (recognition) recognition.lang = currentUserLanguage;
            chatInput.placeholder = placeholderTranslations[currentUserLanguage] || placeholderTranslations['en'];
            langMenu.classList.add('hidden');
            chatBody.innerHTML = '';
            startConversation();
        }
    });

    chatBody?.addEventListener('click', (event) => {
        if (event.target.classList.contains('quick-reply')) {
            const payload = event.target.getAttribute('data-payload');
            const text = event.target.innerText;
            event.target.closest('.quick-replies')?.remove();
            addMessageToChat('user', text);
            sendPayloadToBackend(payload, false);//make sure lang is always currentUserLanguage
        }
    });

    document.addEventListener('click', (event) => {
        if (langMenu && chatWidget && !chatWidget.contains(event.target)) {
            langMenu.classList.add('hidden');
        }
    });

    // --- Initial Setup ---
    loadTheme();

    // --- Main Functions ---
    function toggleChatWidget() {
        const isOpen = chatWidget?.classList.toggle('open');
        if (isOpen && chatBody?.children.length === 0) startConversation();
        if (isOpen && chatInput) setTimeout(() => chatInput.focus(), 200);
    }

    function startConversation() {
        sendPayloadToBackend('', true);
    }

    function sendMessage() {
        if (!chatInput) return;
        const userInput = chatInput.value.trim();
        if (userInput) {
            addMessageToChat('user', userInput);
            sendPayloadToBackend(userInput);
            chatInput.value = '';
            autoResizeInput();
        }
    }

    async function sendPayloadToBackend(payload, isGreet = false) {
        showTypingIndicator();
        try {
            const url = isGreet ? `/greet?lang=${currentUserLanguage}` : '/chat';
            const bodyData = isGreet ? null : JSON.stringify({ 
                query: payload, 
                lang: currentUserLanguage 
            });
            const response = await fetch(url, {
                method: isGreet ? 'GET' : 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: bodyData
            });
            const data = await response.json();
            removeTypingIndicator();
            handleBotResponse(data);
        } catch (err) {
            removeTypingIndicator();
            addMessageToChat('bot', "Error connecting to server. Please try again.");
            console.error(err);
        }
    }

    function handleBotResponse(reply) {
        if (reply?.answer) {
            addMessageToChat('bot', reply.answer);
            if (reply.quick_replies?.length > 0) addQuickReplies(reply.quick_replies);
        } else {
            addMessageToChat('bot', "Sorry, I encountered a problem.");
        }
    }

    // --- UI & Helper Functions ---
    function addMessageToChat(sender, message) {
        if (!chatBody) return;
        const messageContainer = document.createElement('div');
        messageContainer.className = `message-container ${sender}-container`;

        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        messageElement.innerHTML = message;

        const timeElement = document.createElement('div');
        timeElement.className = 'message-time';
        timeElement.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageContainer.appendChild(messageElement);
        messageContainer.appendChild(timeElement);
        chatBody.appendChild(messageContainer);
        scrollToBottom();
    }

    function addQuickReplies(replies) {
        if (!chatBody) return;
        const container = document.createElement('div');
        container.className = 'quick-replies';
        replies.forEach((r, index) => {
            const btn = document.createElement('button');
            btn.className = 'quick-reply';
            btn.innerHTML = r.text;
            btn.setAttribute('data-payload', r.payload);
            btn.style.animationDelay = `${index * 0.1}s`;
            container.appendChild(btn);
        });
        chatBody.appendChild(container);
        scrollToBottom();
    }

    function showTypingIndicator() {
        if (!chatBody || chatBody.querySelector('#typing-indicator')) return;
        const indicator = document.createElement('div');
        indicator.className = 'message bot-message typing-indicator';
        indicator.id = 'typing-indicator';
        indicator.innerHTML = `<span></span><span></span><span></span>`;
        chatBody.appendChild(indicator);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = chatBody?.querySelector('#typing-indicator');
        if (indicator) indicator.remove();
    }

    function autoResizeInput() {
        if (!chatInput) return;
        chatInput.style.height = 'auto';
        chatInput.style.height = `${Math.min(chatInput.scrollHeight, 100)}px`;
    }

    function scrollToBottom() {
        if (chatBody) chatBody.scrollTop = chatBody.scrollHeight;
    }

    function toggleVoiceRecognition() {
        if (!recognition) return;
        if (!isRecognizing) {
            isRecognizing = true;
            voiceInputBtn.classList.add('listening');
            recognition.start();
        }
    }

    // --- Theme Management ---
    function toggleTheme() {
        chatWidget.classList.toggle('dark-mode');
        localStorage.setItem('chat-theme', chatWidget.classList.contains('dark-mode') ? 'dark' : 'light');
    }

    function loadTheme() {
        const theme = localStorage.getItem('chat-theme');
        if (theme === 'dark') chatWidget.classList.add('dark-mode');
    }

    themeSwitcherBtn?.addEventListener('click', toggleTheme);
});
