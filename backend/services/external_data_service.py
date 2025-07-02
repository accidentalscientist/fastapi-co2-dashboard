import asyncio
import aiohttp
import logging
import csv
import io
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from schemas.models import EmissionRecord, EnergyRecord

logger = logging.getLogger(__name__)

class ExternalDataService:
    """Service for fetching real sustainability data from external APIs"""
    
    def __init__(self):
        self.world_bank_base_url = "https://api.worldbank.org/v2"
        self.owid_co2_url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
        self.session_timeout = aiohttp.ClientTimeout(total=60)
        
        # World Bank indicator codes
        self.indicators = {
            "co2_emissions_per_capita": "EN.ATM.CO2E.PC",  # CO2 emissions (metric tons per capita)
            "co2_emissions_total": "EN.ATM.CO2E.KT",       # CO2 emissions (kt)
            "renewable_energy": "EG.FEC.RNEW.ZS",         # Renewable energy consumption (% of total final energy)
            "population": "SP.POP.TOTL",                   # Population, total
            "gdp_per_capita": "NY.GDP.PCAP.CD"             # GDP per capita (current US$)
        }
        
        # Target countries for comprehensive coverage (Our World in Data uses full names)
        self.target_countries = [
            "United States", "China", "India", "Russia", "Japan", "Germany", 
            "Iran", "South Korea", "Saudi Arabia", "Indonesia", "Canada", 
            "Mexico", "Brazil", "Australia", "United Kingdom", "Italy", 
            "France", "Turkey", "Poland", "Thailand", "Egypt", "Argentina", 
            "Malaysia", "Netherlands", "Spain", "Pakistan", "Bangladesh", 
            "Vietnam", "Nigeria", "Philippines", "South Africa", "Iraq", 
            "Venezuela", "Kazakhstan", "Algeria", "Chile", "Morocco", "Peru", 
            "Israel", "Norway", "Finland", "Denmark", "Sweden", "Switzerland", 
            "Austria", "Belgium", "Portugal", "Czech Republic", "Greece", "Ukraine"
        ]
        
        # ISO3 to country name mapping for World Bank compatibility
        self.iso3_to_name = {
            "US": "United States", "CN": "China", "IN": "India", "RU": "Russia", 
            "JP": "Japan", "DE": "Germany", "IR": "Iran", "KR": "South Korea", 
            "SA": "Saudi Arabia", "ID": "Indonesia", "CA": "Canada", "MX": "Mexico", 
            "BR": "Brazil", "AU": "Australia", "GB": "United Kingdom", "IT": "Italy", 
            "FR": "France", "TR": "Turkey", "PL": "Poland", "TH": "Thailand",
            "EG": "Egypt", "AR": "Argentina", "MY": "Malaysia", "NL": "Netherlands", 
            "ES": "Spain", "PK": "Pakistan", "BD": "Bangladesh", "VN": "Vietnam", 
            "NG": "Nigeria", "PH": "Philippines", "ZA": "South Africa", "IQ": "Iraq", 
            "VE": "Venezuela", "KZ": "Kazakhstan", "DZ": "Algeria", "CL": "Chile", 
            "MA": "Morocco", "PE": "Peru", "IL": "Israel", "NO": "Norway",
            "FI": "Finland", "DK": "Denmark", "SE": "Sweden", "CH": "Switzerland", 
            "AT": "Austria", "BE": "Belgium", "PT": "Portugal", "CZ": "Czech Republic", 
            "GR": "Greece", "UA": "Ukraine"
        }

    async def fetch_owid_co2_data(self, target_years: List[int] = None) -> Dict[str, List[Dict]]:
        """Fetch CO2 emissions data from Our World in Data CSV"""
        
        if target_years is None:
            target_years = list(range(2010, 2024))
            
        try:
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                async with session.get(self.owid_co2_url) as response:
                    if response.status == 200:
                        csv_content = await response.text()
                        
                        # Parse CSV data
                        csv_reader = csv.DictReader(io.StringIO(csv_content))
                        
                        # Filter and organize data by year
                        data_by_year = {year: [] for year in target_years}
                        
                        total_rows = 0
                        matching_rows = 0
                        
                        for row in csv_reader:
                            total_rows += 1
                            try:
                                year = int(row.get('year', 0))
                                country = row.get('country', '').strip()
                                
                                # Filter for target years and countries
                                if year in target_years and country in self.target_countries:
                                    matching_rows += 1
                                    # Extract relevant fields
                                    co2_total = row.get('co2')  # Million tonnes
                                    co2_per_capita = row.get('co2_per_capita')  # Tonnes per person
                                    population = row.get('population')
                                    gdp = row.get('gdp')
                                    
                                    # Create record if we have essential data
                                    if co2_total or co2_per_capita:
                                        record = {
                                            'country': country,
                                            'year': year,
                                            'co2_total': float(co2_total) if co2_total else None,
                                            'co2_per_capita': float(co2_per_capita) if co2_per_capita else None,
                                            'population': int(float(population)) if population else None,
                                            'gdp': float(gdp) if gdp else None
                                        }
                                        data_by_year[year].append(record)
                                        
                            except (ValueError, TypeError) as e:
                                # Skip malformed rows
                                continue
                        
                        years_with_data = len([y for y in data_by_year.values() if y])
                        total_records = sum(len(records) for records in data_by_year.values())
                        
                        logger.info(f"Processed {total_rows} total rows, {matching_rows} matching rows")
                        logger.info(f"Fetched OWID CO2 data: {years_with_data} years with data, {total_records} total records")
                        
                        # Debug: Show sample data
                        for year in [2020, 2023]:
                            if year in data_by_year and data_by_year[year]:
                                logger.info(f"Year {year}: {len(data_by_year[year])} records, sample: {data_by_year[year][0]['country'] if data_by_year[year] else 'None'}")
                        
                        return data_by_year
                        
                    else:
                        logger.error(f"OWID API error: {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Error fetching OWID CO2 data: {e}")
            return {}

    async def fetch_world_bank_data(self, indicator: str, countries: List[str] = None, 
                                  start_year: int = 2010, end_year: int = 2023) -> List[Dict]:
        """Fetch data from World Bank API"""
        
        if countries is None:
            # Use ISO3 codes for World Bank API
            countries = list(self.iso3_to_name.keys())
            
        country_codes = ";".join(countries)
        date_range = f"{start_year}:{end_year}"
        
        url = f"{self.world_bank_base_url}/country/{country_codes}/indicator/{indicator}"
        params = {
            "format": "json",
            "date": date_range,
            "per_page": 5000  # Large page size to get all data
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        # World Bank API returns [metadata, data]
                        if isinstance(data, list) and len(data) > 1:
                            return data[1] or []
                        return []
                    else:
                        logger.error(f"World Bank API error {response.status} for indicator {indicator}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching World Bank data for {indicator}: {e}")
            return []

    async def fetch_comprehensive_country_data(self, year: int) -> Dict[str, Dict]:
        """Fetch comprehensive data for all indicators for a specific year"""
        
        tasks = []
        for indicator_name, indicator_code in self.indicators.items():
            task = self.fetch_world_bank_data(indicator_code, start_year=year, end_year=year)
            tasks.append((indicator_name, task))
        
        # Execute all API calls concurrently
        results = {}
        for indicator_name, task in tasks:
            data = await task
            results[indicator_name] = {item['countryiso3code']: item for item in data if item.get('value') is not None}
        
        return results

    async def update_emissions_with_real_data(self, db, target_years: List[int] = None):
        """Update emissions data with real World Bank data"""
        
        if target_years is None:
            target_years = list(range(2010, 2024))
            
        try:
            emissions_collection = db["emissions"]
            
            for year in target_years:
                logger.info(f"Fetching real emissions data for {year}")
                
                # Fetch data for the year
                year_data = await self.fetch_comprehensive_country_data(year)
                
                records_to_upsert = []
                
                # Process each country
                for country_code in self.target_countries:
                    try:
                        # Get country name mapping
                        country_name = self.get_country_name(country_code)
                        
                        # Extract data for this country
                        co2_per_capita = year_data.get("co2_emissions_per_capita", {}).get(country_code, {}).get("value")
                        co2_total_kt = year_data.get("co2_emissions_total", {}).get(country_code, {}).get("value")
                        population = year_data.get("population", {}).get(country_code, {}).get("value")
                        gdp_per_capita = year_data.get("gdp_per_capita", {}).get(country_code, {}).get("value")
                        
                        # Skip if no emissions data
                        if co2_per_capita is None and co2_total_kt is None:
                            continue
                            
                        # Calculate total emissions in Mt (World Bank gives kt)
                        if co2_total_kt is not None:
                            co2_emissions_mt = co2_total_kt / 1000  # Convert kt to Mt
                        elif co2_per_capita is not None and population is not None:
                            co2_emissions_mt = (co2_per_capita * population) / 1000000  # Mt
                        else:
                            continue
                            
                        # Use actual per capita value or calculate it
                        if co2_per_capita is None and population is not None:
                            co2_per_capita = (co2_emissions_mt * 1000000) / population
                        
                        record = EmissionRecord(
                            country=country_name,
                            year=year,
                            co2_emissions=round(co2_emissions_mt, 2),
                            population=int(population) if population else 0,
                            gdp=round(gdp_per_capita, 2) if gdp_per_capita else 0.0,
                            co2_per_capita=round(co2_per_capita, 2) if co2_per_capita else 0.0,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        
                        records_to_upsert.append(record.model_dump(exclude={"id"}))
                        
                    except Exception as e:
                        logger.warning(f"Error processing {country_code} for {year}: {e}")
                        continue
                
                # Batch upsert records
                if records_to_upsert:
                    for record in records_to_upsert:
                        await emissions_collection.update_one(
                            {"country": record["country"], "year": record["year"]},
                            {"$set": record},
                            upsert=True
                        )
                    
                    logger.info(f"Updated {len(records_to_upsert)} real emission records for {year}")
                else:
                    logger.warning(f"No emission data found for {year}")
                    
                # Add delay between years to be respectful to the API
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error updating emissions with real data: {e}")
            raise

    async def update_energy_with_real_data(self, db, target_years: List[int] = None):
        """Update energy data with real World Bank data"""
        
        if target_years is None:
            target_years = list(range(2010, 2024))
            
        try:
            energy_collection = db["energy"]
            
            for year in target_years:
                logger.info(f"Fetching real energy data for {year}")
                
                # Fetch renewable energy data
                renewable_data = await self.fetch_world_bank_data(
                    self.indicators["renewable_energy"], 
                    start_year=year, 
                    end_year=year
                )
                
                records_to_upsert = []
                
                for item in renewable_data:
                    if item.get('value') is None:
                        continue
                        
                    country_code = item.get('countryiso3code')
                    country_name = self.iso3_to_name.get(country_code, country_code)
                    renewable_percentage = item.get('value')
                    
                    # Generate realistic energy consumption data based on country size
                    # This is estimated since World Bank doesn't have total energy consumption in TWh
                    total_energy = self.estimate_total_energy_consumption(country_code)
                    renewable_energy = total_energy * (renewable_percentage / 100)
                    fossil_fuel_energy = total_energy - renewable_energy
                    
                    record = EnergyRecord(
                        country=country_name,
                        year=year,
                        renewable_percentage=round(renewable_percentage, 2),
                        total_energy_consumption=round(total_energy, 2),
                        renewable_energy=round(renewable_energy, 2),
                        fossil_fuel_energy=round(fossil_fuel_energy, 2),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    records_to_upsert.append(record.model_dump(exclude={"id"}))
                
                # Batch upsert records
                if records_to_upsert:
                    for record in records_to_upsert:
                        await energy_collection.update_one(
                            {"country": record["country"], "year": record["year"]},
                            {"$set": record},
                            upsert=True
                        )
                    
                    logger.info(f"Updated {len(records_to_upsert)} real energy records for {year}")
                
                # Add delay between years
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error updating energy with real data: {e}")
            raise


    def estimate_total_energy_consumption(self, country_code: str) -> float:
        """Estimate total energy consumption in TWh based on country characteristics"""
        # Rough estimates based on country size and development level
        energy_estimates = {
            "US": 4000, "CN": 7500, "IN": 1200, "RU": 1100, "JP": 1000,
            "DE": 600, "BR": 600, "CA": 650, "KR": 550, "GB": 350,
            "IT": 320, "FR": 480, "AU": 260, "ES": 280, "MX": 300,
            "ID": 250, "TR": 280, "SA": 350, "IR": 280, "TH": 200,
            "ZA": 230, "PL": 170, "AR": 130, "EG": 180, "NL": 120,
            "MY": 180, "PK": 120, "VN": 220, "BD": 80, "NG": 30,
            "PH": 100, "IQ": 90, "VE": 80, "KZ": 100, "DZ": 70,
            "CL": 80, "MA": 40, "PE": 55, "IL": 65, "NO": 140,
            "FI": 85, "DK": 35, "SE": 140, "CH": 60, "AT": 75,
            "BE": 85, "PT": 50, "CZ": 75, "GR": 50, "UA": 120
        }
        return energy_estimates.get(country_code, 50)  # Default 50 TWh for unknown countries

    async def seed_real_historical_data(self, db):
        """Seed database with real historical data from Our World in Data and World Bank"""
        try:
            emissions_collection = db["emissions"]
            
            # Check if we already have recent real data
            recent_data = await emissions_collection.find_one({
                "year": 2023, 
                "data_source": {"$ne": "synthetic"},
                "updated_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
            })
            
            if recent_data:
                logger.info("Recent real data already exists, skipping full reseed")
                return
            
            logger.info("Starting real data seeding from Our World in Data and World Bank APIs...")
            
            # Priority years (most recent first for faster API response)
            priority_years = [2023, 2022, 2021, 2020]
            all_years = list(range(2010, 2024))
            
            # Fetch CO2 data from Our World in Data (more comprehensive)
            logger.info("Fetching CO2 emissions data from Our World in Data...")
            owid_data = await self.fetch_owid_co2_data(all_years)
            
            logger.info(f"OWID data fetched: {len(owid_data)} years, total records: {sum(len(records) for records in owid_data.values())}")
            
            # Process and insert OWID data
            records_inserted = 0
            for year, year_records in owid_data.items():
                if not year_records:
                    logger.warning(f"No emission data found for {year}")
                    continue
                    
                logger.info(f"Processing {len(year_records)} CO2 records for {year}")
                
                for record_data in year_records:
                    try:
                        # Calculate missing values if needed
                        co2_total = record_data.get('co2_total')  # Already in Mt
                        co2_per_capita = record_data.get('co2_per_capita')
                        population = record_data.get('population')
                        
                        # Skip if no emission data
                        if not co2_total and not co2_per_capita:
                            continue
                            
                        # Calculate per capita if missing
                        if not co2_per_capita and co2_total and population:
                            co2_per_capita = (co2_total * 1000000) / population  # Mt to tonnes
                            
                        # Calculate total if missing  
                        if not co2_total and co2_per_capita and population:
                            co2_total = (co2_per_capita * population) / 1000000  # tonnes to Mt
                        
                        record = EmissionRecord(
                            country=record_data['country'],
                            year=record_data['year'],
                            co2_emissions=round(co2_total, 2) if co2_total else 0.0,
                            population=population if population else 0,
                            gdp=round(record_data.get('gdp', 0.0), 2) if record_data.get('gdp') else 0.0,
                            co2_per_capita=round(co2_per_capita, 2) if co2_per_capita else 0.0,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        
                        record_dict = record.model_dump(exclude={"id"})
                        record_dict["data_source"] = "our_world_in_data"
                        
                        await emissions_collection.update_one(
                            {"country": record.country, "year": record.year},
                            {"$set": record_dict},
                            upsert=True
                        )
                        records_inserted += 1
                        
                    except Exception as e:
                        logger.warning(f"Error processing OWID record for {record_data.get('country', 'unknown')}: {e}")
                        continue
            
            logger.info(f"Inserted {records_inserted} real CO2 emission records from Our World in Data")
            
            # Fetch renewable energy data from World Bank (still the best source for this)
            logger.info("Fetching renewable energy data from World Bank...")
            await self.update_energy_with_real_data(db, all_years)
            
            # Update metadata
            metadata_collection = db["metadata"]
            await metadata_collection.update_one(
                {"type": "data_source"},
                {
                    "$set": {
                        "type": "data_source",
                        "primary_source": "Our World in Data (CO2), World Bank (Energy)",
                        "last_updated": datetime.utcnow(),
                        "co2_source": "Our World in Data GitHub Repository",
                        "energy_source": "World Bank Open Data API",
                        "coverage_years": f"{min(all_years)}-{max(all_years)}",
                        "countries_count": len(self.target_countries)
                    }
                },
                upsert=True
            )
            
            logger.info("Completed real data seeding from Our World in Data and World Bank APIs")
            
        except Exception as e:
            logger.error(f"Error seeding real historical data: {e}")
            raise