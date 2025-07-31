// import React from 'react';
// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// import Navbar from './components/Navbar';
// import Sales from './pages/Sales';
// import Dashboard from './pages/Dashboard';

// function App() {
//   return (
//     <Router>
//       <Navbar />
//       <Routes>
//         <Route path="/" element={<Dashboard />} />
//         <Route path="/sales" element={<Sales />} />
//       </Routes>
//     </Router>
//   );
// }

// export default App;
import React from 'react';
import ForecastInventory from './components/ForecastInventory';

function App() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <ForecastInventory />
    </div>
  );
}

export default App;
