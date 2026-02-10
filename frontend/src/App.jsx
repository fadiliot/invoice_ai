import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./app/Layout";
import Dashboard from "./features/invoices/Dashboard";
import ReviewPage from "./features/invoices/ReviewPage";
import InvoiceDetail from "./features/invoices/InvoiceDetail";
import FailedPage from "./features/invoices/FailedPage";
import AllInvoicesPage from "./features/invoices/AllInvoicesPage";




export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/review" element={<ReviewPage />} />
        <Route path="/review/:id" element={<InvoiceDetail />} />
        <Route path="/failed" element={<FailedPage />} />
        <Route path="/invoices" element={<AllInvoicesPage />} />
      </Route>

      </Routes>
    </BrowserRouter>
  );
}
