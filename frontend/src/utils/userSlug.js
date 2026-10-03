/**
 * Utility to extract a clean, URL-safe user slug from a user object.
 * E.g., "Aaditya Acharya" -> "aaditya"
 * "Mr. Aaditya Acharya" -> "aaditya"
 * "Robert Wilson" -> "robert"
 */
export function getUserSlug(user) {
  if (!user) return "user";

  const rawName =
    user.registered_name ||
    user.full_name ||
    user.name ||
    (user.email ? user.email.split("@")[0] : "") ||
    "user";

  const withoutHonorific = rawName
    .trim()
    .replace(/^(?:mr|mrs|ms|dr|shri|smt)\.?\s+/i, "")
    .trim();

  const firstName = (withoutHonorific || rawName.trim()).split(/\s+/)[0] || "user";

  const slug = firstName.toLowerCase().replace(/[^a-z0-9_-]/g, "");
  return slug || "user";
}

export const DEMO_ROBERT_USER = {
  id: 1,
  customer_id: 1,
  full_name: "Robert Wilson",
  statement_holder_name: "Robert Wilson",
  email: "robert.wilson@demo.com",
  country: "United States",
  preferred_language: "en",
  currency_code: "USD",
  currency_symbol: "$",
  is_demo: true,
  has_transactions: true,
};

export const DEFAULT_AADITYA_USER = {
  id: 9,
  customer_id: 9,
  full_name: "Aaditya Acharya",
  statement_holder_name: "Aaditya Acharya",
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
    const activeCid = sessionStorage.getItem(`active_customer_id_${cleanSlug}`);

    // 1. Check general stored user in localStorage first (most recent login/register/upload)
    const stored = localStorage.getItem("user");
    if (stored) {
      const parsed = JSON.parse(stored);
      const storedSlug = getUserSlug(parsed);
      if ((!cleanSlug || storedSlug === cleanSlug) && Number(parsed.customer_id || parsed.id) !== 1) {
        if (cleanSlug === "aaditya" && Number(parsed.customer_id || parsed.id) === 8) {
          return { ...parsed, id: 9, customer_id: 9 };
        }
        return parsed;
      }
    }

    // 2. Check slug-specific storage
    const slugStored = localStorage.getItem(`user_slug_${cleanSlug}`);
    if (slugStored) {
      const parsedSlugUser = JSON.parse(slugStored);
      if (Number(parsedSlugUser.customer_id || parsedSlugUser.id) !== 1) {
        if (activeCid && String(parsedSlugUser.customer_id || parsedSlugUser.id) === String(activeCid)) {
          return parsedSlugUser;
        }
        if (cleanSlug === "aaditya" && Number(parsedSlugUser.customer_id || parsedSlugUser.id) === 8) {
          return { ...parsedSlugUser, id: 9, customer_id: 9 };
        }
        return parsedSlugUser;
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
