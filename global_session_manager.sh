#!/bin/bash

# Global Session Manager per Background Agent
# Può essere utilizzato da qualsiasi directory
# Cerca automaticamente il progetto crypto-futures-llm-trading

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funzione per trovare il progetto
find_project() {
    local current_dir="$PWD"
    local search_dir="$current_dir"
    
    # Cerca salendo nella gerarchia delle directory
    while [ "$search_dir" != "/" ]; do
        if [ -f "$search_dir/background_agent.py" ] && [ -f "$search_dir/manage_background_agent.sh" ]; then
            echo "$search_dir"
            return 0
        fi
        search_dir=$(dirname "$search_dir")
    done
    
    # Se non trovato, cerca in directory comuni
    local common_paths=(
        "$HOME/Development/crypto-futures-llm-trading"
        "$HOME/crypto-futures-llm-trading"
        "/opt/crypto-futures-llm-trading"
        "/usr/local/crypto-futures-llm-trading"
    )
    
    for path in "${common_paths[@]}"; do
        if [ -f "$path/background_agent.py" ] && [ -f "$path/manage_background_agent.sh" ]; then
            echo "$path"
            return 0
        fi
    done
    
    return 1
}

# Funzione per ottenere il percorso del progetto
get_project_path() {
    local project_path=$(find_project)
    if [ $? -eq 0 ]; then
        echo "$project_path"
    else
        echo ""
    fi
}

# Funzione per verificare se siamo nel progetto
check_project() {
    local project_path=$(get_project_path)
    if [ -z "$project_path" ]; then
        echo -e "${RED}❌ Progetto crypto-futures-llm-trading non trovato${NC}"
        echo ""
        echo -e "${YELLOW}💡 Cerca in:${NC}"
        echo "   - Directory corrente e parent"
        echo "   - $HOME/Development/crypto-futures-llm-trading"
        echo "   - $HOME/crypto-futures-llm-trading"
        echo "   - /opt/crypto-futures-llm-trading"
        echo "   - /usr/local/crypto-futures-llm-trading"
        echo ""
        echo -e "${BLUE}🔧 Soluzioni:${NC}"
        echo "   1. Vai nella directory del progetto"
        echo "   2. Usa: $0 --project-path /path/to/project"
        echo "   3. Crea un link simbolico: ln -s /path/to/project ~/crypto-futures-llm-trading"
        return 1
    fi
    return 0
}

# Funzione per eseguire comando nel progetto
run_in_project() {
    local project_path="$1"
    local command="$2"
    
    if [ -z "$project_path" ]; then
        project_path=$(get_project_path)
        if [ -z "$project_path" ]; then
            echo -e "${RED}❌ Progetto non trovato${NC}"
            return 1
        fi
    fi
    
    # Vai nella directory del progetto
    cd "$project_path"
    
    # Esegui il comando
    if [ -f "session_manager.sh" ]; then
        ./session_manager.sh "$command"
    else
        echo -e "${RED}❌ session_manager.sh non trovato in $project_path${NC}"
        return 1
    fi
}

# Funzione per mostrare aiuto
show_help() {
    echo -e "${BLUE}🌍 Global Session Manager per Background Agent${NC}"
    echo ""
    echo "Uso: $0 [opzioni] [comando] [session_id]"
    echo ""
    echo "Opzioni:"
    echo -e "  ${CYAN}--project-path PATH${NC} - Specifica il percorso del progetto"
    echo -e "  ${CYAN}--find${NC}              - Trova e mostra il percorso del progetto"
    echo -e "  ${CYAN}--help${NC}              - Mostra questo aiuto"
    echo ""
    echo "Comandi disponibili:"
    echo -e "  ${GREEN}start [id]${NC}   - Avvia sessione controllata"
    echo -e "  ${YELLOW}join [id]${NC}    - Unisciti a sessione esistente"
    echo -e "  ${RED}stop [id]${NC}     - Ferma sessione controllata"
    echo -e "  ${PURPLE}status${NC}     - Mostra stato sessioni"
    echo -e "  ${CYAN}cleanup${NC}     - Pulizia completa"
    echo -e "  ${BLUE}logs${NC}        - Mostra log sessione"
    echo ""
    echo "Esempi:"
    echo "  $0 start my_session"
    echo "  $0 --project-path /path/to/project start my_session"
    echo "  $0 status"
    echo "  $0 --find"
    echo ""
    echo "Note:"
    echo "  - Cerca automaticamente il progetto nella gerarchia delle directory"
    echo "  - Può essere usato da qualsiasi directory"
    echo "  - Usa --project-path per specificare un percorso personalizzato"
}

# Funzione per trovare e mostrare il progetto
find_and_show_project() {
    echo -e "${BLUE}🔍 Ricerca Progetto crypto-futures-llm-trading${NC}"
    echo ""
    
    local project_path=$(get_project_path)
    if [ -n "$project_path" ]; then
        echo -e "${GREEN}✅ Progetto trovato:${NC}"
        echo -e "   📁 $project_path"
        echo ""
        
        # Mostra informazioni sul progetto
        if [ -f "$project_path/background_agent.py" ]; then
            echo -e "${GREEN}✅ File principali trovati:${NC}"
            ls -la "$project_path"/*.py "$project_path"/*.sh 2>/dev/null | grep -E "(background_agent|session_manager|manage_background)" || echo "   Nessun file di gestione trovato"
        fi
        
        # Controlla se c'è un processo attivo
        local active_count=$(ps aux | grep "python background_agent.py" | grep -v grep | wc -l)
        echo ""
        echo -e "${BLUE}📊 Stato attuale:${NC}"
        echo -e "   🔄 Processi attivi: $active_count"
        
        if [ $active_count -gt 0 ]; then
            echo -e "   📍 Directory processo: $(ps aux | grep "python background_agent.py" | grep -v grep | awk '{print $11}' | head -1)"
        fi
    else
        echo -e "${RED}❌ Progetto non trovato${NC}"
        echo ""
        echo -e "${YELLOW}💡 Cerca in:${NC}"
        echo "   - Directory corrente: $PWD"
        echo "   - Directory parent"
        echo "   - $HOME/Development/crypto-futures-llm-trading"
        echo "   - $HOME/crypto-futures-llm-trading"
        echo "   - /opt/crypto-futures-llm-trading"
        echo "   - /usr/local/crypto-futures-llm-trading"
    fi
}

# Parsing degli argomenti
PROJECT_PATH=""
COMMAND=""
SESSION_ID=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --project-path)
            PROJECT_PATH="$2"
            shift 2
            ;;
        --find)
            find_and_show_project
            exit 0
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        start|join|stop|status|cleanup|logs)
            COMMAND="$1"
            shift
            if [[ $# -gt 0 ]] && [[ $1 != --* ]]; then
                SESSION_ID="$1"
                shift
            fi
            break
            ;;
        *)
            echo -e "${RED}❌ Argomento sconosciuto: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
done

# Se non è stato specificato un comando, mostra aiuto
if [ -z "$COMMAND" ]; then
    show_help
    exit 0
fi

# Esegui il comando
if [ -n "$PROJECT_PATH" ]; then
    # Usa il percorso specificato
    if [ ! -f "$PROJECT_PATH/background_agent.py" ]; then
        echo -e "${RED}❌ Percorso non valido: $PROJECT_PATH${NC}"
        echo -e "${YELLOW}💡 Il percorso deve contenere background_agent.py${NC}"
        exit 1
    fi
    run_in_project "$PROJECT_PATH" "$COMMAND $SESSION_ID"
else
    # Cerca automaticamente il progetto
    if ! check_project; then
        exit 1
    fi
    run_in_project "" "$COMMAND $SESSION_ID"
fi 