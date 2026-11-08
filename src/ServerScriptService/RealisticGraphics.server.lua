--[[
	RealisticGraphics.server.lua
	Graphismes réalistes "de ouf" tout en gardant le style Roblox.

	À placer dans : ServerScriptService (Script)

	⚠️ À FAIRE UNE FOIS DANS STUDIO (non modifiable par script) :
	   Explorer > Lighting > Propriétés > Technology = Future
	   (c'est ce qui donne les vraies ombres, reflets et lumières dynamiques)

	Changez PRESET ci‑dessous : "CleanHD", "Jour", "CoucherDeSoleil" ou "Nuit"
]]

local Lighting = game:GetService("Lighting")
local MaterialService = game:GetService("MaterialService")

local PRESET = "CleanHD" -- "CleanHD", "Jour", "CoucherDeSoleil" ou "Nuit"

-- Petit utilitaire : applique une propriété sans planter si elle n'existe pas
-- (certaines propriétés récentes ne sont pas dispo partout)
local function trySet(instance, prop, value)
	local ok = pcall(function()
		instance[prop] = value
	end)
	if not ok then
		warn(("[RealisticGraphics] Impossible de régler %s.%s"):format(instance.ClassName, prop))
	end
end

local function getOrCreate(className, name, parent)
	local obj = parent:FindFirstChild(name)
	if obj and obj.ClassName ~= className then
		obj:Destroy()
		obj = nil
	end
	if not obj then
		obj = Instance.new(className)
		obj.Name = name
		obj.Parent = parent
	end
	return obj
end

-- Supprime les anciens effets qui pourraient entrer en conflit
for _, child in ipairs(Lighting:GetChildren()) do
	if child:IsA("PostEffect") or child:IsA("Atmosphere") or child:IsA("Sky") or child:IsA("Clouds") then
		if not child.Name:match("^RG_") then
			child:Destroy()
		end
	end
end

local PRESETS = {
	-- Rendu "photo TikTok" : net partout, ciel bleu vif, peau qui brille, pas de brume ni de flou
	CleanHD = {
		ClockTime = 13.5,
		Brightness = 3,
		ExposureCompensation = 0.1,
		Ambient = Color3.fromRGB(40, 40, 45),
		OutdoorAmbient = Color3.fromRGB(135, 140, 150),
		ColorShift_Top = Color3.fromRGB(255, 247, 235),
		ColorShift_Bottom = Color3.fromRGB(50, 55, 70),
		Atmosphere = {
			Density = 0.22,
			Offset = 0,
			Color = Color3.fromRGB(190, 215, 245),
			Decay = Color3.fromRGB(90, 130, 200),
			Glare = 0,
			Haze = 0,
		},
		Bloom = { Intensity = 0.4, Size = 24, Threshold = 1.8 },
		CC = { Brightness = 0.03, Contrast = 0.12, Saturation = 0.2, TintColor = Color3.fromRGB(255, 252, 248) },
		SunRays = { Intensity = 0.02, Spread = 0.5 },
		DOF = false, -- pas de flou : tout est net
		Clouds = { Cover = 0.4, Density = 0.6, Color = Color3.fromRGB(255, 255, 255) },
	},
	Jour = {
		ClockTime = 14.2,
		Brightness = 3.2,
		ExposureCompensation = 0.15,
		Ambient = Color3.fromRGB(25, 25, 30),
		OutdoorAmbient = Color3.fromRGB(120, 125, 140),
		ColorShift_Top = Color3.fromRGB(255, 244, 225),
		ColorShift_Bottom = Color3.fromRGB(40, 45, 60),
		Atmosphere = {
			Density = 0.32,
			Offset = 0.25,
			Color = Color3.fromRGB(199, 214, 235),
			Decay = Color3.fromRGB(106, 120, 150),
			Glare = 0.35,
			Haze = 1.6,
		},
		Bloom = { Intensity = 0.55, Size = 28, Threshold = 1.6 },
		CC = { Brightness = 0.02, Contrast = 0.16, Saturation = 0.12, TintColor = Color3.fromRGB(255, 250, 244) },
		SunRays = { Intensity = 0.06, Spread = 0.75 },
		DOF = { FarIntensity = 0.12, FocusDistance = 40, InFocusRadius = 45, NearIntensity = 0 },
		Clouds = { Cover = 0.55, Density = 0.75, Color = Color3.fromRGB(255, 255, 255) },
	},
	CoucherDeSoleil = {
		ClockTime = 17.75,
		Brightness = 2.6,
		ExposureCompensation = 0.25,
		Ambient = Color3.fromRGB(30, 22, 25),
		OutdoorAmbient = Color3.fromRGB(140, 110, 100),
		ColorShift_Top = Color3.fromRGB(255, 190, 130),
		ColorShift_Bottom = Color3.fromRGB(60, 40, 70),
		Atmosphere = {
			Density = 0.38,
			Offset = 0.2,
			Color = Color3.fromRGB(255, 190, 150),
			Decay = Color3.fromRGB(120, 80, 110),
			Glare = 1.2,
			Haze = 2.2,
		},
		Bloom = { Intensity = 0.8, Size = 32, Threshold = 1.3 },
		CC = { Brightness = 0.03, Contrast = 0.2, Saturation = 0.2, TintColor = Color3.fromRGB(255, 236, 220) },
		SunRays = { Intensity = 0.12, Spread = 0.85 },
		DOF = { FarIntensity = 0.15, FocusDistance = 40, InFocusRadius = 45, NearIntensity = 0 },
		Clouds = { Cover = 0.6, Density = 0.7, Color = Color3.fromRGB(255, 205, 180) },
	},
	Nuit = {
		ClockTime = 0.5,
		Brightness = 1.2,
		ExposureCompensation = 0.4,
		Ambient = Color3.fromRGB(10, 12, 20),
		OutdoorAmbient = Color3.fromRGB(45, 55, 85),
		ColorShift_Top = Color3.fromRGB(170, 190, 255),
		ColorShift_Bottom = Color3.fromRGB(10, 10, 25),
		Atmosphere = {
			Density = 0.4,
			Offset = 0.1,
			Color = Color3.fromRGB(60, 70, 110),
			Decay = Color3.fromRGB(20, 25, 45),
			Glare = 0,
			Haze = 1.5,
		},
		Bloom = { Intensity = 1, Size = 36, Threshold = 0.9 },
		CC = { Brightness = 0, Contrast = 0.22, Saturation = -0.05, TintColor = Color3.fromRGB(225, 232, 255) },
		SunRays = { Intensity = 0.02, Spread = 0.5 },
		DOF = { FarIntensity = 0.18, FocusDistance = 35, InFocusRadius = 40, NearIntensity = 0 },
		Clouds = { Cover = 0.45, Density = 0.6, Color = Color3.fromRGB(70, 80, 110) },
	},
}

local p = PRESETS[PRESET] or PRESETS.CleanHD

---------------------------------------------------------------------
-- 1) Moteur de lumière
---------------------------------------------------------------------
trySet(Lighting, "Technology", Enum.Technology.Future) -- marche seulement si autorisé, sinon réglez‑le à la main
trySet(Lighting, "LightingStyle", Enum.LightingStyle.Realistic) -- nouvelle option Roblox (si dispo)
trySet(Lighting, "PrioritizeLightingQuality", true)

Lighting.GlobalShadows = true
Lighting.ShadowSoftness = 0.12 -- ombres nettes mais pas "pixel"
Lighting.EnvironmentDiffuseScale = 1 -- lumière indirecte du ciel
Lighting.EnvironmentSpecularScale = 1 -- reflets du ciel sur les matériaux
Lighting.ClockTime = p.ClockTime
Lighting.GeographicLatitude = 41.7
Lighting.Brightness = p.Brightness
Lighting.ExposureCompensation = p.ExposureCompensation
Lighting.Ambient = p.Ambient
Lighting.OutdoorAmbient = p.OutdoorAmbient
Lighting.ColorShift_Top = p.ColorShift_Top
Lighting.ColorShift_Bottom = p.ColorShift_Bottom
Lighting.FogEnd = 100000 -- l'Atmosphere gère le brouillard

---------------------------------------------------------------------
-- 2) Atmosphère (brume, profondeur, horizon réaliste)
---------------------------------------------------------------------
local atmosphere = getOrCreate("Atmosphere", "RG_Atmosphere", Lighting)
for k, v in pairs(p.Atmosphere) do
	atmosphere[k] = v
end

---------------------------------------------------------------------
-- 3) Ciel + nuages volumétriques
---------------------------------------------------------------------
local sky = getOrCreate("Sky", "RG_Sky", Lighting)
sky.CelestialBodiesShown = true
sky.SunAngularSize = 11
sky.MoonAngularSize = 9
sky.StarCount = 3000

local terrain = workspace:FindFirstChildOfClass("Terrain")
if terrain then
	local clouds = getOrCreate("Clouds", "RG_Clouds", terrain)
	for k, v in pairs(p.Clouds) do
		clouds[k] = v
	end

	-- Eau plus réaliste
	terrain.WaterColor = Color3.fromRGB(30, 75, 90)
	terrain.WaterTransparency = 0.85
	terrain.WaterReflectance = 0.6
	terrain.WaterWaveSize = 0.12
	terrain.WaterWaveSpeed = 8
	trySet(terrain, "Decoration", true) -- herbe animée
end

---------------------------------------------------------------------
-- 4) Post‑processing (le "rendu cinéma")
---------------------------------------------------------------------
local bloom = getOrCreate("BloomEffect", "RG_Bloom", Lighting)
for k, v in pairs(p.Bloom) do
	bloom[k] = v
end

local cc = getOrCreate("ColorCorrectionEffect", "RG_ColorCorrection", Lighting)
for k, v in pairs(p.CC) do
	cc[k] = v
end

local sunRays = getOrCreate("SunRaysEffect", "RG_SunRays", Lighting)
for k, v in pairs(p.SunRays) do
	sunRays[k] = v
end

local dof = getOrCreate("DepthOfFieldEffect", "RG_DepthOfField", Lighting)
if p.DOF then
	dof.Enabled = true
	for k, v in pairs(p.DOF) do
		dof[k] = v
	end
else
	dof.Enabled = false
end

---------------------------------------------------------------------
-- 5) Matériaux HD (textures 2022 = beaucoup plus détaillées)
---------------------------------------------------------------------
trySet(MaterialService, "Use2022Materials", true)

-- Rend le sol un peu plus "réel" (léger reflet) sans changer la grille Roblox
local baseplate = workspace:FindFirstChild("Baseplate")
if baseplate and baseplate:IsA("BasePart") then
	baseplate.Reflectance = 0.04
end

---------------------------------------------------------------------
-- 6) Personnages : ombres + matériaux plus doux
---------------------------------------------------------------------
local Players = game:GetService("Players")

local function enhanceCharacter(character)
	for _, d in ipairs(character:GetDescendants()) do
		if d:IsA("BasePart") then
			d.CastShadow = true
		end
	end
	character.DescendantAdded:Connect(function(d)
		if d:IsA("BasePart") then
			d.CastShadow = true
		end
	end)
end

local function onPlayer(player)
	if player.Character then
		enhanceCharacter(player.Character)
	end
	player.CharacterAdded:Connect(enhanceCharacter)
end

Players.PlayerAdded:Connect(onPlayer)
for _, player in ipairs(Players:GetPlayers()) do
	onPlayer(player)
end

-- Sert au script client pour savoir quel preset est actif
Lighting:SetAttribute("RG_Preset", PRESET)

print(("[RealisticGraphics] Preset '%s' appliqué ✅"):format(PRESET))
