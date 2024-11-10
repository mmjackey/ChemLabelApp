from config import AppConfig


class HazardsPrecautionData:
    def __init__(self):
        self.selected_hazards = []
        self.selected_precautions = []
        self.diamond_vars = []

        self.HAZARD_CLASSES = {
            "Physical Hazards (H2)": [
                "H200 Unstable explosive",
                "H201 Explosive; mass explosion hazard",
                "H202 Explosive; severe projection hazard",
                "H203 Explosive; fire, blast or projection hazard",
                "H204 Fire or projection hazard",
                "H205 May mass explode in fire",
                "H206 Fire, blast or projection hazard; increased risk of explosion if desensitizing agent is reduced",
                "H207 Fire or projection hazard; increased risk of explosion if desensitizing agent is reduced",
                "H208 Fire hazard; increased risk of explosion if desensitizing agent is reduced",
                "H220 Extremely flammable gas",
                "H221 Flammable gas",
                "H222 Extremely flammable aerosol",
                "H223 Flammable aerosol",
                "H224 Extremely flammable liquid and vapour",
                "H225 Highly flammable liquid and vapour",
                "H226 Flammable liquid and vapour",
                "H227 Combustible liquid",
                "H228 Flammable solid",
                "H229 Pressurized container: may burst if heated",
                "H230 May react explosively even in the absence of air",
                "H231 May react explosively even in the absence of air at elevated pressure and/or temperature",
                "H232 May ignite spontaneously if exposed to air",
                "H240 Heating may cause an explosion",
                "H241 Heating may cause a fire or explosion",
                "H242 Heating may cause a fire",
                "H250 Catches fire spontaneously if exposed to air",
                "H251 Self-heating; may catch fire",
                "H252 Self-heating in large quantities; may catch fire",
                "H260 In contact with water releases flammable gases which may ignite spontaneously",
                "H261 In contact with water releases flammable gas",
                "H270 May cause or intensify fire; oxidizer",
                "H271 May cause fire or explosion; strong oxidizer",
                "H272 May intensify fire; oxidizer",
                "H280 Contains gas under pressure; may explode if heated",
                "H281 Contains refrigerated gas; may cause cryogenic burns or injury",
                "H290 May be corrosive to metals",
            ],
            "Health Hazards (H3)": [
                "H300 Fatal if swallowed",
                "H301 Toxic if swallowed",
                "H302 Harmful if swallowed",
                "H303 May be harmful if swallowed",
                "H304 May be fatal if swallowed and enters airways",
                "H305 May be harmful if swallowed and enters airways",
                "H310 Fatal in contact with skin",
                "H311 Toxic in contact with skin",
                "H312 Harmful in contact with skin",
                "H313 May be harmful in contact with skin",
                "H314 Causes severe skin burns and eye damage",
                "H315 Causes skin irritation",
                "H316 Causes mild skin irritation",
                "H317 May cause an allergic skin reaction",
                "H318 Causes serious eye damage",
                "H319 Causes serious eye irritation",
                "H320 Causes eye irritation",
                "H330 Fatal if inhaled",
                "H331 Toxic if inhaled",
                "H332 Harmful if inhaled",
                "H333 May be harmful if inhaled",
                "H334 May cause allergy or asthma symptoms or breathing difficulties if inhaled",
                "H335 May cause respiratory irritation",
                "H336 May cause drowsiness or dizziness",
                "H340 May cause genetic defects",
                "H340 May cause genetic defects",
                "H341 Suspected of causing genetic defects",
                "H350 May cause cancer",
                "H351 Suspected of causing cancer",
                "H360 May damage fertility or the unborn child",
                "H361 Suspected of damaging fertility or the unborn child",
                "H361d Suspected of damaging the unborn child",
                "H362 May cause harm to breast-fed children",
                "H370 Causes damage to organs",
                "H371 May cause damage to organs",
                "H372 Causes damage to organs through prolonged or repeated exposure",
                "H373 May cause damage to organs through prolonged or repeated exposure",
            ],
            "Environmental Hazards (H4)": [
                "H400 Very toxic to aquatic life",
                "H401 Toxic to aquatic life",
                "H402 Harmful to aquatic life",
                "H410 Very toxic to aquatic life with long-lasting effects",
                "H411 Toxic to aquatic life with long-lasting effects",
                "H412 Harmful to aquatic life with long-lasting effects",
                "H413 May cause long-lasting harmful effects to aquatic life",
                "H420 Harms public health and the environment by destroying ozone in the upper atmosphere",
            ],
        }
        self.PRECAUTION_CLASSES = {
            "General precautionary statements (P1)": [
                "P101 If medical advice is needed, have product container or label at hand.",
                "P102 Keep out of reach of children.",
                "P103 Read carefully and follow all instructions.",
            ],
            "Prevention precautionary statements (P2)": [
                "P203 Obtain, read and follow all safety instructions before use. "
            ],
            "Response precautionary statements (P3)": [
                "P301 IF SWALLOWED: ",
                "P302 IF ON SKIN: ",
                "P303 IF ON SKIN (or hair): ",
                "P304 IF INHALED: ",
                "P305 IF IN EYES: ",
                "P306 IF ON CLOTHING: ",
                "P308 IF exposed or concerned: ",
                "P332 IF SKIN irritation occurs: ",
                "P333 If skin irritation or rash occurs: ",
                "P337 If eye irritation persists: ",
                "P370 In case of fire: ",
                "P371 In case of major fire and large quantities: ",
            ],
            "Storage precautionary statements (P4)": [
                "P401 Store in accordance with ... ",
                "P402 Store in a dry place. ",
                "P403 Store in a well-ventilated place.",
                "P404 Store in a closed container.",
                "P405 Store locked up.",
                "P406 Store in corrosive resistant/... container with a resistant inner liner.",
                "P407 Maintain air gap between stacks or pallets.",
                "P410 Protect from sunlight.",
                "P411 Store at temperatures not exceeding ... °C/...°F.",
                "P412 Do not expose to temperatures exceeding 50 °C/ 122 °F. ",
                "P413 Store bulk masses greater than ... kg/...lbs at temperatures not exceeding ... °C/...°F. ",
                "P420 Store separately.",
            ],
            "Disposal precautionary statements (P5)": [
                "P501 Dispose of contents/container to ... ",
                "P502 Refer to manufacturer or supplier for information on recovery or recycling.",
                "P503 Refer to manufacturer/supplier... for information on disposal/recovery/recycling.",
            ],
        }

        EXPLOSIVES_PATH = AppConfig.HAZARD_IMAGES / "explosives.png"
        GASSES_PATH = AppConfig.HAZARD_IMAGES / "gasses.png"
        FLAMMABLE_LIQUIDS_PATH = (
            AppConfig.HAZARD_IMAGES / "flammable liquids.png"
        )
        FLAMMABLES_PATH = AppConfig.HAZARD_IMAGES / "flammables.png"
        OXIDIZING_SUBSTANCE_PATH = (
            AppConfig.HAZARD_IMAGES / "exclamation hazard.png"
        )
        TOXIC_SUBSTANCES_PATH = (
            AppConfig.HAZARD_IMAGES / "toxic substances.png"
        )
        RADIOACTIVE_MATERIALS_PATH = (
            AppConfig.HAZARD_IMAGES / "environmental hazard.png"
        )
        CORROSIVE_SUBSTANCE_PATH = (
            AppConfig.HAZARD_IMAGES / "corrosive substances.png"
        )
        MISCELLANEOUS_PATH = AppConfig.HAZARD_IMAGES / "health hazard.png"

        self.HAZARD_DIAMONDS = {
            "Diamonds": [
                ("Class 1 - Explosives", EXPLOSIVES_PATH),
                ("Class 2 - Gasses", GASSES_PATH),
                ("Class 3 - Flammable liquids", FLAMMABLE_LIQUIDS_PATH),
                ("Class 4 - Flammable solids", FLAMMABLES_PATH),
                (
                    "Class 5 - Oxidizing substances and Organic peroxides",
                    OXIDIZING_SUBSTANCE_PATH,
                ),
                (
                    "Class 6 - Toxic* substances and Infectious substances",
                    TOXIC_SUBSTANCES_PATH,
                ),
                (
                    "Class 7 - Radioactive materials",
                    RADIOACTIVE_MATERIALS_PATH,
                ),
                ("Class 8 - Corrosive substances", CORROSIVE_SUBSTANCE_PATH),
                (
                    "Class 9 - Miscellaneous dangerous goods/hazardous materials and articles",
                    MISCELLANEOUS_PATH,
                ),
            ]
        }

    def add_hazard(self, hazard):
        self.selected_hazards.append(hazard)

    def add_precaution(self, hazard):
        self.selected_precautions.append(hazard)
