import axios from 'axios';

const BACKEND_URL = 'http://localhost:8001/api';

const api = axios.create({
  baseURL: BACKEND_URL,
});

export const getProducts = async () => {
  const response = await api.get('/products');
  return response.data;
};

export const placeOrder = async (orderData) => {
  const response = await api.post('/orders', orderData);
  return response.data;
};

export const getOrders = async () => {
  const response = await api.get('/orders');
  return response.data;
};
