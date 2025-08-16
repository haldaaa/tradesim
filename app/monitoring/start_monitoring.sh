#!/bin/bash
# Script de démarrage modulaire du monitoring TradeSim
# ====================================================
#
# ARCHITECTURE :
# - Détection automatique du host Docker
# - Démarrage des services de monitoring
# - Configuration automatique de Prometheus
# - Validation de la connectivité
#
# FONCTIONNEMENT :
# 1. Détection automatique de la plateforme
# 2. Configuration du host Docker approprié
# 3. Démarrage des containers Docker
# 4. Configuration de Prometheus
# 5. Validation des services
#
# UTILISATION :
# - Exécution : ./start_monitoring.sh
# - Arrêt : ./stop_monitoring.sh
# - Status : ./status_monitoring.sh
#
# AUTEUR : Assistant IA
# DERNIÈRE MISE À JOUR : 16/08/2025

# ============================================================================
# FONCTIONS DE LOGGING
# ============================================================================

log_message() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [MONITORING] $message"
    
    # Log dans le fichier monitoring.log
    echo "[$timestamp] [MONITORING] $message" >> logs/monitoring.log 2>/dev/null || true
}

# ============================================================================
# DÉTECTION ET CONFIGURATION
# ============================================================================

setup_docker_host() {
    log_message "Configuration du host Docker"
    
    # Exécuter le script de détection
    source ./monitoring/detect_docker_host.sh
    
    if [ -z "$TRADESIM_DOCKER_HOST" ]; then
        log_message "ERREUR : Impossible de détecter le host Docker"
        return 1
    fi
    
    log_message "Host Docker configuré : $TRADESIM_DOCKER_HOST"
    return 0
}

# ============================================================================
# CONFIGURATION DE PROMETHEUS
# ============================================================================

configure_prometheus() {
    local docker_host="$1"
    local config_file="monitoring/prometheus.yml"
    
    log_message "Configuration de Prometheus avec host : $docker_host"
    
    # Sauvegarder la configuration originale
    cp "$config_file" "${config_file}.backup" 2>/dev/null || true
    
    # Mettre à jour la configuration
    sed -i.bak "s/targets: \['.*:8000'\]/targets: ['${docker_host}:8000']/" "$config_file"
    
    if [ $? -eq 0 ]; then
        log_message "Configuration Prometheus mise à jour : target=${docker_host}:8000"
        return 0
    else
        log_message "ERREUR : Impossible de mettre à jour la configuration Prometheus"
        return 1
    fi
}

# ============================================================================
# DÉMARRAGE DES SERVICES
# ============================================================================

start_docker_services() {
    log_message "Démarrage des services Docker"
    
    # Arrêter les services existants
    docker-compose -f monitoring/docker-compose.yml down 2>/dev/null || true
    
    # Démarrer les services
    if docker-compose -f monitoring/docker-compose.yml up -d; then
        log_message "Services Docker démarrés avec succès"
        return 0
    else
        log_message "ERREUR : Impossible de démarrer les services Docker"
        return 1
    fi
}

# ============================================================================
# VALIDATION DES SERVICES
# ============================================================================

validate_services() {
    log_message "Validation des services"
    
    # Attendre que les services démarrent
    sleep 10
    
    # Vérifier Prometheus
    if curl -s http://localhost:9090/api/v1/status/targets >/dev/null 2>&1; then
        log_message "Prometheus accessible sur http://localhost:9090"
    else
        log_message "ATTENTION : Prometheus non accessible"
    fi
    
    # Vérifier Grafana
    if curl -s http://localhost:3000/api/health >/dev/null 2>&1; then
        log_message "Grafana accessible sur http://localhost:3000"
    else
        log_message "ATTENTION : Grafana non accessible"
    fi
    
    # Vérifier l'exporteur
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        log_message "Exporteur Prometheus accessible sur http://localhost:8000"
    else
        log_message "ATTENTION : Exporteur Prometheus non accessible"
    fi
}

# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

main() {
    log_message "Démarrage du monitoring TradeSim"
    
    # Créer le dossier logs s'il n'existe pas
    mkdir -p logs 2>/dev/null || true
    
    # Configuration du host Docker
    if ! setup_docker_host; then
        log_message "ERREUR : Échec de la configuration du host Docker"
        exit 1
    fi
    
    # Configuration de Prometheus
    if ! configure_prometheus "$TRADESIM_DOCKER_HOST"; then
        log_message "ERREUR : Échec de la configuration de Prometheus"
        exit 1
    fi
    
    # Démarrage des services
    if ! start_docker_services; then
        log_message "ERREUR : Échec du démarrage des services"
        exit 1
    fi
    
    # Validation des services
    validate_services
    
    log_message "Monitoring démarré avec succès"
    echo ""
    echo "📊 Monitoring TradeSim démarré !"
    echo "   Prometheus : http://localhost:9090"
    echo "   Grafana    : http://localhost:3000 (admin/admin)"
    echo "   Exporteur  : http://localhost:8000"
    echo ""
    
    return 0
}

# ============================================================================
# EXÉCUTION
# ============================================================================

main "$@"
