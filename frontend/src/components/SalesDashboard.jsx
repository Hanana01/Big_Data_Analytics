import React, { useEffect, useState } from "react";
import {
  fetchData,
  getImageUrl,
  getDownloadUrl,
} from "../services/api";
import "./SalesDashboard.css";

const SalesDashboard = () => {
  const [stores, setStores] = useState([]);
  const [products, setProducts] = useState([]);
  const [storeId, setStoreId] = useState("");
  const [productId, setProductId] = useState("");
  const [salesImage, setSalesImage] = useState(null);
  const [profitImage, setProfitImage] = useState(null);
  const [summary, setSummary] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchData("sales", "stores").then(setStores);
    fetchData("sales", "products").then(setProducts);
  }, []);

  const handleLoad = async () => {
    setError("");
    if (!storeId || !productId) {
      setError("Please select both Store and Product.");
      return;
    }

    const selectedProduct = products.find((p) => p.id.toString() === productId);
    const productName = selectedProduct?.name || "";

    setSalesImage(getImageUrl("sales", storeId, productId, "sales"));
    setProfitImage(getImageUrl("sales", storeId, productId, "profit"));

    try {
      const res = await fetchData("sales", "summary");
      const filtered = res.filter(
        (row) =>
          row["Store"] === parseInt(storeId) &&
          row["Product"] === productName
      );
      setSummary(filtered);
    } catch (err) {
      setError("Error fetching summary.");
    }
  };

  return (
    <div className="dashboard-container">
      <h1>📊 Sales Prediction Dashboard</h1>

      <div className="selectors">
        <label>
          Store ID:
          <select value={storeId} onChange={(e) => setStoreId(e.target.value)}>
            <option value="">Select Store</option>
            {stores.map((id) => (
              <option key={id} value={id}>
                {id}
              </option>
            ))}
          </select>
        </label>

        <label>
          Product:
          <select
            value={productId}
            onChange={(e) => setProductId(e.target.value)}
          >
            <option value="">Select Product</option>
            {products.map((prod) => (
              <option key={prod.id} value={prod.id}>
                {prod.name}
              </option>
            ))}
          </select>
        </label>

        <button onClick={handleLoad}>Load Charts</button>
      </div>

      {error && <p className="error">{error}</p>}

      <div className="charts">
        {salesImage && (
          <div className="chart">
            <h3>Sales Forecast</h3>
            <img src={salesImage} alt="Sales Forecast" />
          </div>
        )}

        {profitImage && (
          <div className="chart">
            <h3>Profit Forecast</h3>
            <img src={profitImage} alt="Profit Forecast" />
          </div>
        )}
      </div>

      <div className="summary-cards">
        {summary.length > 0 &&
          Object.entries(summary[0]).map(([key, value]) => (
            <div key={key} className="card">
              <h4>{key}</h4>
              <p>{value}</p>
            </div>
          ))}
      </div>

        {salesImage && profitImage && (
    <a
      className="download-btn"
      href={getDownloadUrl("sales", storeId, productId)}
      download
    >
      ⬇️ Download Prediction CSV
    </a>
  )}
    </div>
  );
};

export default SalesDashboard;
