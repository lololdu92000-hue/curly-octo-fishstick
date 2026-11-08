--[[
	RealisticCamera.client.lua
	Effets côté joueur pour un rendu "cinéma" :
	  • Mise au point automatique (le perso est net, le fond est flou)
	  • Exposition qui s'adapte quand on regarde le soleil / l'ombre
	  • Touche G : active / désactive le mode réaliste (pour les PC faibles)

	À placer dans : StarterPlayer > StarterPlayerScripts (LocalScript)
]]

local Players = game:GetService("Players")
local Lighting = game:GetService("Lighting")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local player = Players.LocalPlayer
local camera = workspace.CurrentCamera

local enabled = true
local baseExposure = Lighting.ExposureCompensation
local currentExposure = baseExposure

local function getEffect(name)
	return Lighting:FindFirstChild(name)
end

local EFFECT_NAMES = { "RG_Bloom", "RG_ColorCorrection", "RG_SunRays", "RG_DepthOfField" }

local function setEnabled(state)
	enabled = state
	for _, name in ipairs(EFFECT_NAMES) do
		local e = getEffect(name)
		if e then
			e.Enabled = state
		end
	end
	if not state then
		Lighting.ExposureCompensation = baseExposure
	end
end

UserInputService.InputBegan:Connect(function(input, processed)
	if processed then
		return
	end
	if input.KeyCode == Enum.KeyCode.G then
		setEnabled(not enabled)
	end
end)

-- Attendre que le serveur ait créé les effets
task.wait(1)
baseExposure = Lighting.ExposureCompensation
currentExposure = baseExposure

local rayParams = RaycastParams.new()
rayParams.FilterType = Enum.RaycastFilterType.Exclude

RunService.RenderStepped:Connect(function(dt)
	if not enabled then
		return
	end
	camera = workspace.CurrentCamera
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")

	-- 1) Auto‑focus sur le personnage
	local dof = getEffect("RG_DepthOfField")
	if dof and root then
		local dist = (camera.CFrame.Position - root.Position).Magnitude
		local target = math.clamp(dist, 5, 200)
		dof.FocusDistance = dof.FocusDistance + (target - dof.FocusDistance) * math.min(1, dt * 6)
		dof.InFocusRadius = math.max(15, target * 0.9)
	end

	-- 2) Adaptation de l'œil : plus sombre face au soleil, plus clair dans l'ombre
	local sunDir = Lighting:GetSunDirection()
	local facing = camera.CFrame.LookVector:Dot(sunDir) -- 1 = on regarde le soleil
	local target = baseExposure - math.max(0, facing) * 0.35

	if character then
		rayParams.FilterDescendantsInstances = { character }
		local inShadow = root and workspace:Raycast(root.Position, sunDir * 300, rayParams)
		if inShadow then
			target += 0.2
		end
	end

	currentExposure += (target - currentExposure) * math.min(1, dt * 2)
	Lighting.ExposureCompensation = currentExposure
end)
