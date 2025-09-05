// TradeSim Web Interface - Application JavaScript

// Variables globales
let currentPage = 'home';
let websocket = null;
let gameConfig = {};
let autoScroll = true;

// Configuration par défaut (basée sur config.py)
const defaultConfig = {
    // Simulation de base
    nombre_tours: 100,
    n_entreprises: 2,
    prob_selection: 30,
    duree_pause: 0.1,
    tick_interval_event: 2,
    
    // Transactions
    qte_achat_min: 1,
    qte_achat_max: 40,
    qte_achat_prix_eleve_min: 1,
    qte_achat_prix_eleve_max: 20,
    seuil_prix_eleve: 100,
    budget_initial: 10000,
    stock_initial: 100,
    
    // Entreprises
    budget_entreprise_min: 18000,
    budget_entreprise_max: 35000,
    
    // Produits
    prix_produit_min: 5,
    prix_produit_max: 50,
    nombre_produits_defaut: 12,
    produits_actifs_min: 8,
    produits_actifs_max: 12,
    
    // Événements
    enable_inflation: true,
    enable_recharge_budget: true,
    enable_reassort: true,
    enable_variation_dispo: true,
    
    // Paramètres d'événements
    recharge_budget_min: 4000,
    recharge_budget_max: 8000,
    reassort_quantite_min: 10,
    reassort_quantite_max: 50,
    inflation_pourcentage_min: 30,
    inflation_pourcentage_max: 60,
    penalite_inflation: 15,
    duree_penalite_inflation: 50,
    
    // Probabilités d'événements
    prob_recharge_budget: 50,
    prob_reassort: 50,
    prob_inflation: 40,
    prob_variation_dispo: 30,
    
    // Monitoring
    enable_verbose: true,
    enable_metrics: true,
    metrics_collection_interval: 1.0,
    metrics_system_enabled: true,
    metrics_labels_enabled: false,
    log_level: 'INFO'
};

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 TradeSim Web Interface initialisée');
    loadDefaultConfig();
    testApiConnection();
    showPage('home');
    
    // Initialiser les tooltips Bootstrap
    initializeTooltips();
});

// Initialiser les tooltips Bootstrap
function initializeTooltips() {
    // Initialiser tous les tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    console.log('💡 Tooltips Bootstrap initialisés:', tooltipList.length);
}

// Navigation entre les pages
function showPage(pageName) {
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
    });
    
    document.getElementById(pageName + '-page').style.display = 'block';
    
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[onclick="showPage('${pageName}')"]`).classList.add('active');
    
    currentPage = pageName;
    
    if (pageName === 'config') {
        loadCurrentConfig();
    } else if (pageName === 'game') {
        initializeGamePage();
    }
}

// Charger la configuration par défaut
function loadDefaultConfig() {
    gameConfig = { ...defaultConfig };
    console.log('📋 Configuration par défaut chargée:', gameConfig);
}

// Tester la connexion à l'API
async function testApiConnection() {
    try {
        const response = await fetch('/api/health');
        if (response.ok) {
            const data = await response.json();
            console.log('✅ API connectée:', data);
            updateApiStatus(true);
        } else {
            throw new Error('API non disponible');
        }
    } catch (error) {
        console.error('❌ Erreur connexion API:', error);
        updateApiStatus(false);
    }
}

// Mettre à jour le statut de l'API
function updateApiStatus(connected) {
    const statusElement = document.querySelector('.navbar-text');
    if (statusElement) {
        if (connected) {
            statusElement.innerHTML = '<i class="fas fa-circle text-success me-1"></i>API Connectée';
        } else {
            statusElement.innerHTML = '<i class="fas fa-circle text-danger me-1"></i>API Déconnectée';
        }
    }
}

// Charger la configuration actuelle
function loadCurrentConfig() {
    // Paramètres de base
    document.getElementById('nombre-tours').value = gameConfig.nombre_tours;
    document.getElementById('n-entreprises').value = gameConfig.n_entreprises;
    document.getElementById('prob-selection').value = gameConfig.prob_selection;
    document.getElementById('duree-pause').value = gameConfig.duree_pause;
    document.getElementById('tick-interval-event').value = gameConfig.tick_interval_event;
    
    // Paramètres de transaction
    document.getElementById('qte-achat-min').value = gameConfig.qte_achat_min;
    document.getElementById('qte-achat-max').value = gameConfig.qte_achat_max;
    document.getElementById('qte-achat-prix-eleve-min').value = gameConfig.qte_achat_prix_eleve_min;
    document.getElementById('qte-achat-prix-eleve-max').value = gameConfig.qte_achat_prix_eleve_max;
    document.getElementById('seuil-prix-eleve').value = gameConfig.seuil_prix_eleve;
    document.getElementById('budget-initial').value = gameConfig.budget_initial;
    document.getElementById('stock-initial').value = gameConfig.stock_initial;
    
    // Configuration avancée
    document.getElementById('budget-entreprise-min').value = gameConfig.budget_entreprise_min;
    document.getElementById('budget-entreprise-max').value = gameConfig.budget_entreprise_max;
    document.getElementById('prix-produit-min').value = gameConfig.prix_produit_min;
    document.getElementById('prix-produit-max').value = gameConfig.prix_produit_max;
    document.getElementById('nombre-produits-defaut').value = gameConfig.nombre_produits_defaut;
    document.getElementById('produits-actifs-min').value = gameConfig.produits_actifs_min;
    document.getElementById('produits-actifs-max').value = gameConfig.produits_actifs_max;
    
    // Événements
    document.getElementById('enable-inflation').checked = gameConfig.enable_inflation;
    document.getElementById('enable-recharge-budget').checked = gameConfig.enable_recharge_budget;
    document.getElementById('enable-reassort').checked = gameConfig.enable_reassort;
    document.getElementById('enable-variation-dispo').checked = gameConfig.enable_variation_dispo;
    
    // Paramètres d'événements
    document.getElementById('recharge-budget-min').value = gameConfig.recharge_budget_min;
    document.getElementById('recharge-budget-max').value = gameConfig.recharge_budget_max;
    document.getElementById('reassort-quantite-min').value = gameConfig.reassort_quantite_min;
    document.getElementById('reassort-quantite-max').value = gameConfig.reassort_quantite_max;
    document.getElementById('inflation-pourcentage-min').value = gameConfig.inflation_pourcentage_min;
    document.getElementById('inflation-pourcentage-max').value = gameConfig.inflation_pourcentage_max;
    document.getElementById('penalite-inflation').value = gameConfig.penalite_inflation;
    document.getElementById('duree-penalite-inflation').value = gameConfig.duree_penalite_inflation;
    
    // Probabilités d'événements
    document.getElementById('prob-recharge-budget').value = gameConfig.prob_recharge_budget;
    document.getElementById('prob-reassort').value = gameConfig.prob_reassort;
    document.getElementById('prob-inflation').value = gameConfig.prob_inflation;
    document.getElementById('prob-variation-dispo').value = gameConfig.prob_variation_dispo;
    
    // Monitoring
    document.getElementById('metrics-collection-interval').value = gameConfig.metrics_collection_interval;
    document.getElementById('metrics-system-enabled').checked = gameConfig.metrics_system_enabled;
    document.getElementById('metrics-labels-enabled').checked = gameConfig.metrics_labels_enabled;
    document.getElementById('log-level').value = gameConfig.log_level;
    
    console.log('📋 Configuration chargée dans l\'interface');
}

// Sauvegarder la configuration actuelle
function saveCurrentConfig() {
    // Paramètres de base
    gameConfig.nombre_tours = parseInt(document.getElementById('nombre-tours').value);
    gameConfig.n_entreprises = parseInt(document.getElementById('n-entreprises').value);
    gameConfig.prob_selection = parseInt(document.getElementById('prob-selection').value);
    gameConfig.duree_pause = parseFloat(document.getElementById('duree-pause').value);
    gameConfig.tick_interval_event = parseInt(document.getElementById('tick-interval-event').value);
    
    // Paramètres de transaction
    gameConfig.qte_achat_min = parseInt(document.getElementById('qte-achat-min').value);
    gameConfig.qte_achat_max = parseInt(document.getElementById('qte-achat-max').value);
    gameConfig.qte_achat_prix_eleve_min = parseInt(document.getElementById('qte-achat-prix-eleve-min').value);
    gameConfig.qte_achat_prix_eleve_max = parseInt(document.getElementById('qte-achat-prix-eleve-max').value);
    gameConfig.seuil_prix_eleve = parseFloat(document.getElementById('seuil-prix-eleve').value);
    gameConfig.budget_initial = parseInt(document.getElementById('budget-initial').value);
    gameConfig.stock_initial = parseInt(document.getElementById('stock-initial').value);
    
    // Configuration avancée
    gameConfig.budget_entreprise_min = parseInt(document.getElementById('budget-entreprise-min').value);
    gameConfig.budget_entreprise_max = parseInt(document.getElementById('budget-entreprise-max').value);
    gameConfig.prix_produit_min = parseFloat(document.getElementById('prix-produit-min').value);
    gameConfig.prix_produit_max = parseFloat(document.getElementById('prix-produit-max').value);
    gameConfig.nombre_produits_defaut = parseInt(document.getElementById('nombre-produits-defaut').value);
    gameConfig.produits_actifs_min = parseInt(document.getElementById('produits-actifs-min').value);
    gameConfig.produits_actifs_max = parseInt(document.getElementById('produits-actifs-max').value);
    
    // Événements
    gameConfig.enable_inflation = document.getElementById('enable-inflation').checked;
    gameConfig.enable_recharge_budget = document.getElementById('enable-recharge-budget').checked;
    gameConfig.enable_reassort = document.getElementById('enable-reassort').checked;
    gameConfig.enable_variation_dispo = document.getElementById('enable-variation-dispo').checked;
    
    // Paramètres d'événements
    gameConfig.recharge_budget_min = parseInt(document.getElementById('recharge-budget-min').value);
    gameConfig.recharge_budget_max = parseInt(document.getElementById('recharge-budget-max').value);
    gameConfig.reassort_quantite_min = parseInt(document.getElementById('reassort-quantite-min').value);
    gameConfig.reassort_quantite_max = parseInt(document.getElementById('reassort-quantite-max').value);
    gameConfig.inflation_pourcentage_min = parseInt(document.getElementById('inflation-pourcentage-min').value);
    gameConfig.inflation_pourcentage_max = parseInt(document.getElementById('inflation-pourcentage-max').value);
    gameConfig.penalite_inflation = parseInt(document.getElementById('penalite-inflation').value);
    gameConfig.duree_penalite_inflation = parseInt(document.getElementById('duree-penalite-inflation').value);
    
    // Probabilités d'événements
    gameConfig.prob_recharge_budget = parseInt(document.getElementById('prob-recharge-budget').value);
    gameConfig.prob_reassort = parseInt(document.getElementById('prob-reassort').value);
    gameConfig.prob_inflation = parseInt(document.getElementById('prob-inflation').value);
    gameConfig.prob_variation_dispo = parseInt(document.getElementById('prob-variation-dispo').value);
    
    // Monitoring
    gameConfig.metrics_collection_interval = parseFloat(document.getElementById('metrics-collection-interval').value);
    gameConfig.metrics_system_enabled = document.getElementById('metrics-system-enabled').checked;
    gameConfig.metrics_labels_enabled = document.getElementById('metrics-labels-enabled').checked;
    gameConfig.log_level = document.getElementById('log-level').value;
    
    console.log('💾 Configuration sauvegardée:', gameConfig);
}

// Sauvegarder un template
function saveTemplate() {
    const templateName = prompt('Nom du template:');
    if (templateName) {
        saveCurrentConfig();
        const template = {
            name: templateName,
            config: gameConfig,
            created: new Date().toISOString()
        };
        
        const templates = JSON.parse(localStorage.getItem('tradesim_templates') || '[]');
        templates.push(template);
        localStorage.setItem('tradesim_templates', JSON.stringify(templates));
        
        alert(`✅ Template "${templateName}" sauvegardé !`);
        console.log('💾 Template sauvegardé:', template);
    }
}

// Charger un template
function loadTemplate() {
    const templates = JSON.parse(localStorage.getItem('tradesim_templates') || '[]');
    
    if (templates.length === 0) {
        alert('❌ Aucun template sauvegardé');
        return;
    }
    
    let templateList = 'Templates disponibles:\n\n';
    templates.forEach((template, index) => {
        templateList += `${index + 1}. ${template.name} (${new Date(template.created).toLocaleDateString()})\n`;
    });
    
    const choice = prompt(templateList + '\nEntrez le numéro du template à charger:');
    const index = parseInt(choice) - 1;
    
    if (index >= 0 && index < templates.length) {
        const template = templates[index];
        gameConfig = { ...template.config };
        loadCurrentConfig();
        alert(`✅ Template "${template.name}" chargé !`);
        console.log('📂 Template chargé:', template);
    }
}

// Lancer une partie
async function startGame() {
    try {
        saveCurrentConfig();
        showPage('game');
        initializeGamePage();
        await launchSimulation();
    } catch (error) {
        console.error('❌ Erreur lors du lancement de la partie:', error);
        alert('❌ Erreur lors du lancement de la partie: ' + error.message);
    }
}

// Initialiser la page de jeu
function initializeGamePage() {
    document.getElementById('total-tours').textContent = gameConfig.nombre_tours;
    document.getElementById('current-tours').textContent = '0';
    document.getElementById('total-budget').textContent = '0';
    document.getElementById('total-stock').textContent = '0';
    
    document.getElementById('events-log').innerHTML = '<p class="text-muted">En attente des événements...</p>';
    
    connectWebSocket();
    console.log('🎮 Page de jeu initialisée');
}

// Lancer la simulation via l'API
async function launchSimulation() {
    try {
        const simulationRequest = {
            tours: gameConfig.nombre_tours,
            verbose: gameConfig.enable_verbose,
            with_metrics: gameConfig.enable_metrics
        };
        
        console.log('🚀 Lancement de la simulation:', simulationRequest);
        
        const response = await fetch('/api/simulation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(simulationRequest)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('✅ Simulation lancée:', result);
            addEvent('🚀 Simulation lancée avec succès', 'success');
        } else {
            throw new Error(`Erreur API: ${response.status}`);
        }
        
    } catch (error) {
        console.error('❌ Erreur lors du lancement de la simulation:', error);
        addEvent('❌ Erreur lors du lancement de la simulation: ' + error.message, 'error');
    }
}

// Se connecter au WebSocket
function connectWebSocket() {
    try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//localhost:8000/ws`;
        
        websocket = new WebSocket(wsUrl);
        
        websocket.onopen = function() {
            console.log('🔌 WebSocket connecté');
            addEvent('🔌 Connexion WebSocket établie', 'info');
            websocket.send(JSON.stringify({ type: 'subscribe' }));
        };
        
        websocket.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            } catch (error) {
                console.error('❌ Erreur parsing WebSocket:', error);
            }
        };
        
        websocket.onclose = function() {
            console.log('🔌 WebSocket déconnecté');
            addEvent('🔌 Connexion WebSocket fermée', 'warning');
        };
        
        websocket.onerror = function(error) {
            console.error('❌ Erreur WebSocket:', error);
            addEvent('❌ Erreur WebSocket', 'error');
        };
        
    } catch (error) {
        console.error('❌ Erreur connexion WebSocket:', error);
        addEvent('❌ Impossible de se connecter au WebSocket', 'error');
    }
}

// Gérer les messages WebSocket
function handleWebSocketMessage(data) {
    console.log('📨 Message WebSocket reçu:', data);
    
    switch (data.type) {
        case 'simulation_completed':
            addEvent('✅ Simulation terminée', 'success');
            updateGameInfo(data.result);
            break;
            
        case 'simulation_error':
            addEvent('❌ Erreur simulation: ' + data.error, 'error');
            break;
            
        case 'subscribed':
            addEvent('📡 Abonnement aux mises à jour activé', 'info');
            break;
            
        default:
            addEvent('📨 ' + JSON.stringify(data), 'info');
    }
}

// Ajouter un événement au log
function addEvent(message, type = 'info') {
    const eventsLog = document.getElementById('events-log');
    const timestamp = new Date().toLocaleTimeString();
    
    const eventElement = document.createElement('div');
    eventElement.className = `mb-2 p-2 rounded border-start border-4 ${
        type === 'error' ? 'border-danger bg-danger bg-opacity-10' :
        type === 'success' ? 'border-success bg-success bg-opacity-10' :
        type === 'warning' ? 'border-warning bg-warning bg-opacity-10' :
        'border-info bg-info bg-opacity-10'
    }`;
    
    eventElement.innerHTML = `
        <small class="text-muted">[${timestamp}]</small>
        <span class="ms-2">${message}</span>
    `;
    
    eventsLog.insertBefore(eventElement, eventsLog.firstChild);
    
    if (autoScroll) {
        eventsLog.scrollTop = 0;
    }
    
    const events = eventsLog.children;
    if (events.length > 100) {
        eventsLog.removeChild(events[events.length - 1]);
    }
}

// Mettre à jour les informations de la partie
function updateGameInfo(result) {
    if (result) {
        document.getElementById('total-budget').textContent = Math.round(result.budget_total_actuel || 0);
        document.getElementById('total-stock').textContent = result.stock_total_actuel || 0;
        document.getElementById('current-tours').textContent = result.tours_completes || 0;
    }
}

// Effacer les événements
function clearEvents() {
    document.getElementById('events-log').innerHTML = '<p class="text-muted">Log effacé</p>';
}

// Basculer l'auto-scroll
function toggleAutoScroll() {
    autoScroll = !autoScroll;
    const button = event.target;
    button.innerHTML = autoScroll ? 
        '<i class="fas fa-arrow-down me-1"></i>Auto-scroll' : 
        '<i class="fas fa-pause me-1"></i>Auto-scroll';
    button.className = autoScroll ? 
        'btn btn-sm btn-outline-primary' : 
        'btn btn-sm btn-outline-secondary';
}

// Export des fonctions
window.showPage = showPage;
window.saveTemplate = saveTemplate;
window.loadTemplate = loadTemplate;
window.startGame = startGame;
window.clearEvents = clearEvents;
window.toggleAutoScroll = toggleAutoScroll;
