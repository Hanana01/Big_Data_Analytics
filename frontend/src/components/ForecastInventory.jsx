import * as React from 'react';
import { useState } from 'react';
import { LineChart } from '@mui/x-charts/LineChart';
import { TextField, Button, CircularProgress } from '@mui/material';

export default function ForecastInventoryMui() {
  const [pid, setPid] = useState('');
  const [storeId, setStoreId] = useState(''); 
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
const productsList = [
  { id: 1, name: "Coat" },
  { id: 2, name: "Hoodie" },
  { id: 3, name: "Jacket" },
  { id: 4, name: "Overcoat" },
  { id: 5, name: "Blazer" },
  { id: 6, name: "Blouse" },
  { id: 7, name: "Shirt" },
  { id: 8, name: "Jeans" },
  { id: 9, name: "Trousers" },
  { id: 10, name: "T-shirt" },
  { id: 11, name: "Shorts" },
  { id: 12, name: "Skirt" },
  { id: 13, name: "Saree" },
  { id: 14, name: "Bag" },
  { id: 15, name: "Belt" },
  { id: 16, name: "Gloves" },
  { id: 17, name: "Fragrances" },
  { id: 18, name: "Wristwear" },
  { id: 19, name: "Sunglasses" },
  { id: 20, name: "Hat" },
];
  const fetchData = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:5000/forecast-inventory?product_id=${pid}&store_id=${storeId}`);  // changed here
      const resJson = await res.json();
      if (!res.ok) throw new Error(resJson.error || 'Failed to fetch');
      setData(resJson);
      setError('');
    } catch (e) {
      setData(null);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = data;
  const xLabels = data ? chartData.chart.map((item) => item.Date) : [];

  return (
    <div className="container mx-auto mt-12 space-y-12 px-4 pb-12">
      {/* Always-visible Form */}
      <div className="bg-white p-6 rounded-lg shadow border border-gray-200 flex items-center justify-between">
        <h1 className='font-bold text-xl w-full'>📈 Demand Forecast & Inventory Dashboard</h1>
        <form onSubmit={fetchData} className="w-full flex flex-wrap gap-10 items-end mb-4 justify-end">
          <select
            required
            value={pid}
            onChange={(e) => setPid(e.target.value)}
            className="w-40 p-2 border border-gray-300 rounded"
          >
            <option value="" disabled>Select Product</option>
            {productsList.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
          <TextField
            label="Store ID"                       
            type="number"
            value={storeId}                         
            onChange={(e) => setStoreId(e.target.value)} 
            size="small"
            inputProps={{ min: 0, max: 5 }}
            required
            className="w-40"
          />
          <Button
            type="submit"
            variant="contained"
            className="!bg-indigo-600 !text-white hover:!bg-indigo-700 transition-all"
          >
            Load Data
          </Button>
        </form>
        {error && (
          <p className="text-red-600 font-semibold">
            ❌ {error === 'Failed to fetch' ? 'Backend not reachable or crashed' : error}
          </p>
        )}
      </div>

      {/* Loading Spinner */}
      {loading && (
        <div className="flex flex-col items-center justify-center mt-24">
          <CircularProgress />
          <p className="mt-4 text-gray-500 text-lg">Loading data...</p>
        </div>
      )}

      {/* Summary & Charts if Data Exists */}
      {!loading && data && (
        <>
          {/* Summary Card */}
          <div className="container bg-white p-6 rounded-lg shadow border border-gray-100 space-y-2">
            <h2 className="text-2xl font-bold mb-2 text-gray-800">📦 Inventory Summary</h2>
            <p><span className="font-medium">Date Range:</span> {chartData.date_range.from} → {chartData.date_range.to}</p>
            <hr className="my-2" />
            <p><span className="font-medium">EOQ:</span> {chartData.eoq}</p>
            <p><span className="font-medium">Safety Stock:</span> {chartData.safety_stock}</p>
            <p><span className="font-medium">Reorder Point:</span> {chartData.reorder_point}</p>
            <p><span className="font-medium">Current Inventory:</span> {chartData.daily_inventory_levels}</p>
            <p>
              <span className="font-medium">Status:</span>{' '}
              <span className={chartData.reorder_needed ? 'text-red-600 font-semibold' : 'text-green-600 font-semibold'}>
                {chartData.reorder_needed ? '🚨 Reorder Needed' : '✅ Inventory Sufficient'}
              </span>
            </p>
          </div>

          {/* Demand Forecast Chart */}
          <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">📈 Demand Forecast (Last 30 Days)</h2>
            <LineChart
              xAxis={[{ scaleType: 'band', data: xLabels }]}
              series={[
                {
                  data: chartData.chart.map((item) => item.actual),
                  label: 'Actual Demand',
                  color: '#8884d8',
                  curve: 'linear',
                },
                {
                  data: chartData.chart.map((item) => item.predicted),
                  label: 'Predicted Demand',
                  color: '#82ca9d',
                  curve: 'linear',
                },
              ]}
              height={350}
              tooltip
              legend
            />
          </div>

                {/* Demand Forecast Chart */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">📈 Sold Units vs Predicted Demand (Last 30 Days)</h2>
        <LineChart
            xAxis={[{ scaleType: 'band', data: xLabels }]}
            series={[
            {
                data: chartData.chart.map((item) => item.predicted),
                label: 'Predicted Demand',
              color: '#82ca9d',
                curve: 'linear',
            },
            {
                data: chartData.chart.map((item) => item.units_sold),
                label: 'Sold Units',
                    color: '#00BFFF',
                curve: 'linear',
            },
            ]}
            height={350}
            tooltip
            legend
        />
        </div>


          {/* Inventory Optimization Chart */}
          <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">📊 Inventory Optimization Metrics</h2>
            <LineChart
              xAxis={[{ scaleType: 'band', data: xLabels }]}
              series={[
                {
                  data: chartData.chart.map(() => chartData.eoq),
                  label: 'EOQ',
                  color: '#228B22',
                  curve: 'linear',
                },
                {
                  data: chartData.chart.map(() => chartData.safety_stock),
                  label: 'Safety Stock',
                  color: '#FFA500',
                  curve: 'linear',
                },
                {
                  data: chartData.chart.map(() => chartData.reorder_point),
                  label: 'Reorder Point',
                  color: '#FF0000',
                  curve: 'linear',
                },
                {
                  data: chartData.chart.map(() => chartData.inventory_level),
                  label: 'Current Inventory',
                  color: '#800080',
                  curve: 'linear',
                },
                {
                  data: chartData.chart.map((item) => item.actual),
                  label: 'Actual Demand',
                  color: '#8884d8',
                  curve: 'linear',
                },
                {
                  data: chartData.chart.map((item) => item.predicted),
                  label: 'Predicted Demand',
                  color: '#82ca9d',
                  curve: 'linear',
                },
                {
                  data: chartData.chart.map((item) => item.units_sold),
                  label: 'Sold Units',
                  color: '#00BFFF',
                  curve: 'linear',
                },
              ]}
              height={350}
              tooltip
              legend
            />
          </div>
        </>
      )}
    </div>
  );
}
