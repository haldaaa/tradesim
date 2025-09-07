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
    nombre_entreprises: 3,
    budget_entreprise_min: 18000,
    budget_entreprise_max: 35000,
    
    // Produits
    prix_produit_min: 5,
    prix_produit_max: 50,
    nombre_produits_defaut: 12,
    produits_actifs_min: 8,
    produits_actifs_max: 12,
    
    // Fournisseurs
    nombre_fournisseurs: 5,
    
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

/**
 * Initialise la page de jeu
 * Met à jour l'interface avec les données actuelles
 */
function initializeGamePage() {
    try {
        console.log('🎮 Initialisation de la page de jeu...');
        
        // Mettre à jour le nombre total de tours
        const totalToursElement = document.getElementById('total-tours');
        if (totalToursElement && gameConfig.nombre_tours) {
            totalToursElement.textContent = gameConfig.nombre_tours;
        }
        
        // Ajouter un message d'initialisation
        addEventToLog('🎮 Page de jeu initialisée - En attente de la simulation...');
        
        console.log('✅ Page de jeu initialisée');
        
    } catch (error) {
        console.error('❌ Erreur lors de l\'initialisation de la page de jeu:', error);
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
    document.getElementById('nombre-entreprises').value = gameConfig.nombre_entreprises;
    document.getElementById('budget-entreprise-min').value = gameConfig.budget_entreprise_min;
    document.getElementById('budget-entreprise-max').value = gameConfig.budget_entreprise_max;
    document.getElementById('prix-produit-min').value = gameConfig.prix_produit_min;
    document.getElementById('prix-produit-max').value = gameConfig.prix_produit_max;
    document.getElementById('nombre-produits-defaut').value = gameConfig.nombre_produits_defaut;
    document.getElementById('produits-actifs-min').value = gameConfig.produits_actifs_min;
    document.getElementById('produits-actifs-max').value = gameConfig.produits_actifs_max;
    document.getElementById('nombre-fournisseurs').value = gameConfig.nombre_fournisseurs;
    
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
    gameConfig.nombre_entreprises = parseInt(document.getElementById('nombre-entreprises').value);
    gameConfig.budget_entreprise_min = parseInt(document.getElementById('budget-entreprise-min').value);
    gameConfig.budget_entreprise_max = parseInt(document.getElementById('budget-entreprise-max').value);
    gameConfig.prix_produit_min = parseFloat(document.getElementById('prix-produit-min').value);
    gameConfig.prix_produit_max = parseFloat(document.getElementById('prix-produit-max').value);
    gameConfig.nombre_produits_defaut = parseInt(document.getElementById('nombre-produits-defaut').value);
    gameConfig.produits_actifs_min = parseInt(document.getElementById('produits-actifs-min').value);
    gameConfig.produits_actifs_max = parseInt(document.getElementById('produits-actifs-max').value);
    gameConfig.nombre_fournisseurs = parseInt(document.getElementById('nombre-fournisseurs').value);
    
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
async function startGameOriginal() {
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

// ===== FONCTION DE LANCEMENT DE SIMULATION =====

/**
 * Lance la simulation en appelant l'API backend
 * Utilise la configuration actuelle et gère les erreurs
 */
async function launchSimulation() {
    try {
        console.log('🚀 Lancement de la simulation...');
        
        // 1. Sauvegarder la configuration actuelle
        saveCurrentConfig();
        
        // 2. Préparer les données pour l'API
        const simulationData = {
            tours: gameConfig.nombre_tours,
            verbose: true,
            with_metrics: true
        };
        
        console.log('📡 Envoi de la configuration:', simulationData);
        
        // 3. Appeler l'API /simulation
        const response = await fetch('/api/simulation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(simulationData)
        });
        
        // 4. Gérer la réponse
        if (response.ok) {
            const result = await response.json();
            console.log('✅ Simulation démarrée avec succès:', result);
            
            // 5. Mettre à jour l'interface avec les résultats
            updateGameInfo(result.result);
            
            // 6. Connecter au WebSocket pour les événements temps réel
            connectWebSocket();
            
            return result;
        } else {
            const errorData = await response.json();
            throw new Error(`Erreur API: ${errorData.detail || response.statusText}`);
        }
        
    } catch (error) {
        console.error('❌ Erreur lors du lancement de la simulation:', error);
        showError(`Erreur: ${error.message}`);
        return null;
    }
}

/**
 * Connecte au WebSocket pour recevoir les événements temps réel
 * Gère la reconnexion automatique en cas de déconnexion
 */
function connectWebSocket() {
    try {
        console.log('🔌 Connexion au WebSocket...');
        
        // Créer la connexion WebSocket
        const ws = new WebSocket('ws://localhost:8000/ws');
        
        // Événement d'ouverture
        ws.onopen = () => {
            console.log('✅ WebSocket connecté');
            
            // S'abonner aux mises à jour
            ws.send(JSON.stringify({ type: 'subscribe' }));
            
            // Afficher le statut de connexion
            showConnectionStatus('connecté');
        };
        
        // Événement de réception de message
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('📨 Message WebSocket reçu:', data);
                
                // Traiter selon le type de message
                switch(data.type) {
                    case 'simulation_started':
                        handleSimulationStarted(data);
                        break;
                    case 'tour_completed':
                        handleTourCompleted(data);
                        break;
                    case 'simulation_completed':
                        handleSimulationCompleted(data);
                        break;
                    case 'simulation_error':
                        handleSimulationError(data);
                        break;
                    case 'subscribed':
                        console.log('✅ Abonnement WebSocket confirmé');
                        break;
                    case 'pong':
                        console.log('🏓 Pong reçu');
                        break;
                    default:
                        console.log('📨 Message inconnu:', data);
                }
            } catch (error) {
                console.error('❌ Erreur parsing message WebSocket:', error);
            }
        };
        
        // Événement de fermeture
        ws.onclose = (event) => {
            console.log('🔌 WebSocket fermé:', event.code, event.reason);
            showConnectionStatus('déconnecté');
            
            // Tentative de reconnexion après 3 secondes
            setTimeout(() => {
                console.log('🔄 Tentative de reconnexion WebSocket...');
                connectWebSocket();
            }, 3000);
        };
        
        // Événement d'erreur
        ws.onerror = (error) => {
            console.error('❌ Erreur WebSocket:', error);
            showConnectionStatus('erreur');
        };
        
        // Stocker la référence pour pouvoir fermer la connexion
        window.tradesimWebSocket = ws;
        
    } catch (error) {
        console.error('❌ Erreur lors de la connexion WebSocket:', error);
        showConnectionStatus('erreur');
    }
}

/**
 * Gère le début de simulation reçue via WebSocket
 * Initialise l'interface pour la simulation
 */
function handleSimulationStarted(data) {
    console.log('🚀 Simulation démarrée:', data);
    
    // Ajouter un événement au log
    addEventToLog(`🚀 Simulation démarrée pour ${data.tours} tours`);
    
    // Afficher un message de début
    showSuccess(`Simulation démarrée pour ${data.tours} tours !`);
}

/**
 * Gère la fin d'un tour reçue via WebSocket
 * Met à jour l'interface avec les données du tour
 * IMPORTANT: C'est ici qu'on collecte les données pour Grafana
 * FORMAT 4C-C: Timeline ultra détaillée avec calculs de probabilités
 */
function handleTourCompleted(data) {
    console.log('🔄 Tour terminé:', data);
    
    // Mettre à jour les informations de jeu avec les stats
    if (data.stats) {
        updateGameInfo(data.stats);
    }
    
    // FORMAT 4C-C: Afficher la timeline ultra détaillée
    displayTourTimeline4CC(data);
    
    // Afficher les métriques pour Grafana
    if (data.stats) {
        console.log('📊 Métriques pour Grafana:', {
            tour: data.tour,
            budget_total: data.stats.budget_total_actuel,
            stock_total: data.stats.stock_total_actuel,
            tours_completes: data.stats.tours_completes,
            evenements_appliques: data.stats.evenements_appliques,
            timestamp: data.timestamp
        });
    }
}

/**
 * Gère la fin de simulation reçue via WebSocket
 * Met à jour l'interface avec les résultats finaux
 */
function handleSimulationCompleted(data) {
    console.log('🎯 Simulation terminée:', data);
    
    // Mettre à jour les informations de jeu
    if (data.result) {
        updateGameInfo(data.result);
    }
    
    // Ajouter un événement au log
    addEventToLog(`🎯 Simulation terminée après ${data.tours} tours`);
    
    // Afficher un message de succès
    showSuccess('Simulation terminée avec succès !');
}

/**
 * Gère les erreurs de simulation reçues via WebSocket
 * Affiche les erreurs à l'utilisateur
 */
function handleSimulationError(data) {
    console.error('❌ Erreur de simulation:', data);
    
    // Afficher l'erreur
    showError(`Erreur de simulation: ${data.error}`);
    
    // Ajouter l'erreur au log
    addEventToLog(`❌ Erreur: ${data.error}`);
}

/**
 * Met à jour les informations de jeu affichées
 * Utilise les données reçues de l'API ou du WebSocket
 */
function updateGameInfo(result) {
    if (!result) return;
    
    try {
        // Mettre à jour les éléments de l'interface
        const budgetElement = document.getElementById('total-budget');
        const stockElement = document.getElementById('total-stock');
        const toursElement = document.getElementById('current-tours');
        
        if (budgetElement && result.budget_total_actuel !== undefined) {
            budgetElement.textContent = Math.round(result.budget_total_actuel);
        }
        
        if (stockElement && result.stock_total_actuel !== undefined) {
            stockElement.textContent = result.stock_total_actuel;
        }
        
        if (toursElement && result.tours_completes !== undefined) {
            toursElement.textContent = result.tours_completes;
        }
        
        console.log('📊 Interface mise à jour:', {
            budget: result.budget_total_actuel,
            stock: result.stock_total_actuel,
            tours: result.tours_completes
        });
        
    } catch (error) {
        console.error('❌ Erreur lors de la mise à jour de l\'interface:', error);
    }
}

/**
 * Affiche la timeline ultra détaillée FORMAT 4C-C
 * Avec calculs de probabilités et formules complètes
 */
function displayTourTimeline4CC(data) {
    try {
        const eventsLog = document.getElementById('events-log');
        if (!eventsLog) {
            console.warn('⚠️ Élément events-log non trouvé');
            return;
        }
        
        // Créer le conteneur principal du tour
        const tourContainer = document.createElement('div');
        tourContainer.className = 'mb-4 p-3 border border-2 border-primary bg-light';
        
        // En-tête du tour
        const tourHeader = document.createElement('div');
        tourHeader.className = 'fw-bold text-primary mb-3';
        tourHeader.innerHTML = `🔄 Tour ${data.tour}/${data.total_tours} - Tick ${data.tour}`;
        tourContainer.appendChild(tourHeader);
        
        // Timeline des événements
        const timeline = document.createElement('div');
        timeline.className = 'timeline-4cc';
        
        // Ajouter les transactions détaillées
        if (data.result.transactions_effectuees > 0) {
            addDetailedTransactionsToTimeline(timeline, data);
        } else {
            // Afficher "Aucune transaction" même si 0
            addNoTransactionToTimeline(timeline);
        }
        
        // Ajouter les événements détaillés avec calculs de probabilités
        if (data.result.evenements_detaille && data.result.evenements_detaille.length > 0) {
            addDetailedEventsToTimeline(timeline, data);
        } else if (data.result.evenements_appliques > 0) {
            // Si on a des événements mais pas de détails, afficher un message
            addEventsSummaryToTimeline(timeline, data);
        } else {
            // Afficher "Aucun événement" même si 0
            addNoEventToTimeline(timeline);
        }
        
        // Ajouter les métriques globales
        addGlobalMetricsToTimeline(timeline, data);
        
        tourContainer.appendChild(timeline);
        
        // Ajouter au début du log
        eventsLog.insertBefore(tourContainer, eventsLog.firstChild);
        
        // Limiter à 10 tours maximum
        const tours = eventsLog.querySelectorAll('.border-primary');
        if (tours.length > 10) {
            eventsLog.removeChild(tours[tours.length - 1]);
        }
        
        console.log('📝 Timeline 4C-C ajoutée pour le tour:', data.tour);
        
    } catch (error) {
        console.error('❌ Erreur lors de l\'affichage de la timeline 4C-C:', error);
    }
}

/**
 * Ajoute les transactions détaillées à la timeline (comme CLI)
 */
function addDetailedTransactionsToTimeline(timeline, data) {
    const transactionElement = document.createElement('div');
    transactionElement.className = 'mb-3 p-2 border-start border-3 border-success bg-white';
    
    const timestamp = new Date().toLocaleTimeString();
    const icon = '🎯';
    const status = 'TRANSACTIONS EFFECTUÉES';
    
    // Compter le nombre réel de transactions détaillées
    const nbTransactions = data.result.transactions_detaille ? data.result.transactions_detaille.length : data.result.transactions_effectuees;
    
    let transactionHTML = `
        <div class="fw-bold text-success">
            ${icon} ${status}
        </div>
        <div class="ms-3 mt-2">
            <div><strong>Nombre de transactions:</strong> ${nbTransactions}</div>
            <div><strong>Timestamp:</strong> ${timestamp}</div>
    `;
    
    // Ajouter les détails des transactions si disponibles (FORMAT 4C-C)
    if (data.result.transactions_detaille && data.result.transactions_detaille.length > 0) {
        transactionHTML += '<div class="mt-2"><strong>Détails des transactions:</strong></div>';
        data.result.transactions_detaille.forEach((txn, index) => {
            const budgetAvant = txn.budget_avant || 'N/A';
            const budgetApres = txn.budget_apres || 'N/A';
            const prixUnitaire = txn.prix_unitaire || 'N/A';
            const quantite = txn.quantite || 'N/A';
            const statut = txn.statut || 'SUCCÈS';
            const statutIcon = statut === 'SUCCÈS' ? '✅' : '❌';
            const raisonEchec = txn.raison_echec ? ` (${txn.raison_echec})` : '';
            
            transactionHTML += `
                <div class="ms-3 mt-1 small">
                    • ${statutIcon} ${txn.entreprise || 'Entreprise'} → ${txn.produit || 'Produit'} (${txn.fournisseur || 'Fournisseur'})
                    <br>&nbsp;&nbsp;&nbsp;💰 Budget: ${budgetAvant}€ → ${budgetApres}€
                    <br>&nbsp;&nbsp;&nbsp;📦 Prix: ${prixUnitaire}€ × ${quantite} = ${txn.montant_total || 'N/A'}€${raisonEchec}
                </div>
            `;
        });
    }
    
    transactionHTML += `</div>`;
    transactionElement.innerHTML = transactionHTML;
    timeline.appendChild(transactionElement);
}

/**
 * Ajoute les transactions à la timeline (version simple)
 */
function addTransactionToTimeline(timeline, data) {
    if (data.result && data.result.transactions_effectuees > 0) {
        const transactionElement = document.createElement('div');
        transactionElement.className = 'mb-3 p-2 border-start border-3 border-success bg-white';
        
        const timestamp = new Date().toLocaleTimeString();
        const icon = '🎯';
        const status = 'TRANSACTIONS EFFECTUÉES';
        
        let transactionHTML = `
            <div class="fw-bold text-success">
                ${icon} ${status}
            </div>
            <div class="ms-3 mt-2">
                <div><strong>Nombre de transactions:</strong> ${data.result.transactions_effectuees}</div>
                <div><strong>Timestamp:</strong> ${timestamp}</div>
        `;
        
        transactionHTML += `</div>`;
        transactionElement.innerHTML = transactionHTML;
        timeline.appendChild(transactionElement);
    }
}

/**
 * Ajoute "Aucune transaction" à la timeline
 */
function addNoTransactionToTimeline(timeline) {
    const transactionElement = document.createElement('div');
    transactionElement.className = 'mb-3 p-2 border-start border-3 border-secondary bg-white';
    
    const timestamp = new Date().toLocaleTimeString();
    const icon = '⏸️';
    const status = 'AUCUNE TRANSACTION';
    
    let transactionHTML = `
        <div class="fw-bold text-muted">
            ${icon} ${status}
        </div>
        <div class="ms-3 mt-2">
            <div><strong>Raison:</strong> Aucune transaction effectuée dans ce tour</div>
            <div><strong>Timestamp:</strong> ${timestamp}</div>
    `;
    
    transactionHTML += `</div>`;
    transactionElement.innerHTML = transactionHTML;
    timeline.appendChild(transactionElement);
}

/**
 * Ajoute un résumé des événements quand on n'a pas les détails
 */
function addEventsSummaryToTimeline(timeline, data) {
    const eventElement = document.createElement('div');
    eventElement.className = 'mb-3 p-2 border-start border-3 border-warning bg-white';
    
    const timestamp = new Date().toLocaleTimeString();
    const icon = '🎲';
    const status = 'ÉVÉNEMENTS APPLIQUÉS';
    
    let eventHTML = `
        <div class="fw-bold text-warning">
            ${icon} ${status}
        </div>
        <div class="ms-3 mt-2">
            <div><strong>Nombre d'événements:</strong> ${data.result.evenements_appliques}</div>
            <div><strong>Timestamp:</strong> ${timestamp}</div>
            <div class="text-muted small">Détails des événements en cours de traitement...</div>
        </div>
    `;
    
    eventElement.innerHTML = eventHTML;
    timeline.appendChild(eventElement);
}

/**
 * Ajoute les événements détaillés à la timeline (comme CLI)
 */
function addDetailedEventsToTimeline(timeline, data) {
    if (data.result.evenements_detaille && data.result.evenements_detaille.length > 0) {
        data.result.evenements_detaille.forEach((event, index) => {
            const eventElement = document.createElement('div');
            eventElement.className = 'mb-3 p-2 border-start border-3 border-warning bg-white';
            
            let eventType = 'ÉVÉNEMENT';
            let icon = '🎲';
            let color = 'warning';
            
            // Utiliser les données nettoyées si disponibles
            const eventDescription = event.log_humain_clean || event.log_humain || 'N/A';
            
            if (eventDescription) {
                if (eventDescription.includes('INFLATION')) {
                    eventType = 'ÉVÉNEMENT INFLATION';
                    icon = '🔥';
                    color = 'danger';
                } else if (eventDescription.includes('REASSORT')) {
                    eventType = 'ÉVÉNEMENT REASSORT';
                    icon = '📦';
                    color = 'info';
                } else if (eventDescription.includes('RECHARGE')) {
                    eventType = 'ÉVÉNEMENT RECHARGE';
                    icon = '💰';
                    color = 'success';
                }
            }
            
            let eventHTML = `
                <div class="fw-bold text-${color}">
                    ${icon} ${eventType}
                </div>
                <div class="ms-3 mt-2">
                    <div><strong>Description:</strong> ${eventDescription}</div>
                    <div><strong>Timestamp:</strong> ${event.timestamp || new Date().toLocaleTimeString()}</div>
            `;
            
            // Ajouter les calculs de probabilités si disponibles (FORMAT 4C-C)
            if (event.probability_calculation) {
                eventHTML += `<div class="mt-2"><strong>Calcul de probabilité:</strong></div>`;
                eventHTML += `<div class="ms-3 small">${event.probability_calculation}</div>`;
            }
            
            // Ajouter les détails du calcul si disponibles
            if (event.seuil_declenchement !== undefined && event.valeur_aleatoire !== undefined) {
                const statutDeclenche = event.valeur_aleatoire <= event.seuil_declenchement ? 'DÉCLENCHÉ' : 'NON DÉCLENCHÉ';
                const statutIcon = statutDeclenche === 'DÉCLENCHÉ' ? '✅' : '❌';
                const raison = statutDeclenche === 'NON DÉCLENCHÉ' ? ` (${event.valeur_aleatoire.toFixed(3)} > ${event.seuil_declenchement.toFixed(3)})` : ` (${event.valeur_aleatoire.toFixed(3)} ≤ ${event.seuil_declenchement.toFixed(3)})`;
                
                eventHTML += `
                    <div class="mt-2"><strong>Résultat:</strong></div>
                    <div class="ms-3 small">
                        ${statutIcon} ${statutDeclenche}${raison}
                    </div>
                `;
            }
            
            eventHTML += `</div>`;
            eventElement.innerHTML = eventHTML;
            timeline.appendChild(eventElement);
        });
    }
}

/**
 * Ajoute les événements avec calculs de probabilités à la timeline
 */
function addEventsToTimeline(timeline, events) {
    if (events && events.length > 0) {
        events.forEach((event, index) => {
            const eventElement = document.createElement('div');
            eventElement.className = 'mb-3 p-2 border-start border-3 border-warning bg-white';
            
            let eventType = 'ÉVÉNEMENT';
            let icon = '🎲';
            let color = 'warning';
            
            if (event.log_humain) {
                if (event.log_humain.includes('INFLATION')) {
                    eventType = 'ÉVÉNEMENT INFLATION';
                    icon = '🔥';
                    color = 'danger';
                } else if (event.log_humain.includes('REASSORT')) {
                    eventType = 'ÉVÉNEMENT REASSORT';
                    icon = '📦';
                    color = 'info';
                } else if (event.log_humain.includes('RECHARGE')) {
                    eventType = 'ÉVÉNEMENT RECHARGE BUDGET';
                    icon = '💰';
                    color = 'success';
                }
            }
            
            let eventHTML = `
                <div class="fw-bold text-${color}">
                    ${icon} ${eventType}
                </div>
                <div class="ms-3 mt-2">
                    <div><strong>Description:</strong> ${event.log_humain || 'Événement appliqué'}</div>
            `;
            
            if (event.probability_calculation) {
                const calc = event.probability_calculation;
                eventHTML += `
                    <div class="mt-2 p-2 bg-light border rounded">
                        <strong>🧮 CALCUL:</strong> ${calc.formula}
                    </div>
                `;
            }
            
            eventHTML += `</div>`;
            eventElement.innerHTML = eventHTML;
            timeline.appendChild(eventElement);
        });
    }
}

/**
 * Ajoute "Aucun événement" à la timeline
 */
function addNoEventToTimeline(timeline) {
    const eventElement = document.createElement('div');
    eventElement.className = 'mb-3 p-2 border-start border-3 border-secondary bg-white';
    
    const timestamp = new Date().toLocaleTimeString();
    const icon = '⏸️';
    const status = 'AUCUN ÉVÉNEMENT';
    
    let eventHTML = `
        <div class="fw-bold text-muted">
            ${icon} ${status}
        </div>
        <div class="ms-3 mt-2">
            <div><strong>Raison:</strong> Aucun événement déclenché dans ce tour</div>
            <div><strong>Timestamp:</strong> ${timestamp}</div>
    `;
    
    eventHTML += `</div>`;
    eventElement.innerHTML = eventHTML;
    timeline.appendChild(eventElement);
}

/**
 * Ajoute les métriques globales à la timeline
 */
function addGlobalMetricsToTimeline(timeline, data) {
    const metricsElement = document.createElement('div');
    metricsElement.className = 'mb-3 p-2 border-start border-3 border-info bg-white';
    
    const timestamp = new Date().toLocaleTimeString();
    
    let metricsHTML = `
        <div class="fw-bold text-info">
            📊 MÉTRIQUES GLOBALES
        </div>
        <div class="ms-3 mt-2">
            <div><strong>Budget total:</strong> ${data.stats.budget_total?.toFixed(2) || 'N/A'}€ | <strong>Stock total:</strong> ${data.stats.stock_total || 'N/A'} | <strong>Tours:</strong> ${data.tour}/${data.total_tours}</div>
            <div><strong>Événements appliqués:</strong> ${data.stats.evenements_appliques || 0} | <strong>Durée simulation:</strong> ${data.stats.duree_simulation || 'N/A'}s</div>
        </div>
    `;
    
    metricsElement.innerHTML = metricsHTML;
    timeline.appendChild(metricsElement);
}

/**
 * Ajoute un événement au log de la partie
 * Met à jour l'interface avec les événements en temps réel
 */
function addEventToLog(eventText) {
    try {
        const eventsLog = document.getElementById('events-log');
        if (!eventsLog) {
            console.warn('⚠️ Élément events-log non trouvé');
            return;
        }
        
        // Créer un nouvel élément d'événement
        const eventElement = document.createElement('div');
        eventElement.className = 'mb-2 p-2 border-start border-3 border-primary bg-light';
        eventElement.innerHTML = `
            <small class="text-muted">${new Date().toLocaleTimeString()}</small>
            <div class="fw-bold">${eventText}</div>
        `;
        
        // Ajouter au début du log
        eventsLog.insertBefore(eventElement, eventsLog.firstChild);
        
        // Limiter à 50 événements maximum
        const events = eventsLog.children;
        if (events.length > 50) {
            eventsLog.removeChild(events[events.length - 1]);
        }
        
        console.log('📝 Événement ajouté au log:', eventText);
        
    } catch (error) {
        console.error('❌ Erreur lors de l\'ajout d\'événement au log:', error);
    }
}

/**
 * Affiche le statut de connexion WebSocket
 * Met à jour l'interface pour indiquer l'état de la connexion
 */
function showConnectionStatus(status) {
    // Créer ou mettre à jour l'indicateur de statut
    let statusElement = document.getElementById('websocket-status');
    if (!statusElement) {
        statusElement = document.createElement('div');
        statusElement.id = 'websocket-status';
        statusElement.className = 'alert alert-info';
        statusElement.style.position = 'fixed';
        statusElement.style.top = '10px';
        statusElement.style.right = '10px';
        statusElement.style.zIndex = '9999';
        document.body.appendChild(statusElement);
    }
    
    // Mettre à jour le contenu selon le statut
    switch(status) {
        case 'connecté':
            statusElement.className = 'alert alert-success';
            statusElement.innerHTML = '<i class="fas fa-wifi"></i> WebSocket connecté';
            break;
        case 'déconnecté':
            statusElement.className = 'alert alert-warning';
            statusElement.innerHTML = '<i class="fas fa-wifi"></i> WebSocket déconnecté - Reconnexion...';
            break;
        case 'erreur':
            statusElement.className = 'alert alert-danger';
            statusElement.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Erreur WebSocket';
            break;
    }
}

/**
 * Affiche un message d'erreur à l'utilisateur
 * Utilise Bootstrap pour un affichage cohérent
 */
function showError(message) {
    // Créer ou mettre à jour l'élément d'erreur
    let errorElement = document.getElementById('error-message');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.id = 'error-message';
        errorElement.className = 'alert alert-danger';
        errorElement.style.position = 'fixed';
        errorElement.style.top = '60px';
        errorElement.style.right = '10px';
        errorElement.style.zIndex = '9999';
        errorElement.style.maxWidth = '400px';
        document.body.appendChild(errorElement);
    }
    
    errorElement.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i> ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    // Supprimer automatiquement après 5 secondes
    setTimeout(() => {
        if (errorElement && errorElement.parentElement) {
            errorElement.remove();
        }
    }, 5000);
}

/**
 * Affiche un message de succès à l'utilisateur
 * Utilise Bootstrap pour un affichage cohérent
 */
function showSuccess(message) {
    // Créer ou mettre à jour l'élément de succès
    let successElement = document.getElementById('success-message');
    if (!successElement) {
        successElement = document.createElement('div');
        successElement.id = 'success-message';
        successElement.className = 'alert alert-success';
        successElement.style.position = 'fixed';
        successElement.style.top = '60px';
        successElement.style.right = '10px';
        successElement.style.zIndex = '9999';
        successElement.style.maxWidth = '400px';
        document.body.appendChild(successElement);
    }
    
    successElement.innerHTML = `
        <i class="fas fa-check-circle"></i> ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    // Supprimer automatiquement après 3 secondes
    setTimeout(() => {
        if (successElement && successElement.parentElement) {
            successElement.remove();
        }
    }, 3000);
}

// ===== FONCTIONS POUR LA MODAL DE CONFIRMATION =====

/**
 * Affiche la modal de confirmation avec tous les paramètres de configuration
 * Collecte les valeurs actuelles et les affiche dans la modal
 */
function showConfigModal() {
    // Sauvegarder la configuration actuelle
    saveCurrentConfig();
    
    // Remplir la modal avec les valeurs actuelles
    fillModalWithCurrentConfig();
    
    // Afficher la modal
    const modal = new bootstrap.Modal(document.getElementById('configModal'));
    modal.show();
}

/**
 * Remplit la modal avec la configuration actuelle
 * Met à jour tous les éléments de la modal avec les valeurs du formulaire
 */
function fillModalWithCurrentConfig() {
    // Section 1: Création de la Partie
    document.getElementById('modal-nombre-tours').textContent = document.getElementById('nombre-tours').value;
    document.getElementById('modal-nombre-entreprises').textContent = document.getElementById('nombre-entreprises').value;
    document.getElementById('modal-nombre-fournisseurs').textContent = document.getElementById('nombre-fournisseurs').value;
    document.getElementById('modal-nombre-produits-defaut').textContent = document.getElementById('nombre-produits-defaut').value;
    
    const produitsActifsMin = document.getElementById('produits-actifs-min').value;
    const produitsActifsMax = document.getElementById('produits-actifs-max').value;
    document.getElementById('modal-produits-actifs').textContent = `${produitsActifsMin} - ${produitsActifsMax}`;
    
    // Section 2: Configuration des Entités
    const budgetEntrepriseMin = document.getElementById('budget-entreprise-min').value;
    const budgetEntrepriseMax = document.getElementById('budget-entreprise-max').value;
    document.getElementById('modal-budget-entreprise').textContent = `${budgetEntrepriseMin}€ - ${budgetEntrepriseMax}€`;
    
    const prixProduitMin = document.getElementById('prix-produit-min').value;
    const prixProduitMax = document.getElementById('prix-produit-max').value;
    document.getElementById('modal-prix-produit').textContent = `${prixProduitMin}€ - ${prixProduitMax}€`;
    
    document.getElementById('modal-stock-initial').textContent = document.getElementById('stock-initial').value;
    document.getElementById('modal-budget-initial').textContent = document.getElementById('budget-initial').value + '€';
    
    // Section 3: Simulation par Tour
    document.getElementById('modal-n-entreprises').textContent = document.getElementById('n-entreprises').value;
    document.getElementById('modal-prob-selection').textContent = document.getElementById('prob-selection').value + '%';
    document.getElementById('modal-duree-pause').textContent = document.getElementById('duree-pause').value + 'ms';
    document.getElementById('modal-tick-interval-event').textContent = document.getElementById('tick-interval-event').value;
    
    const qteAchatMin = document.getElementById('qte-achat-min').value;
    const qteAchatMax = document.getElementById('qte-achat-max').value;
    document.getElementById('modal-qte-achat').textContent = `${qteAchatMin} - ${qteAchatMax}`;
    
    document.getElementById('modal-seuil-prix-eleve').textContent = document.getElementById('seuil-prix-eleve').value + '€';
    
    // Section 4: Événements
    fillModalEvents();
    
    // Monitoring
    document.getElementById('modal-metrics-collection-interval').textContent = document.getElementById('metrics-collection-interval').value + 's';
    document.getElementById('modal-metrics-system-enabled').textContent = document.getElementById('metrics-system-enabled').checked ? 'Activé' : 'Désactivé';
    document.getElementById('modal-log-level').textContent = document.getElementById('log-level').value;
}

/**
 * Remplit la section événements de la modal
 * Affiche les événements activés et leurs paramètres
 */
function fillModalEvents() {
    // Événements activés
    const eventsEnabled = [];
    if (document.getElementById('enable-inflation').checked) eventsEnabled.push('Inflation');
    if (document.getElementById('enable-recharge-budget').checked) eventsEnabled.push('Recharge Budget');
    if (document.getElementById('enable-reassort').checked) eventsEnabled.push('Réassort');
    if (document.getElementById('enable-variation-dispo').checked) eventsEnabled.push('Variation Disponibilité');
    
    document.getElementById('modal-events-enabled').innerHTML = eventsEnabled.length > 0 ? 
        eventsEnabled.map(event => `<span class="badge bg-success me-1">${event}</span>`).join('') : 
        '<span class="badge bg-secondary">Aucun événement activé</span>';
    
    // Paramètres d'événements
    const rechargeBudgetMin = document.getElementById('recharge-budget-min').value;
    const rechargeBudgetMax = document.getElementById('recharge-budget-max').value;
    document.getElementById('modal-recharge-budget').textContent = `${rechargeBudgetMin}€ - ${rechargeBudgetMax}€`;
    
    const reassortMin = document.getElementById('reassort-quantite-min').value;
    const reassortMax = document.getElementById('reassort-quantite-max').value;
    document.getElementById('modal-reassort').textContent = `${reassortMin} - ${reassortMax} unités`;
    
    // Paramètres d'inflation
    const inflationMin = document.getElementById('inflation-pourcentage-min').value;
    const inflationMax = document.getElementById('inflation-pourcentage-max').value;
    document.getElementById('modal-inflation').textContent = `${inflationMin}% - ${inflationMax}%`;
    
    const penaliteInflation = document.getElementById('penalite-inflation').value;
    const dureePenalite = document.getElementById('duree-penalite-inflation').value;
    document.getElementById('modal-penalite-inflation').textContent = `${penaliteInflation}% (${dureePenalite} tours)`;
    
    // Probabilités
    const probabilities = [
        `Recharge Budget: ${document.getElementById('prob-recharge-budget').value}%`,
        `Réassort: ${document.getElementById('prob-reassort').value}%`,
        `Inflation: ${document.getElementById('prob-inflation').value}%`,
        `Variation Disponibilité: ${document.getElementById('prob-variation-dispo').value}%`
    ];
    document.getElementById('modal-probabilities').innerHTML = probabilities.map(prob => 
        `<span class="badge bg-info me-1">${prob}</span>`
    ).join('');
}

/**
 * Confirme la configuration et lance la partie
 * Ferme la modal et démarre la simulation
 */
async function confirmAndStartGame() {
    // Fermer la modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('configModal'));
    modal.hide();
    
    // Rediriger vers l'onglet "Jeu"
    showPage('game');
    
    // Lancer la simulation avec la nouvelle fonction
    await launchSimulation();
}

// ===== MODIFICATION DE LA FONCTION STARTGAME =====

/**
 * Fonction startGame modifiée pour afficher la modal de confirmation
 * Au lieu de lancer directement, affiche d'abord la modal
 */
function startGameWithConfirmation() {
    showConfigModal();
}

// Export des fonctions
window.showPage = showPage;
window.saveTemplate = saveTemplate;
window.loadTemplate = loadTemplate;
window.startGame = startGameWithConfirmation; // Utilise maintenant la version avec confirmation
window.clearEvents = clearEvents;
window.toggleAutoScroll = toggleAutoScroll;
window.showConfigModal = showConfigModal;
window.confirmAndStartGame = confirmAndStartGame;
window.launchSimulation = launchSimulation;
window.connectWebSocket = connectWebSocket;
window.updateGameInfo = updateGameInfo;
window.addEventToLog = addEventToLog;
window.displayTourTimeline4CC = displayTourTimeline4CC;

window.showError = showError;
window.showSuccess = showSuccess;
