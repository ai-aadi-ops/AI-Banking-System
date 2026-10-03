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

export const DEMO_ROBERT_USER = {
  id: 1,
  customer_id: 1,
  full_name: "Robert Wilson",
  email: "robert.wilson@demo.com",
  country: "United States",
  preferred_language: "en",
  currency_code: "USD",
  currency_symbol: "$",
  is_demo: true,
  has_transactions: true,
};

export const DEFAULT_AADITYA_USER = {
  id: 8,
  customer_id: 8,
  full_name: "Aaditya Acharya",
  email: "aadityaacharya2109@gmail.com",
  country: "India",
  preferred_language: "en",
  currency_code: "INR",
  currency_symbol: "₹",
  is_demo: false,
  has_transactions: true,
};

/**
 * Save user session without clobbering other slug profiles.
 */
export function saveUserSession(userObj) {
  if (!userObj) return;
  try {
    const slug = getUserSlug(userObj);
    localStorage.setItem("isLoggedIn", "true");
    localStorage.setItem("user", JSON.stringify(userObj));
    localStorage.setItem(`user_slug_${slug}`, JSON.stringify(userObj));
    if (userObj.preferred_language) {
      localStorage.setItem("preferred_language", userObj.preferred_language);
    }
  } catch (e) {
    console.warn("Failed to save user session:", e);
  }
}

/**
 * Resolve the initial user synchronously for a given URL slug.
 */
export function resolveInitialUserForSlug(userSlug) {
  const cleanSlug = (userSlug || "").replace(/[-_]dashboard$/i, "").toLowerCase();

  if (cleanSlug === "robert" || cleanSlug === "demo") {
    return DEMO_ROBERT_USER;
  }

  try {
    // 1. Check if this session explicitly set an active customer for this slug (e.g. just uploaded statement)
    const activeCid = sessionStorage.getItem(`active_customer_id_${cleanSlug}`);
    const slugStored = localStorage.getItem(`user_slug_${cleanSlug}`);
    if (slugStored) {
      const parsedSlugUser = JSON.parse(slugStored);
      if (activeCid && String(parsedSlugUser.customer_id || parsedSlugUser.id) === String(activeCid)) {
        return parsedSlugUser;
      }
      // For aaditya, avoid empty test accounts 6 and 7 unless explicitly active in this session
      if (cleanSlug === "aaditya" && (parsedSlugUser.customer_id === 6 || parsedSlugUser.customer_id === 7) && !activeCid) {
        return DEFAULT_AADITYA_USER;
      }
      if (parsedSlugUser.customer_id && parsedSlugUser.customer_id !== 1) {
        return parsedSlugUser;
      }
    }

    // 2. Check general stored user in localStorage
    const stored = localStorage.getItem("user");
    if (stored) {
      const parsed = JSON.parse(stored);
      const storedSlug = getUserSlug(parsed);
      if (!cleanSlug || storedSlug === cleanSlug) {
        if (cleanSlug === "aaditya" && (parsed.customer_id === 6 || parsed.customer_id === 7) && !activeCid) {
          return DEFAULT_AADITYA_USER;
        }
        if (cleanSlug !== "robert" && parsed.customer_id === 1) {
          // Don't use Robert Wilson's ID 1 for a non-robert slug
        } else {
          return parsed;
        }
      }
    }
  } catch (e) {
    console.warn("Error reading user from storage:", e);
  }

  if (cleanSlug === "aaditya") {
    return DEFAULT_AADITYA_USER;
  }

  return null;
}
