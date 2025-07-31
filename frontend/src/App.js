
// import React from "react";
// import SalesDashboard from "./components/SalesDashboard";
// import ForecastInventory from './components/ForecastInventory';
// import './index.css';
// function App() {
//   return (
//     <div className="p-8 font-sans bg-gray-100 min-h-screen space-y-8">
//       <div className="bg-white p-6 rounded-2xl shadow">
//         <h2 className="text-2xl font-semibold text-gray-800 mb-4">📈 Forecast Inventory</h2>
//         <ForecastInventory />
//       </div>

//       <div className="bg-white p-6 rounded-2xl shadow">
//         <h2 className="text-2xl font-semibold text-gray-800 mb-4">📊 Sales Dashboard</h2>
//         <SalesDashboard />
//       </div>
//     </div>
//   );
// }

// export default App;

// // App.jsximport React from 'react';
// import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
// import './index.css';
// import ForecastInventory from './components/ForecastInventory';
// import SalesDashboard from './components/SalesDashboard';
// // import CustomerDashboard from './components/CustomerDashboard';

// function App() {
//   return (
//     <Router>
//       <div className="p-8 font-sans bg-gray-100 min-h-screen flex flex-col items-center">
//         {/* Navigation */}
//         <nav className="mb-8 space-x-6">
//           {[
//             { to: '/inventory', label: 'Inventory' },
//             { to: '/sales', label: 'Sales' },
//             { to: '/customers', label: 'Customers' },
//           ].map(({ to, label }) => (
//             <NavLink
//               key={to}
//               to={to}
//               className={({ isActive }) =>
//                 `px-4 py-2 rounded-lg font-medium transition ${
//                   isActive
//                     ? 'bg-blue-600 text-white shadow-lg'
//                     : 'text-blue-600 hover:bg-blue-100'
//                 }`
//               }
//             >
//               {label}
//             </NavLink>
//           ))}
//         </nav>

//         {/* Routes */}
//         <div className="w-full bg-white p-6 rounded-2xl shadow">
//           <Routes>
//             <Route path="/inventory" element={<ForecastInventory />} />
//             <Route path="/sales" element={<SalesDashboard />} />
//             {/* <Route path="/customers" element={<CustomerDashboard />} /> */}
//             <Route path="*" element={<div className="text-gray-600 text-center text-lg">Welcome! Please select a dashboard.</div>} />
//           </Routes>
//         </div>
//       </div>
//     </Router>
//   );
// }

// export default App;

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './index.css';
import Home from './page/Home';
import ForecastInventory from './components/ForecastInventory';
import SalesDashboard from './components/SalesDashboard';
// import CustomerDashboard from './components/CustomerDashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/inventory" element={<ForecastInventory />} />
        <Route path="/sales" element={<SalesDashboard />} />
        {/* <Route path="/customers" element={<CustomerDashboard />} /> */}
      </Routes>
    </Router>
  );
}

export default App;
