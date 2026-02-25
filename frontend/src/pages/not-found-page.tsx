import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="max-w-2xl mx-auto p-6 text-center">
      <h1 className="text-4xl font-bold mb-4">404</h1>
      <p className="text-gray-600 mb-4">Page not found</p>
      <Link to="/" className="text-blue-600 underline hover:text-blue-800">
        Back to Home
      </Link>
    </div>
  );
}
