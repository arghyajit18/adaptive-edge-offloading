from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
class Ns3Settings(BaseModel):
    binary_path: Path = Path("/opt/ns-3-dev/build/scratch/ns3_scenario")
    tick_ms: int = 100
class DbSettings(BaseModel):
    url: str = "sqlite+aiosqlite:///./data/offload.db"
    echo: bool = False
class ApiSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
class LinkMonitorSettings(BaseModel):
    store_interval_sec: float = 1.0
class PredictionSettings(BaseModel):
    window: int = 20
    eval_interval: int = 50
class BatterySettings(BaseModel):
    budget_mj: float = 5000.0
class ClientSettings(BaseModel):
    mix: dict = {"image":0.35,"matmul":0.35,"ml_inference":0.30}
    size_range_bytes: list = 200_000, 5_000_000
    complexity_range: list = 100, 1000
    deadline_range_ms: list = 50, 300
    seed: int = 42
    local_executor: dict = {
        "base_power_w":0.5,
        "dyn_coeff":0.02,
        "cpu_freq_ghz":2.0,
        "max_complexity":1000
    }
class ComparisonSettings(BaseModel):
    num_tasks: int = 200
class DashboardSettings(BaseModel):
    refresh_interval_sec: int = 2
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    ns3: Ns3Settings = Ns3Settings()
    db: DbSettings = DbSettings()
    api: ApiSettings = ApiSettings()
    link_monitor: LinkMonitorSettings = LinkMonitorSettings()
    prediction: PredictionSettings = PredictionSettings()
    battery: BatterySettings = BatterySettings()
    client: ClientSettings = ClientSettings()
    comparison: ComparisonSettings = ComparisonSettings()
    dashboard: DashboardSettings = DashboardSettings()
settings = Settings()
