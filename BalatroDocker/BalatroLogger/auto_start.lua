
-- Auto Start Game Mod - Super Simple with Lovely Logs
--
-- STARTUP OPTION CONFIGURATION:
-- This mod reads a JSON file from /tmp/balatro_auto_start.json to start a game
-- with specific configuration. The available options are:
--
-- MAIN OPTIONS:
-- • auto_start (boolean): If true, automatically starts the game
--
-- GAME CONFIGURATION OPTIONS:
-- • deck (string): The deck to use. Valid values include:
--   - "b_red"      - Red Deck (default)
--   - "b_blue"     - Blue Deck
--   - "b_yellow"   - Yellow Deck
--   - "b_green"    - Green Deck
--   - "b_black"    - Black Deck
--   - "b_magic"    - Magic Deck
--   - "b_nebula"   - Nebula Deck
--   - "b_ghost"    - Ghost Deck
--   - "b_abandoned"- Abandoned Deck
--   - "b_checkered"- Checkered Deck
--   - "b_zodiac"   - Zodiac Deck
--   - "b_painted"  - Painted Deck
--   - "b_anaglyph" - Anaglyph Deck
--   - "b_plasma"   - Plasma Deck
--   - "b_erratic"  - Erratic Deck
--   (Note: Only unlocked decks will work)
--
-- • stake (number): The difficulty/stake level. Valid values:
--   - 1 = White Stake (easiest)
--   - 2 = Red Stake
--   - 3 = Green Stake
--   - 4 = Black Stake
--   - 5 = Blue Stake
--   - 6 = Purple Stake
--   - 7 = Orange Stake
--   - 8 = Gold Stake (hardest)
--   (Note: Only unlocked stakes will work)
--
-- • seed (string): Seed to generate the game deterministically
--   - Any text works as a seed
--   - "random" or null/undefined = random seed
--   - Using the same seed will produce the same sequence of cards/events

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
