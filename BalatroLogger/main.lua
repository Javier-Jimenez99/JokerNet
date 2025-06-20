--- VirtualPadTest · main.lua
local MOD    = SMODS.current_mod
local PFX    = MOD.prefix or "VPT"

-- Empuja el botón A cuando pulses P
local old_key = love.keypressed or function() end
function love.keypressed(key, sc, rep)
  local joy = G.CONTROLLER and G.CONTROLLER.joystick or love.joystick.getJoysticks()[1]

  if joy then
    sendInfoMessage("Joystick virtual detectado: "..joy:getName(), PFX)
  else
    sendInfoMessage("¡No se encontró joystick virtual!", PFX)
  end
  old_key(key, sc, rep)
  if key == "p" and joy then
    love.event.push("gamepadpressed",  joy, "a")
    love.event.push("gamepadreleased", joy, "a")
    sendInfoMessage("Inyectado botón A mediante joystick virtual", PFX)
  end
end
