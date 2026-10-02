/**
 * Utility to extract a clean, URL-safe user slug from a user object.
 * E.g., "Aaditya Acharya" -> "aaditya"
 * "Robert Wilson" -> "robert"
 * "John" -> "john"
 */
export function getUserSlug(user) {
  if (!user) return "user";

  const rawName = user.full_name || user.name || (user.email ? user.email.split("@")[0] : "") || "user";
  const firstName = rawName.trim().split(/\s+/)[0] || "user";
  
  // Clean special characters, convert to lowercase
  const slug = firstName.toLowerCase().replace(/[^a-z0-9_-]/g, "");
  return slug || "user";
}
