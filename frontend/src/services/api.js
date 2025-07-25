import axios from "axios";

const BASE_URL = "http://127.0.0.1:5000/api";

// Reusable GET request
export const fetchData = (module, endpoint = "") =>
  axios.get(`${BASE_URL}/${module}/${endpoint}`).then(res => res.data);

// Reusable POST request
export const postData = (module, endpoint = "", payload) =>
  axios.post(`${BASE_URL}/${module}/${endpoint}`, payload).then(res => res.data);

// Get image URL
export const getImageUrl = (module, store, product, chartType) =>
  `${BASE_URL}/${module}/images/${store}/${encodeURIComponent(product)}/${chartType}`;

// Get download URL
export const getDownloadUrl = (module, store, product) =>
  `${BASE_URL}/${module}/download/${store}/${encodeURIComponent(product)}`;
