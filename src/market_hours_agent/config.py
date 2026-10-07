from __future__ import annotations

import os
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    secret_key: str | None
    wallet_address: str | None
    demo_mode: str

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            api_key=os.getenv("BINANCE_WEB3_API_KEY"),
            secret_key=os.getenv("BINANCE_WEB3_SECRET_KEY"),
            wallet_address=os.getenv("PULSE_WALLET_ADDRESS"),
            demo_mode=os.getenv("PULSE_DEMO_MODE", "fixture").lower(),
        )

    def health(self) -> dict[str, object]:
        missing = []
        if not self.api_key:
            missing.append("BINANCE_WEB3_API_KEY")
        if not self.secret_key:
            missing.append("BINANCE_WEB3_SECRET_KEY")
        if not self.wallet_address:
            missing.append("PULSE_WALLET_ADDRESS")
        wallet_valid = self.wallet_address is None or bool(re.fullmatch(r"0x[a-fA-F0-9]{40}", self.wallet_address))
        live_ready = not missing and wallet_valid
        return {
            "mode": self.demo_mode, "live_ready": live_ready, "credentials_present": bool(self.api_key and self.secret_key),
            "wallet_present": bool(self.wallet_address), "wallet_valid": wallet_valid, "missing": missing,
            "secrets_exposed": False,
        }

    def validate_startup(self) -> None:
        if self.demo_mode not in {"fixture", "live"}:
            raise ValueError("PULSE_DEMO_MODE must be fixture or live")
        health = self.health()
        if self.demo_mode == "live" and not health["live_ready"]:
            fields = ", ".join(health["missing"])
            raise RuntimeError(f"Live mode is not ready. Set server-side variables: {fields}")

