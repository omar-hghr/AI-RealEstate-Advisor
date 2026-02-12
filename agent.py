import json
import os
from math import isfinite


class AgentPreferences:
    DEFAULT = {
        "w_roi": 0.5,
        "w_risk": 0.3,
        "w_budget": 0.2
    }

    def __init__(self, user_id="default_user", path="learning.json"):
        self.user_id = user_id
        self.path = path

        self.w_roi = self.DEFAULT["w_roi"]
        self.w_risk = self.DEFAULT["w_risk"]
        self.w_budget = self.DEFAULT["w_budget"]
        self.interactions = 0

        self.load()

    def load(self):
        if not os.path.exists(self.path):
            return

        with open(self.path, "r") as f:
            data = json.load(f)

        users = data.get("users", {})
        u = users.get(self.user_id)
        if not u:
            return

        self.w_roi = float(u.get("w_roi", self.w_roi))
        self.w_risk = float(u.get("w_risk", self.w_risk))
        self.w_budget = float(u.get("w_budget", self.w_budget))
        self.interactions = int(u.get("interactions", 0))

        self.normalize()

    def save(self):
        data = {"users": {}}

        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                data = json.load(f)

        data["users"][self.user_id] = {
            "w_roi": self.w_roi,
            "w_risk": self.w_risk,
            "w_budget": self.w_budget,
            "interactions": self.interactions
        }

        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    def normalize(self):
        t = self.w_roi + self.w_risk + self.w_budget
        if t > 0 and isfinite(t):
            self.w_roi /= t
            self.w_risk /= t
            self.w_budget /= t

    def update_from_choice(self, prop, budget):
        self.interactions += 1

        if prop.get("roi", 0) >= 0.15:
            self.w_roi += 0.03
        elif prop.get("roi", 0) <= 0.10:
            self.w_roi -= 0.02

        if "Low" in prop.get("risk_text", ""):
            self.w_risk += 0.03
        elif "High" in prop.get("risk_text", ""):
            self.w_risk -= 0.03

        if budget and budget > 0:
            diff = abs(prop.get("price", 0) - budget) / budget
            if diff <= 0.15:
                self.w_budget += 0.03
            elif diff >= 0.40:
                self.w_budget -= 0.03

        self.normalize()
        self.save()

    def update_from_rejection(self, props, budget):
        self.interactions += 1
        self.w_roi -= 0.02

        if budget and budget > 0 and props:
            diffs = [
                abs(p.get("price", 0) - budget) / budget
                for p in props
            ]
            avg_diff = sum(diffs) / len(diffs)

            if avg_diff >= 0.4:
                self.w_budget += 0.03
            elif avg_diff <= 0.15:
                self.w_budget -= 0.02

        self.normalize()
        self.save()
    