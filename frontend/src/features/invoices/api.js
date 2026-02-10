import api from "../../shared/api/axios";

// Fetch invoices with proper stage → status mapping
export const fetchInvoices = (query) =>
  api.get("/invoices", {
    params: {
      page: query.page,
      limit: query.limit,
      search: query.search,
      status: query.stage || "",   // map frontend stage to backend param
      sort: query.sort,
      order: query.order,
    },
  });

// Retry a failed invoice
export const retryInvoice = (id) =>
  api.post(`/invoice/${id}/retry`);

// Dashboard stats
export const fetchDashboardStats = () =>
  api.get("/dashboard-stats");

// Upload invoices
export const uploadInvoices = (files) => {
  const formData = new FormData();

  for (let file of files) {
    formData.append("files", file);
  }

  return api.post("/upload-invoices", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};
