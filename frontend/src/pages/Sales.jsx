import React, { useEffect, useState } from 'react';
import api from '../services/api';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer
} from 'recharts';

const Sales = () => {
  const [forecast, setForecast] = useState([]);

  useEffect(() => {
  api.get("/sales_prediction/")
    .then(res => {
      console.log("Raw data from backend:", res.data);  // Log raw response data

      const formatted = res.data.map(item => ({
        ...item,
        ds: new Date(item.ds).toISOString().split('T')[0]
      }));

      console.log("Formatted data:", formatted);  // Log formatted data before setting state
      setForecast(formatted);
    })
    .catch(err => console.error("Error fetching forecast:", err));
}, []);


  return (
    <div style={{ padding: '2rem' }}>
      <h2>30-Day Sales Forecast</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={forecast}>
          <CartesianGrid stroke="#ccc" />
          <XAxis dataKey="ds" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="yhat" stroke="#8884d8" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default Sales;
