import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Loader2, CheckCircle2, AlertCircle } from "lucide-react";
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
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { createTicket } from "@/api/ticketApi";
import { validateTicket } from "@/lib/validateTicket";

const DEPARTMENTS = ["IT", "HR", "Finance", "Operations", "Engineering", "Other"];
const initialValues = { title: "", description: "", requesterEmail: "", department: "" };

export default function TicketForm() {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});

  const mutation = useMutation({
    mutationFn: createTicket,
    onSuccess: () => {
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
    <Card className="w-full max-w-xl">
      <CardHeader>
        <CardTitle>Submit New Ticket</CardTitle>
        <CardDescription>
          Describe your issue and our AI agent will classify and route it automatically.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="title">Ticket Title</Label>
            <Input
              id="title"
              placeholder="e.g. VPN Connection Failing on Corporate Network"
              value={values.title}
              onChange={(e) => handleChange("title", e.target.value)}
              aria-invalid={!!errors.title}
            />
            {errors.title && <p className="text-sm text-red-600">{errors.title}</p>}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              rows={4}
              placeholder="Include error messages, what you already tried, and when the issue started."
              value={values.description}
              onChange={(e) => handleChange("description", e.target.value)}
              aria-invalid={!!errors.description}
            />
            {errors.description && (
              <p className="text-sm text-red-600">{errors.description}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="requesterEmail">Requester Email</Label>
            <Input
              id="requesterEmail"
              type="email"
              placeholder="john.doe@company.com"
              value={values.requesterEmail}
              onChange={(e) => handleChange("requesterEmail", e.target.value)}
              aria-invalid={!!errors.requesterEmail}
            />
            {errors.requesterEmail && (
              <p className="text-sm text-red-600">{errors.requesterEmail}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="department">Department</Label>
            <Select
              value={values.department}
              onValueChange={(val) => handleChange("department", val)}
            >
              <SelectTrigger id="department" aria-invalid={!!errors.department}>
                <SelectValue placeholder="Select department" />
              </SelectTrigger>
              <SelectContent>
                {DEPARTMENTS.map((dept) => (
                  <SelectItem key={dept} value={dept}>
                    {dept}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.department && <p className="text-sm text-red-600">{errors.department}</p>}
          </div>

          {mutation.isError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Couldn't submit ticket</AlertTitle>
              <AlertDescription>
                {mutation.error?.response?.data?.message ||
                  "Something went wrong reaching the support API. Please try again."}
              </AlertDescription>
            </Alert>
          )}

          {mutation.isSuccess && (
            <Alert className="border-green-600 text-green-700">
              <CheckCircle2 className="h-4 w-4" />
              <AlertTitle>Ticket submitted</AlertTitle>
              <AlertDescription>
                Ticket #{mutation.data?.ticket_id} was created. You'll get an
                email update once it's classified.
              </AlertDescription>
            </Alert>
          )}

          <Button type="submit" className="w-full" disabled={mutation.isPending}>
            {mutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Submitting...
              </>
            ) : (
              "Submit Ticket TEST123"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}