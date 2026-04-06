class Move:
    name : str
    type : str
    category : str
    power : int
    accuracy : int
    pp: int
    current_pp : int
    disabled_turns : int
    priority : int
    multihit: list[int]
    high_crit : bool
    recoil : float
    charge_turns : int
    effects : list[dict]

    def __init__(self, name : str, data: dict):
        self.name = name.upper()
        self.type = data["type"]
        self.category = data["category"]
        self.power = data["power"]
        self.accuracy = data["accuracy"]
        self.pp = data["pp"]
        self.current_pp = self.pp

        self.disabled_turns = 0

        self.priority = data.get("priority", 0)
        self.multihit = data.get("multihit", None)
        self.high_crit = data.get("high_crit", False)
        self.recoil = data.get("recoil", 0)
        self.charge_turns = data.get("charge_turns", 0)
        self.effects = data.get("effects", [])
