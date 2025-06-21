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

-- Parse JSON and extract config
local function read_config()
    local file = io.open("/tmp/balatro_auto_start.json", "r")
    if file then
        local content = file:read("*all")
        file:close()
        
        os.remove("/tmp/balatro_auto_start.json")
        
        -- Parse JSON values
        local config = {}
        config.auto_start = content:find('"auto_start"%s*:%s*true') ~= nil
        config.deck = content:match('"deck"%s*:%s*"([^"]*)"')
        config.stake = tonumber(content:match('"stake"%s*:%s*(%d+)'))
        config.seed = content:match('"seed"%s*:%s*"([^"]*)"')
        
        return config
    end
    return nil
end

-- Write simple status
local function write_status(msg)
    local file = io.open("/tmp/balatro_mod_status.json", "w")
    if file then
        file:write('{"status":"' .. msg .. '"}')
        file:close()
    end
end

-- Main loop - check every frame
local original_update = love.update
love.update = function(dt)
    if original_update then original_update(dt) end
    
    -- Check for config
    local config = read_config()
    
    if config and config.auto_start then
        if G then
            -- Set deck if specified
            if config.deck and G.P_CENTERS[config.deck] then
                G.GAME.viewed_back = G.P_CENTERS[config.deck]
            end
            
            if G.FUNCS and G.FUNCS.start_run then
                -- Prepare arguments
                local args = {
                    stake = config.stake or 1,
                    seed = (config.seed and config.seed ~= "random") and config.seed or nil
                }
                
                G.FUNCS.start_run(nil, args)
                write_status("started")
            else
                write_status("error")
            end
        end
    end
end

write_status("ready")
