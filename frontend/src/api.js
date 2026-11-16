
import axios from "axios";

const API = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000",
  timeout: 60000,
});

export const uploadDocument = async (file) => {
  const formData = new FormData();

  formData.append("file", file);

  const response = await API.post(
    "/api/documents/upload",
    formData
  );

  return response.data;
};

export const checkBackend = async () => {
  const response = await API.get("/api/health");
  return response.data;
};

export default API;
