import { classifyTicket } from "@/api/classifyApi";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Loader2, CheckCircle2, AlertCircle, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { createTicket } from "@/api/ticketApi";
import { validateTicket } from "@/lib/validateTicket";

const DEPARTMENTS = ["IT", "HR", "Finance", "Operations", "Engineering", "Other"];
const initialValues = { title: "", description: "", requesterEmail: "", department: "" };

export default function TicketForm({ onTicketCreated }) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createTicket,
    onSuccess: async (ticketData) => {
      // Invalidate and refetch tickets query
      queryClient.invalidateQueries({ queryKey: ["tickets"] });

      // Automatically classify the ticket after it's created
      try {
        const classification = await classifyTicket(ticketData.description);
        console.log("Classification result:", classification);
        if (onTicketCreated) {
          onTicketCreated(ticketData, classification);
        }
      } catch (error) {
        console.error("Classification failed:", error);
        if (onTicketCreated) {
          onTicketCreated(ticketData, { department: "Pending", confidence: 0 });
        }
      }

      setValues(initialValues);
      setErrors({});
    },
  });

  function handleChange(field, value) {
    setValues((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    const validationErrors = validateTicket(values);
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length === 0) {
      // Map our form's field names to what the backend expects
      const payload = {
        subject: values.title,
        description: values.description,
        requester_email: values.requesterEmail,
        department: values.department,
      };
      mutation.mutate(payload);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-5 bg-white dark:bg-zinc-900 border border-gray-250 dark:border-zinc-800 p-6 rounded-2xl shadow-sm text-left">
      {/* Ticket Title */}
      <div className="space-y-1.5">
        <Label htmlFor="title" className="text-xs font-bold text-gray-700 dark:text-zinc-300">Ticket Title</Label>
        <Input
          id="title"
          placeholder="e.g. VPN Connection Failing on Corporate Network"
          value={values.title}
          onChange={(e) => handleChange("title", e.target.value)}
          aria-invalid={!!errors.title}
          className="h-10 text-sm rounded-xl border-gray-305 dark:border-zinc-800 focus:ring-2 focus:ring-indigo-500/20 placeholder:text-gray-400 dark:placeholder:text-zinc-500"
        />
        {errors.title && (
          <p className="text-[11px] text-red-500 font-semibold">{errors.title}</p>
        )}
      </div>

      {/* Description */}
      <div className="space-y-1.5">
        <Label htmlFor="description" className="text-xs font-bold text-gray-700 dark:text-zinc-300">Description</Label>
        <Textarea
          id="description"
          rows={4}
          placeholder="Provide a detailed description of the support request..."
          value={values.description}
          onChange={(e) => handleChange("description", e.target.value)}
          aria-invalid={!!errors.description}
          className="text-sm rounded-xl border-gray-305 dark:border-zinc-800 focus:ring-2 focus:ring-indigo-500/20 resize-none placeholder:text-gray-400 dark:placeholder:text-zinc-500"
        />
        {errors.description && (
          <p className="text-[11px] text-red-500 font-semibold">{errors.description}</p>
        )}
      </div>

      {/* Requester Email & Department Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <Label htmlFor="requesterEmail" className="text-xs font-bold text-gray-700 dark:text-zinc-300">Requester Email</Label>
          <Input
            id="requesterEmail"
            type="email"
            placeholder="john.doe@company.com"
            value={values.requesterEmail}
            onChange={(e) => handleChange("requesterEmail", e.target.value)}
            aria-invalid={!!errors.requesterEmail}
            className="h-10 text-sm rounded-xl border-gray-305 dark:border-zinc-800 focus:ring-2 focus:ring-indigo-500/20 placeholder:text-gray-400 dark:placeholder:text-zinc-500"
          />
          {errors.requesterEmail && (
            <p className="text-[11px] text-red-500 font-semibold">{errors.requesterEmail}</p>
          )}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="department" className="text-xs font-bold text-gray-700 dark:text-zinc-300">Department</Label>
          <Select
            value={values.department}
            onValueChange={(val) => handleChange("department", val)}
          >
            <SelectTrigger
              id="department"
              aria-invalid={!!errors.department}
              className="h-10 text-sm rounded-xl border-gray-305 dark:border-zinc-800 focus:ring-2 focus:ring-indigo-500/20 text-gray-800 dark:text-zinc-200"
            >
              <SelectValue placeholder="Select department" />
            </SelectTrigger>
            <SelectContent className="text-sm bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-xl shadow-lg">
              {DEPARTMENTS.map((dept) => (
                <SelectItem key={dept} value={dept}>{dept}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.department && (
            <p className="text-[11px] text-red-500 font-semibold">{errors.department}</p>
          )}
        </div>
      </div>

      {/* Error / Success Alerts */}
      {mutation.isError && (
        <Alert variant="destructive" className="py-2.5 rounded-xl border border-rose-200/50 bg-rose-50/50 dark:bg-rose-950/15">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <AlertTitle className="text-xs font-bold text-red-900 dark:text-rose-400">Submission Error</AlertTitle>
          <AlertDescription className="text-[11px] text-red-700 dark:text-rose-500 mt-0.5">
            {mutation.error?.response?.data?.message || "Could not submit ticket. Please check your connection."}
          </AlertDescription>
        </Alert>
      )}

      {mutation.isSuccess && (
        <Alert className="border-emerald-200 dark:border-emerald-900 bg-emerald-50/40 dark:bg-emerald-950/15 py-2.5 rounded-xl">
          <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
          <AlertTitle className="text-xs font-bold text-emerald-950 dark:text-emerald-400">Success!</AlertTitle>
          <AlertDescription className="text-[11px] text-emerald-700 dark:text-emerald-400 mt-0.5">
            Ticket #{mutation.data?.ticket_id} submitted and RAG execution started.
          </AlertDescription>
        </Alert>
      )}

      {/* Submit Button */}
      <div className="pt-2">
        <Button
          type="submit"
          id="submit-ticket-btn"
          disabled={mutation.isPending}
          className="w-full h-10 rounded-xl bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-600 dark:hover:bg-indigo-700 text-white text-xs font-bold transition-all shadow-sm cursor-pointer flex items-center justify-center gap-2"
        >
          {mutation.isPending ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Processing Ticket...
            </>
          ) : (
            <>
              <PlusCircle className="h-4 w-4" />
              Submit Ticket
            </>
          )}
        </Button>
      </div>
    </form>
  );
}