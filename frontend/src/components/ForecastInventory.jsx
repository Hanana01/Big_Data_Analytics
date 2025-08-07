import * as React from 'react';
import { useState } from 'react';
import { LineChart } from '@mui/x-charts/LineChart';
import { Button, CircularProgress } from '@mui/material';
import { PieChart, Pie, Cell, Legend, Tooltip } from 'recharts';

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
    const res = await fetch(`http://localhost:5000/api/inventory/forecast-inventory?product_id=${pid}&store_id=${storeId}`);
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
          <select
            required
            value={storeId}
            onChange={(e) => setStoreId(e.target.value)}
            className="w-40 p-2 border border-gray-300 rounded"
          >
            <option value="" disabled>
              Select Store
            </option>
            {[1, 2, 3, 4, 5].map((id) => (
              <option key={id} value={id}>
                Store {id}
              </option>
            ))}
          </select>
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
  <h2 className="text-xl font-semibold mb-4 text-gray-700">📊 Inventory Optimization Metrics (Last 30 Days)</h2>
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
        data: chartData.chart.map((_, idx) => chartData.reorder_point_daily[idx]),
        label: 'Reorder Point',
        color: '#FF0000',
        curve: 'linear',
      },
      {
        data: chartData.chart.map((item) => item.inventory_level),
        label: 'predicted Inventory level',
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
      // {
      //   data: chartData.chart.map((item) => item.units_sold),
      //   label: 'Sold Units',
      //   color: '#00BFFF',
      //   curve: 'linear',
      // },
{
  data: chartData.chart.map((item) => item.xgb_sales_pred),
  label: 'Predicted Sales',
  color: '#FF6347', // Tomato red or change as needed
  curve: 'linear',
},

    ]}
    height={350}
    // tooltip
    tooltip={{
    trigger: 'item',
    renderTooltip: ({ index }) => {
      const item = chartData.chart[index];
      const reorderPoint = chartData.reorder_point_daily
        ? chartData.reorder_point_daily[index]
        : chartData.reorder_point;
      const status = item.inventory_level <= reorderPoint ? '🚨 Reorder Needed' : '✅ OK';
      return (
        <div className="bg-white p-2 rounded shadow text-sm text-gray-800">
          <p><strong>Date:</strong> {item.Date}</p>
          <p><strong>Inventory:</strong> {item.inventory_level}</p>
          <p><strong>Reorder Point:</strong> {reorderPoint.toFixed(2)}</p>
          <p><strong>Status:</strong> {status}</p>
        </div>
      );
    }
  }}
    legend
  />
</div>

      <div className="mt-6 bg-white p-4 rounded-lg shadow border border-gray-100 max-h-64 overflow-auto">
  <h3 className="text-lg font-semibold mb-3 text-gray-700">📅 Daily Reorder Status</h3>
   <table className="w-full text-sm text-left border-collapse border border-gray-300">     <thead>       <tr>
        <th className="border border-gray-300 px-2 py-1">Date</th>
        <th className="border border-gray-300 px-2 py-1">Predicted Inventory Level</th>
         <th className="border border-gray-300 px-2 py-1">Reorder Point</th>
         <th className="border border-gray-300 px-2 py-1">Status</th>
      </tr>     </thead>
    <tbody>
       {data.chart.map((item, idx) => {
        const reorderPoint = data.reorder_point_daily ? data.reorder_point_daily[idx] : data.reorder_point;
        const status = item.inventory_level <= reorderPoint ? '🚨 Reorder Needed' : '✅ OK';         
        const statusColor = item.inventory_level <= reorderPoint ? 'text-red-600' : 'text-green-600';
        return (
          <tr key={item.Date}>
            <td className="border border-gray-300 px-2 py-1">{item.Date}</td>
          <td className="border border-gray-300 px-2 py-1">{item.inventory_level}</td>
             <td className="border border-gray-300 px-2 py-1">{Math.round(reorderPoint)}</td>
             <td className={`border border-gray-300 px-2 py-1 font-semibold ${statusColor}`}>{status}</td>
          </tr>
        );       })}
    </tbody>
   </table>
    </div>


          {/* Cost Breakdown Pie Chart */}
<div className="bg-white p-6 rounded-lg shadow border border-gray-100 mt-8">
  {/* Dynamic Alert Message */}
  {(() => {
    const holding = data.total_holding_cost;
    const ordering = data.total_ordering_cost;
    let alertMessage = '';
    let bgColor = 'bg-yellow-50';
    let borderColor = 'border-yellow-400';
    let textColor = 'text-yellow-800';

    if (holding > 1.5 * ordering) {
      alertMessage =
        '⚠️ High holding costs detected. Consider reducing overstock or ordering in smaller batches.';
      bgColor = 'bg-red-50';
      borderColor = 'border-red-400';
      textColor = 'text-red-800';
    } else if (ordering > 1.5 * holding) {
      alertMessage =
        '⚠️ High ordering costs detected. Consider increasing order quantity or reducing order frequency.';
      bgColor = 'bg-orange-50';
      borderColor = 'border-orange-400';
      textColor = 'text-orange-800';
    } else {
      alertMessage =
        '✅ Good balance between holding and ordering costs. Keep monitoring to maintain efficiency.';
      bgColor = 'bg-green-50';
      borderColor = 'border-green-400';
      textColor = 'text-green-800';
    }

    return (
      <div className={`${bgColor} border-l-4 ${borderColor} ${textColor} p-4 mb-4 rounded`} role="alert">
        <strong className="font-bold">💡 Inventory Insight:</strong>
        <span className="block sm:inline">{' ' + alertMessage}</span>
      </div>
    );
  })()}

  <h2 className="text-xl font-semibold mb-4 text-gray-700">💰 Cost Breakdown</h2>
  <PieChart width={400} height={300}>
    <Pie
      data={[
        { name: 'Holding Cost', value: data.total_holding_cost },
        { name: 'Ordering Cost', value: data.total_ordering_cost },
      ]}
      dataKey="value"
      nameKey="name"
      cx="50%"
      cy="50%"
      outerRadius={100}
      label
    >
      <Cell fill="#8884d8" />
      <Cell fill="#82ca9d" />
    </Pie>
    <Tooltip />
    <Legend />
  </PieChart>
</div>
{/* Stockout and Overstock Summary */}
<div className="bg-white p-6 rounded-lg shadow border border-gray-100 mt-8">
  <h2 className="text-xl font-semibold mb-4 text-gray-700">📊 Stockout vs Overstock Days (Last 30 Days)</h2>
  <p className="mb-4 text-gray-700">
    Total Stockout Days: <strong>{data.stockout_days}</strong><br />
    Total Overstock Days: <strong>{data.overstock_days}</strong>
  </p>

  {/* Pie chart for Stockout vs Overstock */}
  <PieChart width={800} height={250}>
    <Pie
      data={[
        { name: 'Stockout Days', value: data.stockout_days },
        { name: 'Overstock Days', value: data.overstock_days },
        { name: 'Normal Stock Days', value: 30 - (data.stockout_days + data.overstock_days) },
      ]}
      dataKey="value"
      nameKey="name"
      cx="50%"
      cy="50%"
      outerRadius={80}
      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
    >
      <Cell fill="#FF4136" /> {/* Red for Stockout */}
      <Cell fill="#FF851B" /> {/* Orange for Overstock */}
      <Cell fill="#2ECC40" /> {/* Green for Normal */}
    </Pie>
    <Tooltip />
    <Legend verticalAlign="bottom" height={36} />
  </PieChart>
</div>

    
        </>
      )}
    </div>
  );
}
