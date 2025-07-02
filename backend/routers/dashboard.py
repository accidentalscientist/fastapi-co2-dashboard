from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

from db import get_database
from schemas.models import (
    DashboardStats, 
    ChartData, 
    TimeSeriesData,
    EmissionRecord,
    EnergyRecord,
    CountryMetrics
)

router = APIRouter()

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db=Depends(get_database)):
    """Get overall dashboard statistics"""
    
    try:
        emissions_collection = db["emissions"]
        energy_collection = db["energy"]
        
        # Get total countries
        countries = await emissions_collection.distinct("country")
        total_countries = len(countries)
        
        # Get latest year
        latest_emission = await emissions_collection.find_one(
            {}, sort=[("year", -1)]
        )
        latest_year = latest_emission["year"] if latest_emission else 2023
        
        # Calculate total CO2 emissions for latest year
        pipeline = [
            {"$match": {"year": latest_year}},
            {"$group": {"_id": None, "total": {"$sum": "$co2_emissions"}}}
        ]
        total_co2_result = await emissions_collection.aggregate(pipeline).to_list(1)
        total_co2_emissions = total_co2_result[0]["total"] if total_co2_result else 0
        
        # Calculate average renewable percentage
        energy_pipeline = [
            {"$match": {"year": latest_year}},
            {"$group": {"_id": None, "avg": {"$avg": "$renewable_percentage"}}}
        ]
        avg_renewable_result = await energy_collection.aggregate(energy_pipeline).to_list(1)
        avg_renewable_percentage = avg_renewable_result[0]["avg"] if avg_renewable_result else 0
        
        # Get top and worst performers by CO2 per capita
        top_performers = await emissions_collection.find(
            {"year": latest_year, "co2_per_capita": {"$exists": True}},
            {"country": 1, "co2_per_capita": 1, "_id": 0}
        ).sort("co2_per_capita", 1).limit(5).to_list(5)
        
        worst_performers = await emissions_collection.find(
            {"year": latest_year, "co2_per_capita": {"$exists": True}},
            {"country": 1, "co2_per_capita": 1, "_id": 0}
        ).sort("co2_per_capita", -1).limit(5).to_list(5)
        
        return DashboardStats(
            total_countries=total_countries,
            latest_year=latest_year,
            total_co2_emissions=round(total_co2_emissions, 2),
            avg_renewable_percentage=round(avg_renewable_percentage, 2),
            top_performers=top_performers,
            worst_performers=worst_performers,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard stats: {str(e)}")

@router.get("/dashboard/co2-timeseries", response_model=ChartData)
async def get_co2_timeseries(
    countries: Optional[List[str]] = Query(default=None),
    start_year: Optional[int] = Query(default=2010),
    end_year: Optional[int] = Query(default=2023),
    db=Depends(get_database)
):
    """Get CO2 emissions time series data"""
    
    try:
        emissions_collection = db["emissions"]
        
        # If no countries specified, get top 10 emitters
        if not countries:
            top_emitters = await emissions_collection.aggregate([
                {"$match": {"year": end_year}},
                {"$sort": {"co2_emissions": -1}},
                {"$limit": 10},
                {"$project": {"country": 1}}
            ]).to_list(10)
            countries = [doc["country"] for doc in top_emitters]
        
        # Build query
        query = {
            "country": {"$in": countries},
            "year": {"$gte": start_year, "$lte": end_year}
        }
        
        # Get data
        emissions_data = await emissions_collection.find(
            query,
            {"country": 1, "year": 1, "co2_emissions": 1, "_id": 0}
        ).sort([("country", 1), ("year", 1)]).to_list(None)
        
        # Process data for chart
        years = sorted(list(set(doc["year"] for doc in emissions_data)))
        labels = [str(year) for year in years]
        
        datasets = []
        colors = [
            "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF",
            "#FF9F40", "#FF6384", "#C9CBCF", "#4BC0C0", "#FF6384"
        ]
        
        for i, country in enumerate(countries):
            country_data = [doc for doc in emissions_data if doc["country"] == country]
            data_points = []
            
            for year in years:
                year_data = next((doc for doc in country_data if doc["year"] == year), None)
                data_points.append(year_data["co2_emissions"] if year_data else 0)
            
            datasets.append({
                "label": country,
                "data": data_points,
                "borderColor": colors[i % len(colors)],
                "backgroundColor": colors[i % len(colors)] + "20",
                "fill": False
            })
        
        return ChartData(
            type="line",
            title="CO2 Emissions Over Time",
            data=TimeSeriesData(labels=labels, datasets=datasets),
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching CO2 timeseries: {str(e)}")

@router.get("/dashboard/renewable-energy", response_model=ChartData)
async def get_renewable_energy_data(
    year: Optional[int] = Query(default=2023),
    limit: Optional[int] = Query(default=15),
    db=Depends(get_database)
):
    """Get renewable energy percentage by country"""
    
    try:
        energy_collection = db["energy"]
        
        # Get top countries by renewable percentage
        pipeline = [
            {"$match": {"year": year}},
            {"$sort": {"renewable_percentage": -1}},
            {"$limit": limit},
            {"$project": {
                "country": 1,
                "renewable_percentage": 1,
                "_id": 0
            }}
        ]
        
        energy_data = await energy_collection.aggregate(pipeline).to_list(limit)
        
        countries = [doc["country"] for doc in energy_data]
        percentages = [doc["renewable_percentage"] for doc in energy_data]
        
        colors = [
            "#4CAF50", "#8BC34A", "#CDDC39", "#FFEB3B", "#FFC107",
            "#FF9800", "#FF5722", "#F44336", "#E91E63", "#9C27B0",
            "#673AB7", "#3F51B5", "#2196F3", "#03A9F4", "#00BCD4"
        ]
        
        datasets = [{
            "label": "Renewable Energy %",
            "data": percentages,
            "backgroundColor": colors[:len(countries)],
            "borderWidth": 1
        }]
        
        return ChartData(
            type="bar",
            title=f"Renewable Energy Percentage by Country ({year})",
            data=TimeSeriesData(labels=countries, datasets=datasets),
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching renewable energy data: {str(e)}")

@router.get("/dashboard/emissions-comparison")
async def get_emissions_comparison(
    compare_years: List[int] = Query(default=[2020, 2023]),
    limit: Optional[int] = Query(default=10),
    db=Depends(get_database)
):
    """Get year-over-year emissions comparison"""
    
    try:
        emissions_collection = db["emissions"]
        
        if len(compare_years) != 2:
            raise HTTPException(status_code=400, detail="Exactly two years must be provided for comparison")
        
        year1, year2 = compare_years
        
        # Get data for both years
        pipeline = [
            {"$match": {"year": {"$in": [year1, year2]}}},
            {"$group": {
                "_id": "$country",
                "emissions": {
                    "$push": {
                        "year": "$year",
                        "co2_emissions": "$co2_emissions"
                    }
                }
            }},
            {"$match": {"emissions": {"$size": 2}}},  # Only countries with data for both years
            {"$project": {
                "country": "$_id",
                "year1_emissions": {
                    "$arrayElemAt": [
                        {
                            "$filter": {
                                "input": "$emissions",
                                "cond": {"$eq": ["$$this.year", year1]}
                            }
                        }, 0
                    ]
                },
                "year2_emissions": {
                    "$arrayElemAt": [
                        {
                            "$filter": {
                                "input": "$emissions",
                                "cond": {"$eq": ["$$this.year", year2]}
                            }
                        }, 0
                    ]
                }
            }},
            {"$project": {
                "country": 1,
                "year1_value": "$year1_emissions.co2_emissions",
                "year2_value": "$year2_emissions.co2_emissions",
                "change": {
                    "$subtract": ["$year2_emissions.co2_emissions", "$year1_emissions.co2_emissions"]
                },
                "percent_change": {
                    "$multiply": [
                        {
                            "$divide": [
                                {"$subtract": ["$year2_emissions.co2_emissions", "$year1_emissions.co2_emissions"]},
                                "$year1_emissions.co2_emissions"
                            ]
                        },
                        100
                    ]
                }
            }},
            {"$sort": {"year2_value": -1}},
            {"$limit": limit}
        ]
        
        comparison_data = await emissions_collection.aggregate(pipeline).to_list(limit)
        
        return {
            "type": "comparison",
            "title": f"CO2 Emissions Comparison: {year1} vs {year2}",
            "data": comparison_data,
            "years": [year1, year2],
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching emissions comparison: {str(e)}")

@router.get("/countries")
async def get_countries(db=Depends(get_database)):
    """Get list of available countries"""
    
    try:
        emissions_collection = db["emissions"]
        countries = await emissions_collection.distinct("country")
        return {"countries": sorted(countries)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching countries: {str(e)}")

@router.get("/years")
async def get_available_years(db=Depends(get_database)):
    """Get list of available years"""
    
    try:
        emissions_collection = db["emissions"]
        years = await emissions_collection.distinct("year")
        return {"years": sorted(years)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching years: {str(e)}")