# Ticket Submission Form — Setup

## 1. Install dependencies
```bash
npm install axios @tanstack/react-query lucide-react
npx shadcn@latest add button input textarea label select card alert
```
(shadcn's CLI drops components into `src/components/ui/`, matching the imports in `TicketForm.jsx`.)

## 2. Wrap your app in a QueryClientProvider
In `main.jsx` / `App.jsx`, wherever your app root is:
```jsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient();

<QueryClientProvider client={queryClient}>
  <App />
</QueryClientProvider>
```

## 3. Set the API base URL
Create `.env`:
```
VITE_API_BASE_URL=http://localhost:8000/api
```
Update it to Member 2's actual endpoint once it's up. Adjust `.post("/tickets", ...)` in
`src/api/ticketApi.js` if the real route path differs.

## 4. Drop in the files
Copy this folder's `src/` contents into your project's `src/`, then render:
```jsx
import TicketForm from "@/components/TicketForm";

<TicketForm />
```

## Files
- `src/api/ticketApi.js` — axios client + `createTicket()` call
- `src/lib/validateTicket.js` — form validation rules
- `src/components/TicketForm.jsx` — the form UI, wired to axios via TanStack Query's `useMutation`

## Expected API contract
**Request** — `POST /tickets`
```json
{
  "title": "VPN Connection Failing on Corporate Network",
  "description": "Unable to connect to VPN since this morning...",
  "requesterEmail": "john.doe@company.com",
  "department": "IT"
}
```
**Response (success)**
```json
{ "ticketId": "T-2026-4521" }
```
Confirm this shape with Member 2 — adjust the field name read in `TicketForm.jsx`
(`mutation.data?.ticketId`) if their API returns something different (e.g. `id`).
