from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MetricType(str, Enum):
    CO2_EMISSIONS = "co2_emissions"
    RENEWABLE_ENERGY = "renewable_energy"
    ENERGY_CONSUMPTION = "energy_consumption"
    WASTE_GENERATION = "waste_generation"
    GREEN_POLICY_INDEX = "green_policy_index"

class EmissionRecord(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    id: Optional[str] = Field(default=None, alias="_id")
    country: str
    year: int
    co2_emissions: float  # in metric tons
    population: Optional[int] = None
    gdp: Optional[float] = None
    co2_per_capita: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class EnergyRecord(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    id: Optional[str] = Field(default=None, alias="_id")
    country: str
    year: int
    renewable_percentage: float
    total_energy_consumption: float  # in TWh
    renewable_energy: float  # in TWh
    fossil_fuel_energy: float  # in TWh
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CountryMetrics(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    id: Optional[str] = Field(default=None, alias="_id")
    country: str
    year: int
    co2_emissions: Optional[float] = None
    renewable_percentage: Optional[float] = None
    green_policy_score: Optional[float] = None
    sustainability_ranking: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DashboardStats(BaseModel):
    total_countries: int
    latest_year: int
    total_co2_emissions: float
    avg_renewable_percentage: float
    top_performers: List[Dict[str, Any]]
    worst_performers: List[Dict[str, Any]]
    last_updated: datetime

class TimeSeriesData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]

class ChartData(BaseModel):
    type: str
    title: str
    data: TimeSeriesData
    last_updated: datetime

class HealthStatus(BaseModel):
    status: str
    database_connected: bool
    last_data_update: Optional[datetime] = None
    scheduler_running: bool
    total_records: int
    uptime: str