import React from 'react';
import { Link } from 'react-router-dom';

import inventoryImg from '../assets/inventory.webp';
import salesImg from '../assets/sales.jpeg';
import customersImg from '../assets/customers.jpg';

const Home = () => {
  return (
    <div className="p-8 min-h-screen bg-gray-100 font-sans flex flex-col items-center justify-center">
        <h1 className="max-w-5xl text-5xl font-extrabold text-center text-gray-800 mb-12 leading-tight">
        📊 Welcome to <span className="text-purple-600">EcomPulse</span> <br />
        <span className="text-blue-600">Forecast Sales</span>, <span className="text-green-600">Optimize Inventory</span>, and <span className="text-pink-600">Know Your Customers</span>
      </h1>


      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-5xl mx-auto">
        <Link to="/sales" className="bg-white rounded-2xl shadow p-4 hover:shadow-lg transition">
          <img src={salesImg} alt="Sales" className="w-full h-40 object-contain mb-4" />
          <h2 className="text-xl font-semibold text-center text-gray-700">Sales</h2>
        </Link>
        <Link to="/inventory" className="bg-white rounded-2xl shadow p-4 hover:shadow-lg transition">
          <img src={inventoryImg} alt="Inventory" className="w-full h-40 object-contain mb-4" />
          <h2 className="text-xl font-semibold text-center text-gray-700">Inventory</h2>
        </Link>
        <Link to="/customers" className="bg-white rounded-2xl shadow p-4 hover:shadow-lg transition">
          <img src={customersImg} alt="Customers" className="w-full h-40 object-contain mb-4" />
          <h2 className="text-xl font-semibold text-center text-gray-700">Customers</h2>
        </Link>
      </div>
    </div>
  );
};

export default Home;
