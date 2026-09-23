import axios from "axios";

const classifyClient = axios.create({
    baseURL: import.meta.env.VITE_CLASSIFY_API_BASE_URL || "http://localhost:8001",
    headers: {
        "Content-Type": "application/json",
    },
    timeout: 10000,
});

/**
 * Sends a ticket description to the classification engine
 * @param {string} description - the ticket description to classify
 * @returns {Promise<{ department: string, confidence: number, matched_symptoms: string[], suggested_priority: string, needs_clarification: boolean, clarifying_questions: string[] }>}
 */
export async function classifyTicket(description) {
    const { data } = await classifyClient.get("/diagnose", { params: { text: description } });
    return {
        department: data.predicted_category || "Pending",
        confidence: data.confidence ?? null,
        matched_symptoms: data.matched_symptoms || [],
        suggested_priority: data.suggested_priority || "Medium",
        needs_clarification: data.needs_clarification || false,
        clarifying_questions: data.clarifying_questions || []
    };
}

export default classifyClient;