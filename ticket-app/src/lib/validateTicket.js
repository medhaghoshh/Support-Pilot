const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Validates ticket form values.
 * @param {{ title: string, description: string, requesterEmail: string, department: string }} values
 * @returns {Record<string, string>} errors keyed by field name (empty object = valid)
 */
export function validateTicket(values) {
  const errors = {};

  if (!values.title.trim()) {
    errors.title = "Ticket title is required.";
  } else if (values.title.trim().length < 5) {
    errors.title = "Title must be at least 5 characters.";
  }

  if (!values.description.trim()) {
    errors.description = "Description is required.";
  } else if (values.description.trim().length < 20) {
    errors.description = "Please describe the issue in more detail (min 20 characters).";
  }

  if (!values.requesterEmail.trim()) {
    errors.requesterEmail = "Requester email is required.";
  } else if (!EMAIL_REGEX.test(values.requesterEmail.trim())) {
    errors.requesterEmail = "Enter a valid email address.";
  }

  if (!values.department) {
    errors.department = "Please select a department.";
  }

  return errors;
}
