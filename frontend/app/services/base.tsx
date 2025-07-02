// Get the base URL from environment or use an empty string (for same-origin requests)
const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || '';

// If baseUrl is empty, we're running in production mode where frontend and backend are on the same domain
// Otherwise, we're in development mode and need to use the full URL
export const API_BASE_URL = baseUrl ? `${baseUrl.replace(/\/+$/, '')}/admin/` : '/admin/';