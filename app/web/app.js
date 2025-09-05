const { useState, useEffect, useRef } = React;

// Composant principal de l'application
function TradeSimApp() {
    const [config, setConfig] = useState({});
    const [metrics, setMetrics] = useState({});
    const [isConnected, setIsConnected] = useState(false);
    const [logs, setLogs] = useState([]);
    const [simulationRunning, setSimulationRunning] = useState(false);
    const wsRef = useRef(null);

    // Configuration de la simulation
    const [simulationConfig, setSimulationConfig] = useState({
        tours: 10,
        verbose: false,
        withMetrics: true
    });

    // Connexion WebSocket
    useEffect(() => {
        const connectWebSocket = () => {
            const ws = new WebSocket('ws://localhost:8000/ws');
            wsRef.current = ws;

            ws.onopen = () => {
                setIsConnected(true);
                addLog('🔗 Connexion WebSocket établie');
                ws.send(JSON.stringify({ type: 'subscribe' }));
            };

            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                handleWebSocketMessage(message);
            };

            ws.onclose = () => {
                setIsConnected(false);
                addLog('❌ Connexion WebSocket fermée');
                // Reconnexion automatique après 3 secondes
                setTimeout(connectWebSocket, 3000);
            };

            ws.onerror = (error) => {
                addLog(`❌ Erreur WebSocket: ${error}`);
            };
        };

        connectWebSocket();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    // Chargement initial des données
    useEffect(() => {
        loadConfig();
        loadMetrics();
    }, []);

    const addLog = (message) => {
        const timestamp = new Date().toLocaleTimeString();
        setLogs(prev => [...prev.slice(-49), `${timestamp} - ${message}`]);
    };

    const handleWebSocketMessage = (message) => {
        switch (message.type) {
            case 'subscribed':
                addLog('✅ Abonnement aux mises à jour activé');
                break;
            case 'simulation_completed':
                addLog(`🎯 Simulation terminée: ${message.tours} tours`);
                setSimulationRunning(false);
                loadMetrics();
                break;
            case 'simulation_error':
                addLog(`❌ Erreur simulation: ${message.error}`);
                setSimulationRunning(false);
                break;
            default:
                addLog(`📨 Message reçu: ${JSON.stringify(message)}`);
        }
    };

    const loadConfig = async () => {
        try {
            const response = await fetch('/config');
            const data = await response.json();
            if (data.status === 'success') {
                setConfig(data.config);
                addLog('📋 Configuration chargée');
            }
        } catch (error) {
            addLog(`❌ Erreur chargement config: ${error.message}`);
        }
    };

    const loadMetrics = async () => {
        try {
            const response = await fetch('/metrics');
            const data = await response.json();
            if (data.status === 'success') {
                setMetrics(data.metrics);
                addLog('📊 Métriques mises à jour');
            }
        } catch (error) {
            addLog(`❌ Erreur chargement métriques: ${error.message}`);
        }
    };

    const runSimulation = async () => {
        setSimulationRunning(true);
        addLog(`🚀 Lancement simulation: ${simulationConfig.tours} tours`);
        
        try {
            const response = await fetch('/simulation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(simulationConfig)
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                addLog('✅ Simulation lancée avec succès');
            } else {
                addLog(`❌ Erreur simulation: ${data.detail}`);
                setSimulationRunning(false);
            }
        } catch (error) {
            addLog(`❌ Erreur simulation: ${error.message}`);
            setSimulationRunning(false);
        }
    };

    const updateConfig = async (key, value) => {
        try {
            const response = await fetch('/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ key, value })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                addLog(`⚙️ Configuration ${key} mise à jour`);
                loadConfig();
            }
        } catch (error) {
            addLog(`❌ Erreur mise à jour config: ${error.message}`);
        }
    };

    return (
        <div className="container-fluid">
            {/* Header */}
            <nav className="navbar navbar-dark bg-dark mb-4">
                <div className="container-fluid">
                    <span className="navbar-brand mb-0 h1">
                        <i className="fas fa-chart-line me-2"></i>
                        TradeSim - Interface Web
                    </span>
                    <div className="d-flex align-items-center">
                        <span className={`status-indicator ${isConnected ? 'status-online' : 'status-offline'}`}></span>
                        <span className="text-light">
                            {isConnected ? 'Connecté' : 'Déconnecté'}
                        </span>
                    </div>
                </div>
            </nav>

            <div className="row">
                {/* Configuration */}
                <div className="col-md-4">
                    <div className="config-section">
                        <h4><i className="fas fa-cog me-2"></i>Configuration</h4>
                        
                        <div className="mb-3">
                            <label className="form-label">Nombre de tours</label>
                            <input
                                type="number"
                                className="form-control"
                                value={simulationConfig.tours}
                                onChange={(e) => setSimulationConfig({
                                    ...simulationConfig,
                                    tours: parseInt(e.target.value)
                                })}
                                min="1"
                                max="1000"
                            />
                        </div>

                        <div className="mb-3">
                            <div className="form-check">
                                <input
                                    className="form-check-input"
                                    type="checkbox"
                                    checked={simulationConfig.verbose}
                                    onChange={(e) => setSimulationConfig({
                                        ...simulationConfig,
                                        verbose: e.target.checked
                                    })}
                                />
                                <label className="form-check-label">
                                    Mode verbose
                                </label>
                            </div>
                        </div>

                        <div className="mb-3">
                            <div className="form-check">
                                <input
                                    className="form-check-input"
                                    type="checkbox"
                                    checked={simulationConfig.withMetrics}
                                    onChange={(e) => setSimulationConfig({
                                        ...simulationConfig,
                                        withMetrics: e.target.checked
                                    })}
                                />
                                <label className="form-check-label">
                                    Avec métriques
                                </label>
                            </div>
                        </div>

                        <button
                            className="btn btn-primary w-100"
                            onClick={runSimulation}
                            disabled={simulationRunning}
                        >
                            {simulationRunning ? (
                                <>
                                    <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                                    Simulation en cours...
                                </>
                            ) : (
                                <>
                                    <i className="fas fa-play me-2"></i>
                                    Lancer la simulation
                                </>
                            )}
                        </button>
                    </div>

                    {/* Métriques */}
                    <div className="config-section">
                        <h4><i className="fas fa-chart-bar me-2"></i>Métriques</h4>
                        
                        <div className="metric-card">
                            <div className="d-flex justify-content-between">
                                <span>Tours complétés</span>
                                <strong>{metrics.tours_completes || 0}</strong>
                            </div>
                        </div>

                        <div className="metric-card">
                            <div className="d-flex justify-content-between">
                                <span>Entreprises actives</span>
                                <strong>{metrics.entreprises_actives || 0}</strong>
                            </div>
                        </div>

                        <div className="metric-card">
                            <div className="d-flex justify-content-between">
                                <span>Produits actifs</span>
                                <strong>{metrics.produits_actifs || 0}</strong>
                            </div>
                        </div>

                        <div className="metric-card">
                            <div className="d-flex justify-content-between">
                                <span>Fournisseurs actifs</span>
                                <strong>{metrics.fournisseurs_actifs || 0}</strong>
                            </div>
                        </div>

                        <button
                            className="btn btn-outline-secondary w-100 mt-2"
                            onClick={loadMetrics}
                        >
                            <i className="fas fa-sync-alt me-2"></i>
                            Actualiser
                        </button>
                    </div>
                </div>

                {/* Logs */}
                <div className="col-md-8">
                    <div className="config-section">
                        <h4><i className="fas fa-terminal me-2"></i>Logs en temps réel</h4>
                        <div className="log-container">
                            {logs.map((log, index) => (
                                <div key={index}>{log}</div>
                            ))}
                        </div>
                        <button
                            className="btn btn-outline-secondary btn-sm mt-2"
                            onClick={() => setLogs([])}
                        >
                            <i className="fas fa-trash me-2"></i>
                            Vider les logs
                        </button>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <footer className="mt-5 py-3 bg-light text-center">
                <small className="text-muted">
                    TradeSim v2.0.0 - Interface Web | 
                    <a href="http://localhost:3000" target="_blank" className="ms-2">
                        <i className="fas fa-external-link-alt me-1"></i>
                        Grafana
                    </a>
                </small>
            </footer>
        </div>
    );
}

// Rendu de l'application
ReactDOM.render(<TradeSimApp />, document.getElementById('root'));
