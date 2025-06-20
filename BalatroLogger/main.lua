local MOD    = SMODS.current_mod
local PFX    = MOD.prefix or "VPT"

sendInfoMessage(PFX .. " Mod cargado correctamente!")

-- Función para forzar modo controlador
local function force_controller_mode()
    sendInfoMessage(PFX .. " Forzando modo controlador...")
    
    if G and G.SETTINGS then
        -- Forzar configuración de controlador
        G.SETTINGS.paused = false
        G.SETTINGS.GRAPHICS = G.SETTINGS.GRAPHICS or {}
        G.SETTINGS.GRAPHICS.gamepad_cursor = true  -- Habilitar cursor de gamepad
        
        sendInfoMessage(PFX .. " Configuración de controlador aplicada!")
        
        -- Si existe la configuración de input method, cambiarla
        if G.CONTROLLER then
            G.CONTROLLER.HID.axis = {}  -- Reset axis
            G.CONTROLLER.HID.button = {}  -- Reset buttons
            sendInfoMessage(PFX .. " Controlador reseteado!")
        end
    end
end

-- Función helper para simular un botón completo (presión + liberación)
local function simulate_button_press(button, hold_time)
    hold_time = hold_time or 0.1
    
    sendInfoMessage(PFX .. " Iniciando simulación del botón: " .. button)
    
    if not G or not G.CONTROLLER then
        sendInfoMessage(PFX .. " ERROR: G.CONTROLLER no disponible!")
        return
    end

    -- Forzar modo controlador antes de simular
    force_controller_mode()

    -- Presionar el botón
    G.CONTROLLER:button_press(button)
    sendInfoMessage(PFX .. " Botón presionado: " .. button)
    
    -- Programar la liberación
    G.E_MANAGER:add_event(Event({
        trigger = 'after',
        delay = hold_time,
        func = function()
            G.CONTROLLER:button_release(button)
            sendInfoMessage(PFX .. " Botón liberado: " .. button)
            return true
        end
    }))
end

-- Hook para inicialización del juego
local old_love_load = love.load or function() end
function love.load(...)
    sendInfoMessage(PFX .. " love.load interceptado!")
    
    -- Llamar función original
    old_love_load(...)
    
    -- Forzar modo controlador después de cargar
    G.E_MANAGER:add_event(Event({
        trigger = 'after',
        delay = 1.0,  -- Esperar un poco después de cargar
        func = function()
            force_controller_mode()
            return true
        end
    }))
end

-- Verificar que love.keypressed existe
if love.keypressed then
    sendInfoMessage(PFX .. " love.keypressed ya existe, extendiendo...")
else
    sendInfoMessage(PFX .. " love.keypressed no existe, creando nueva...")
end

-- Guardar la función original y extenderla
local old_keypressed = love.keypressed or function() end
function love.keypressed(key, sc, rep)
    sendInfoMessage(PFX .. " love.keypressed llamada con key: " .. tostring(key))
    
    -- Llamar primero a la función original
    old_keypressed(key, sc, rep)
    
    -- Mapeo de teclas a botones del controlador
    local key_to_button = {
        ["return"] = "a",
        ["escape"] = "b", 
        ["space"] = "x",
        ["tab"] = "y",
        ["up"] = "up",
        ["down"] = "down",
        ["left"] = "left", 
        ["right"] = "right",
        ["q"] = "leftshoulder",
        ["e"] = "rightshoulder",
        ["1"] = "lefttrigger", 
        ["2"] = "righttrigger",
        ["p"] = "start"
    }
    
    local button = key_to_button[key]
    if button then
        sendInfoMessage(PFX .. " Tecla " .. key .. " mapeada a botón " .. button)
        simulate_button_press(button)
    end
end

sendInfoMessage(PFX .. " Hook de love.keypressed instalado!")