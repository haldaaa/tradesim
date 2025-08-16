#!/bin/bash
# Script de détection automatique du host Docker pour TradeSim
# ===========================================================
#
# ARCHITECTURE :
# - Détection automatique de la plateforme d'exécution
# - Configuration modulaire de la connectivité Docker
# - Support des variables d'environnement
# - Fallback intelligent pour différentes configurations
#
# FONCTIONNEMENT :
# 1. Détection de la plateforme d'exécution (Linux, macOS, Windows)
# 2. Configuration automatique du host Docker approprié
# 3. Validation de la connectivité
# 4. Logging des résultats
#
# UTILISATION :
# - Exécution : ./detect_docker_host.sh
# - Variable : DOCKER_HOST sera configurée automatiquement
# - Override : export DOCKER_HOST=custom_host (avant exécution)
#
# AUTEUR : Assistant IA
# DERNIÈRE MISE À JOUR : 16/08/2025

# ============================================================================
# FONCTIONS DE LOGGING
# ============================================================================

log_message() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [SCRIPT] detect_docker_host : $message"
    
    # Log dans le fichier monitoring.log
    echo "[$timestamp] [SCRIPT] detect_docker_host : $message" >> logs/monitoring.log 2>/dev/null || true
}

# ============================================================================
# DÉTECTION DE LA PLATEFORME
# ============================================================================

detect_platform() {
    case "$OSTYPE" in
        darwin*)
            echo "macos"
            ;;
        linux-gnu*)
            echo "linux"
            ;;
        msys*|cygwin*)
            echo "windows"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# ============================================================================
# DÉTECTION DU HOST DOCKER
# ============================================================================

get_docker_host() {
    local platform="$1"
    
    case "$platform" in
        macos|windows)
            echo "host.docker.internal"
            ;;
        linux)
            get_linux_docker_host
            ;;
        *)
            echo "localhost"
            ;;
    esac
}

get_linux_docker_host() {
    # Essayer de récupérer l'IP du bridge Docker
    local bridge_ip=$(docker network inspect bridge --format '{{.IPAM.Config.0.Gateway}}' 2>/dev/null)
    
    if [ -n "$bridge_ip" ]; then
        echo "$bridge_ip"
        return
    fi
    
    # Fallback: utiliser l'IP de la route par défaut
    local default_ip=$(ip route show default | grep -oP 'via \K\S+' | head -1)
    
    if [ -n "$default_ip" ]; then
        echo "$default_ip"
        return
    fi
    
    # Fallback final
    echo "localhost"
}

# ============================================================================
# VALIDATION DE LA CONNECTIVITÉ
# ============================================================================

validate_connectivity() {
    local host="$1"
    local port="${2:-8000}"
    
    # Test de connectivité simple
    if timeout 5 bash -c "</dev/tcp/$host/$port" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

main() {
    log_message "Démarrage de la détection du host Docker"
    
    # Vérifier si Docker est disponible
    if ! command -v docker &> /dev/null; then
        log_message "ERREUR : Docker n'est pas installé ou n'est pas dans le PATH"
        exit 1
    fi
    
    # Détecter la plateforme
    local platform=$(detect_platform)
    log_message "Plateforme détectée : $platform"
    
    # Vérifier si une variable d'environnement est déjà définie
    if [ -n "$TRADESIM_DOCKER_HOST" ]; then
        log_message "Variable TRADESIM_DOCKER_HOST déjà définie : $TRADESIM_DOCKER_HOST"
        export TRADESIM_DOCKER_HOST
        log_message "script OK host détecté : $TRADESIM_DOCKER_HOST"
        return 0
    fi
    
    # Détecter le host approprié
    local detected_host=$(get_docker_host "$platform")
    log_message "Host Docker détecté : $detected_host"
    
    # Valider la connectivité (optionnel)
    if validate_connectivity "$detected_host" 8000; then
        log_message "Connectivité validée vers $detected_host:8000"
    else
        log_message "ATTENTION : Connectivité non validée vers $detected_host:8000 (l'exporteur peut ne pas être démarré)"
    fi
    
    # Exporter la variable (utiliser un nom différent pour éviter les conflits)
    export TRADESIM_DOCKER_HOST="$detected_host"
    log_message "script OK host détecté : $TRADESIM_DOCKER_HOST"
    
    return 0
}

# ============================================================================
# EXÉCUTION
# ============================================================================

# Créer le dossier logs s'il n'existe pas
mkdir -p logs 2>/dev/null || true

# Exécuter la fonction principale
main "$@"
