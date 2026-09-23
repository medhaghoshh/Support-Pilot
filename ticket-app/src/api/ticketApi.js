import axios from "axios";

// Point this at Member 2's API base URL. Keep it in an env var so it's
// easy to swap between local, staging, and prod without touching code.
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

/**
 * Submits a new ticket.
 * @param {{ title: string, description: string, requesterEmail: string, department: string }} payload
 * @returns {Promise<{ ticketId: string }>}
 */
export async function createTicket(payload) {
  const { data } = await apiClient.post("/tickets", payload);
  return data;
}

export default apiClient;
