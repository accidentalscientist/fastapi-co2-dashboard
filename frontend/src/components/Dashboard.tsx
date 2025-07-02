import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw, Activity, Globe, Zap, TrendingUp, Database, ExternalLink, Info, Calendar, Users } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { apiClient, type DashboardStats, type ChartData, type ComparisonData } from '@/api/client';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface DashboardProps {
  className?: string;
}

export function Dashboard({ className }: DashboardProps) {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [co2TimeSeries, setCO2TimeSeries] = useState<ChartData | null>(null);
  const [renewableData, setRenewableData] = useState<ChartData | null>(null);
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      setError(null);
      
      const [statsData, co2Data, renewableEnergyData, emissionsComparison] = await Promise.all([
        apiClient.getDashboardStats(),
        apiClient.getCO2TimeSeries({ start_year: 2018, end_year: 2023 }),
        apiClient.getRenewableEnergyData({ year: 2023, limit: 12 }),
        apiClient.getEmissionsComparison({ compare_years: [2020, 2023], limit: 10 })
      ]);

      setStats(statsData);
      setCO2TimeSeries(co2Data);
      setRenewableData(renewableEnergyData);
      setComparisonData(emissionsComparison);
      setLastUpdate(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchData();
  };

  useEffect(() => {
    fetchData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatLineChartData = (chartData: ChartData) => {
    const years = chartData.data.labels;
    const result = years.map(year => {
      const dataPoint: any = { year };
      chartData.data.datasets.forEach(dataset => {
        const index = years.indexOf(year);
        dataPoint[dataset.label] = dataset.data[index] || 0;
      });
      return dataPoint;
    });
    return result;
  };

  const formatBarChartData = (chartData: ChartData) => {
    return chartData.data.labels.map((label, index) => ({
      country: label,
      value: chartData.data.datasets[0]?.data[index] || 0
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span>Loading sustainability data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center space-y-4">
          <p className="text-red-600">Error: {error}</p>
          <Button onClick={fetchData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* Enhanced Header */}
      <div className="space-y-4">
        <div className="flex justify-between items-start">
          <div className="space-y-2">
            <div className="flex items-center space-x-3">
              <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                Global Sustainability Dashboard
              </h1>
              <Badge variant="secondary" className="text-xs">
                <Database className="h-3 w-3 mr-1" />
                Real Data
              </Badge>
            </div>
            <p className="text-lg text-muted-foreground max-w-2xl">
              Real-time insights into global environmental metrics, powered by authoritative data sources including Our World in Data and World Bank Open Data APIs.
            </p>
            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
              <div className="flex items-center space-x-1">
                <Globe className="h-4 w-4" />
                <span>50+ Countries</span>
              </div>
              <div className="flex items-center space-x-1">
                <Calendar className="h-4 w-4" />
                <span>2010-2023 Coverage</span>
              </div>
              <div className="flex items-center space-x-1">
                <Users className="h-4 w-4" />
                <span>Population & Economic Data</span>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              {lastUpdate && (
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Activity className="h-4 w-4 text-green-500" />
                  <span>Updated: {lastUpdate.toLocaleTimeString()}</span>
                </div>
              )}
              <div className="flex items-center space-x-2 text-xs text-muted-foreground mt-1">
                <Database className="h-3 w-3" />
                <span>Our World in Data + World Bank APIs</span>
                <ExternalLink className="h-3 w-3" />
              </div>
            </div>
            <Button onClick={handleRefresh} disabled={refreshing} size="lg" className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700">
              <RefreshCw className={cn("h-4 w-4 mr-2", refreshing && "animate-spin")} />
              Refresh Data
            </Button>
          </div>
        </div>
        
        {/* Data Source Attribution */}
        <Alert className="border-green-200 bg-green-50 dark:bg-green-900/20">
          <Info className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800 dark:text-green-200">
            <div className="flex items-center justify-between">
              <span>
                Data sourced from <strong>Our World in Data</strong> (CO₂ emissions) and <strong>World Bank Open Data API</strong> (renewable energy) - authoritative global environmental datasets.
              </span>
              <Button variant="ghost" size="sm" className="text-green-700 hover:text-green-800">
                <ExternalLink className="h-3 w-3 mr-1" />
                View Source
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      </div>

      {/* Enhanced Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="border-l-4 border-l-blue-500 hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-medium text-blue-700 dark:text-blue-300">Total Countries</CardTitle>
              <div className="h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                <Globe className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="text-3xl font-bold text-blue-900 dark:text-blue-100">{stats.total_countries}</div>
              <p className="text-sm text-muted-foreground flex items-center">
                <Calendar className="h-3 w-3 mr-1" />
                Coverage for {stats.latest_year}
              </p>
              <Badge variant="secondary" className="text-xs bg-blue-50 text-blue-700 border-blue-200">
                Global Dataset
              </Badge>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-red-500 hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-medium text-red-700 dark:text-red-300">Global CO₂ Emissions</CardTitle>
              <div className="h-10 w-10 rounded-full bg-red-100 dark:bg-red-900 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-red-600 dark:text-red-400" />
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="text-3xl font-bold text-red-900 dark:text-red-100">
                {(stats.total_co2_emissions / 1000).toFixed(1)}Gt
              </div>
              <p className="text-sm text-muted-foreground flex items-center">
                <Activity className="h-3 w-3 mr-1" />
                Total for {stats.latest_year}
              </p>
              <Badge variant="secondary" className="text-xs bg-red-50 text-red-700 border-red-200">
                Carbon Emissions
              </Badge>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-green-500 hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-medium text-green-700 dark:text-green-300">Renewable Energy</CardTitle>
              <div className="h-10 w-10 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
                <Zap className="h-5 w-5 text-green-600 dark:text-green-400" />
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="text-3xl font-bold text-green-900 dark:text-green-100">
                {stats.avg_renewable_percentage.toFixed(1)}%
              </div>
              <p className="text-sm text-muted-foreground flex items-center">
                <Globe className="h-3 w-3 mr-1" />
                Global average
              </p>
              <Badge variant="secondary" className="text-xs bg-green-50 text-green-700 border-green-200">
                Clean Energy
              </Badge>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-purple-500 hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-medium text-purple-700 dark:text-purple-300">Best Performer</CardTitle>
              <div className="h-10 w-10 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
                <Activity className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="text-3xl font-bold text-purple-900 dark:text-purple-100">
                {stats.top_performers[0]?.country || 'N/A'}
              </div>
              <p className="text-sm text-muted-foreground flex items-center">
                <TrendingUp className="h-3 w-3 mr-1" />
                {stats.top_performers[0]?.co2_per_capita.toFixed(2)} t/capita
              </p>
              <Badge variant="secondary" className="text-xs bg-purple-50 text-purple-700 border-purple-200">
                Lowest Emissions
              </Badge>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CO2 Time Series */}
        {co2TimeSeries && (
          <Card>
            <CardHeader>
              <CardTitle>{co2TimeSeries.title}</CardTitle>
              <CardDescription>
                CO₂ emissions trend for top emitting countries
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={formatLineChartData(co2TimeSeries)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis />
                  <Tooltip formatter={(value: number) => [`${value.toFixed(0)} Mt`, 'CO₂ Emissions']} />
                  <Legend />
                  {co2TimeSeries.data.datasets.slice(0, 5).map((dataset) => (
                    <Line
                      key={dataset.label}
                      type="monotone"
                      dataKey={dataset.label}
                      stroke={dataset.borderColor}
                      strokeWidth={2}
                      dot={{ r: 3 }}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {/* Renewable Energy */}
        {renewableData && (
          <Card>
            <CardHeader>
              <CardTitle>{renewableData.title}</CardTitle>
              <CardDescription>
                Countries leading in renewable energy adoption
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={formatBarChartData(renewableData)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="country" 
                    angle={-45}
                    textAnchor="end"
                    height={100}
                  />
                  <YAxis />
                  <Tooltip 
                    formatter={(value: number) => [`${value.toFixed(1)}%`, 'Renewable Energy']}
                  />
                  <Bar dataKey="value" fill="#4CAF50" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Comparison Table */}
      {comparisonData && (
        <Card>
          <CardHeader>
            <CardTitle>{comparisonData.title}</CardTitle>
            <CardDescription>
              Year-over-year comparison of CO₂ emissions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Country</th>
                    <th className="text-right p-2">{comparisonData.years[0]}</th>
                    <th className="text-right p-2">{comparisonData.years[1]}</th>
                    <th className="text-right p-2">Change</th>
                    <th className="text-right p-2">% Change</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonData.data.map((row, index) => (
                    <tr key={index} className="border-b">
                      <td className="p-2 font-medium">{row.country}</td>
                      <td className="text-right p-2">{row.year1_value.toFixed(0)} Mt</td>
                      <td className="text-right p-2">{row.year2_value.toFixed(0)} Mt</td>
                      <td className={cn(
                        "text-right p-2",
                        row.change > 0 ? "text-red-600" : "text-green-600"
                      )}>
                        {row.change > 0 ? '+' : ''}{row.change.toFixed(0)} Mt
                      </td>
                      <td className={cn(
                        "text-right p-2",
                        row.percent_change > 0 ? "text-red-600" : "text-green-600"
                      )}>
                        {row.percent_change > 0 ? '+' : ''}{row.percent_change.toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Footer with Data Attribution */}
      <Card className="border-t-4 border-t-green-500 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-950 dark:to-blue-950">
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <h3 className="text-lg font-semibold text-green-900 dark:text-green-100 flex items-center">
                  <Database className="h-5 w-5 mr-2" />
                  Data Sources & Attribution
                </h3>
                <p className="text-sm text-green-700 dark:text-green-300 max-w-2xl">
                  This dashboard presents real environmental data from authoritative global sources, 
                  processed and visualized to provide insights into climate action and sustainability trends.
                </p>
              </div>
              <Badge variant="secondary" className="bg-green-100 text-green-800 border-green-300">
                <Activity className="h-3 w-3 mr-1" />
                Real-time Data
              </Badge>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
              <div className="space-y-2">
                <h4 className="font-medium text-green-900 dark:text-green-100 flex items-center">
                  <Globe className="h-4 w-4 mr-2" />
                  Primary Data Source
                </h4>
                <div className="text-green-700 dark:text-green-300 space-y-1">
                  <p><strong>Our World in Data</strong></p>
                  <p>CO₂ emissions and population data</p>
                  <p><strong>World Bank Open Data API</strong></p>
                  <p>Renewable energy and economic indicators</p>
                </div>
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium text-green-900 dark:text-green-100 flex items-center">
                  <Calendar className="h-4 w-4 mr-2" />
                  Data Coverage
                </h4>
                <div className="text-green-700 dark:text-green-300 space-y-1">
                  <p><strong>Time Range:</strong> 2010-2023</p>
                  <p><strong>Countries:</strong> 50+ nations</p>
                  <p><strong>Last Updated:</strong> {lastUpdate?.toLocaleDateString()}</p>
                </div>
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium text-green-900 dark:text-green-100 flex items-center">
                  <Info className="h-4 w-4 mr-2" />
                  Data Quality
                </h4>
                <div className="text-green-700 dark:text-green-300 space-y-1">
                  <p><strong>Source:</strong> Official government data</p>
                  <p><strong>Standards:</strong> UNFCCC compliance</p>
                  <p><strong>Processing:</strong> Real-time validation</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between text-xs text-green-600 dark:text-green-400 pt-4 border-t border-green-200 dark:border-green-800">
              <div className="flex items-center space-x-4">
                <span>© 2024 Global Sustainability Dashboard</span>
                <span>•</span>
                <span>Powered by Our World in Data & World Bank APIs</span>
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="ghost" size="sm" className="text-green-700 hover:text-green-800 h-6 px-2">
                  <ExternalLink className="h-3 w-3 mr-1" />
                  API Docs
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}