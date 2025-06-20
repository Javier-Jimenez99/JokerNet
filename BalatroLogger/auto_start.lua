-- Auto Start Game Mod - Super Simple with Lovely Logs
--
-- CONFIGURACIÓN DE OPCIONES DE INICIO:
-- Este mod lee un archivo JSON desde /tmp/balatro_auto_start.json para iniciar una partida
-- con configuración específica. Las opciones disponibles son:
--
-- OPCIONES PRINCIPALES:
-- • auto_start (boolean): Si es true, inicia automáticamente la partida
--
-- OPCIONES DE CONFIGURACIÓN DE PARTIDA:
-- • deck (string): El mazo a usar. Valores válidos incluyen:
--   - "b_red"      - Mazo Rojo (predeterminado)
--   - "b_blue"     - Mazo Azul  
--   - "b_yellow"   - Mazo Amarillo
--   - "b_green"    - Mazo Verde
--   - "b_black"    - Mazo Negro
--   - "b_magic"    - Mazo Mágico
--   - "b_nebula"   - Mazo Nebulosa
--   - "b_ghost"    - Mazo Fantasma
--   - "b_abandoned"- Mazo Abandonado
--   - "b_checkered"- Mazo A Cuadros
--   - "b_zodiac"   - Mazo Zodíaco
--   - "b_painted"  - Mazo Pintado
--   - "b_anaglyph" - Mazo Anaglifo
--   - "b_plasma"   - Mazo Plasma
--   - "b_erratic"  - Mazo Errático
--   (Nota: Solo funcionarán mazos desbloqueados)
--
-- • stake (number): El nivel de dificultad/apuesta. Valores válidos:
--   - 1 = Apuesta Blanca (más fácil)
--   - 2 = Apuesta Roja
--   - 3 = Apuesta Verde  
--   - 4 = Apuesta Negra
--   - 5 = Apuesta Azul
--   - 6 = Apuesta Púrpura
--   - 7 = Apuesta Naranja
--   - 8 = Apuesta Dorada (más difícil)
--   (Nota: Solo funcionarán apuestas desbloqueadas)
--
-- • seed (string): Semilla para generar la partida de forma determinística
--   - Cualquier texto funciona como semilla
--   - "random" o null/undefined = semilla aleatoria
--   - Usar la misma semilla producirá la misma secuencia de cartas/eventos
--
-- EJEMPLOS DE USO:
-- ================
--
-- 1. INICIAR CON CONFIGURACIÓN BÁSICA:
--    curl -X POST http://localhost:8000/auto_start \
--      -H "Content-Type: application/json" \
--      -d '{"auto_start": true}'
--
-- 2. INICIAR CON MAZO ESPECÍFICO:
--    curl -X POST http://localhost:8000/auto_start \
--      -H "Content-Type: application/json" \
--      -d '{"auto_start": true, "deck": "b_blue"}'
--
-- 3. INICIAR CON CONFIGURACIÓN COMPLETA:
--    curl -X POST http://localhost:8000/auto_start \
--      -H "Content-Type: application/json" \
--      -d '{"auto_start": true, "deck": "b_magic", "stake": 5, "seed": "MYSTICAL2024"}'
--
-- 4. INICIAR CON SEMILLA ALEATORIA:
--    curl -X POST http://localhost:8000/auto_start \
--      -H "Content-Type: application/json" \
--      -d '{"auto_start": true, "deck": "b_nebula", "stake": 2, "seed": "random"}'
--
-- VERIFICAR ESTADO DEL MOD:
-- =========================
-- curl http://localhost:8000/mod_status
--
-- ESTRUCTURA DEL ARCHIVO JSON COMPLETA:
-- ====================================
-- {
--   "auto_start": true,                    // REQUERIDO: activar auto-inicio
--   "deck": "b_blue",                      // OPCIONAL: ID del mazo
--   "stake": 3,                            // OPCIONAL: nivel de apuesta 1-8
--   "seed": "mi_semilla_personalizada"     // OPCIONAL: semilla o "random"
-- }
--
-- NOTAS IMPORTANTES:
-- ==================
-- • El archivo se elimina automáticamente después de leerlo
-- • Solo funciona cuando el juego está en el menú principal
-- • Las opciones inválidas se ignoran (usa valores predeterminados)
-- • El estado del mod se escribe en /tmp/balatro_mod_status.json
-- • Todos los pasos se registran en los logs de Lovely para debugging
-- • Solo funcionan mazos y apuestas que ya estén desbloqueados en el juego

-- Parse JSON and extract config
local function read_config()
    local file = io.open("/tmp/balatro_auto_start.json", "r")
    if file then
        sendDebugMessage("[AUTO_START] Config file found! Reading...")
        
        local content = file:read("*all")
        file:close()
        
        sendDebugMessage("[AUTO_START] File content: " .. content)
        sendDebugMessage("[AUTO_START] Deleting config file...")
        os.remove("/tmp/balatro_auto_start.json")
        
        -- Parse JSON values
        local config = {}
        config.auto_start = content:find('"auto_start"%s*:%s*true') ~= nil
        config.deck = content:match('"deck"%s*:%s*"([^"]*)"')
        config.stake = tonumber(content:match('"stake"%s*:%s*(%d+)'))
        config.seed = content:match('"seed"%s*:%s*"([^"]*)"')
        
        sendDebugMessage("[AUTO_START] Parsed config:")
        sendDebugMessage("[AUTO_START]   auto_start: " .. tostring(config.auto_start))
        sendDebugMessage("[AUTO_START]   deck: " .. tostring(config.deck))
        sendDebugMessage("[AUTO_START]   stake: " .. tostring(config.stake))
        sendDebugMessage("[AUTO_START]   seed: " .. tostring(config.seed))
        
        return config
    end
    return nil
end

-- Write simple status
local function write_status(msg)
    sendDebugMessage("[AUTO_START] Writing status: " .. msg)
    
    local file = io.open("/tmp/balatro_mod_status.json", "w")
    if file then
        file:write('{"status":"' .. msg .. '"}')
        file:close()
        sendDebugMessage("[AUTO_START] Status written successfully")
    else
        sendDebugMessage("[AUTO_START] ERROR: Could not write status file")
    end
end

-- Main loop - check every frame
local original_update = love.update
love.update = function(dt)
    if original_update then original_update(dt) end
    
    -- Check for config
    local config = read_config()
    
    if config and config.auto_start then
        sendDebugMessage("[AUTO_START] Config says auto_start = true")
        
        if G then
            sendDebugMessage("[AUTO_START] G is available")
            
            -- Check if we're in main menu using G.STAGE
            if G.STAGE == G.STAGES.MAIN_MENU then
                sendDebugMessage("[AUTO_START] In MAIN_MENU stage - proceeding with start")
                
                -- Set deck if specified
                if config.deck and G.P_CENTERS[config.deck] then
                    sendDebugMessage("[AUTO_START] Setting deck to: " .. config.deck)
                    G.GAME.viewed_back = G.P_CENTERS[config.deck]
                    sendDebugMessage("[AUTO_START] Deck set successfully")
                end
                
                if G.FUNCS and G.FUNCS.start_run then
                    sendDebugMessage("[AUTO_START] G.FUNCS.start_run found - calling with parameters...")
                    
                    -- Prepare arguments
                    local args = {
                        stake = config.stake or 1,
                        seed = (config.seed and config.seed ~= "random") and config.seed or nil
                    }
                    
                    sendDebugMessage("[AUTO_START] start_run args:")
                    sendDebugMessage("[AUTO_START]   stake: " .. tostring(args.stake))
                    sendDebugMessage("[AUTO_START]   seed: " .. tostring(args.seed))
                    
                    G.FUNCS.start_run(nil, args)
                    sendDebugMessage("[AUTO_START] start_run called successfully with parameters!")
                    write_status("started")
                else
                    sendDebugMessage("[AUTO_START] ERROR: G.FUNCS.start_run not found")
                    write_status("error")
                end
            else
                sendDebugMessage("[AUTO_START] Not in MAIN_MENU stage - current stage: " .. tostring(G.STAGE))
            end
        else
            sendDebugMessage("[AUTO_START] G not available")
        end
    end
end

sendDebugMessage("[AUTO_START] === MOD INITIALIZED ===")
write_status("ready")
